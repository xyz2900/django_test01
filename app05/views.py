from django.shortcuts import render, HttpResponse
from django.views.generic import TemplateView, DetailView
from django.conf import settings
import datetime as dt
import pandas as pd
import awswrangler as wr
import boto3
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.offline import plot

# nginxのアクセス数を表示
# 不要なデータを除く
def nginx_access_filter(df):
   df = df[df['url'] != '/']
   df = df[~df['url'].str.contains('/wp')]
   df = df[~df['url'].str.contains('xmlrpc')]
   df = df[~df['url'].str.contains('favicon.ico')]
   df = df[~df['url'].str.contains('robots.txt')]
   df = df[~df['url'].str.contains('/apple')]
   df = df[~df['url'].str.contains('/sitemap')]
   df = df[~df['url'].str.contains('/feed')]

   return df

# 日別アクセス数
class DailyAccessView(TemplateView):
   template_name = 'app05/daily.html'

   def __init__(self):
      super().__init__()
      self.session = boto3.Session(aws_access_key_id=settings.AWS_ACCESS_KEY, aws_secret_access_key=settings.AWS_SECRET_KEY, region_name=settings.AWS_REZGION)

   # アクセス数(GET, PUT)（折れ線グラフ)
   def get_access_plot(self, today):

      # nginxのアクセス数
      sql = f"SELECT date_format (time, '%Y-%m-%d') as date, request_method, count(*) as count FROM log_k245 WHERE time < CAST('{today}' as timestamp) group by date_format (time, '%Y-%m-%d'), request_method order by date_format (time, '%Y-%m-%d'), request_method".format(today=today.strftime("%Y-%m-%d"))
      df_nginx = wr.athena.read_sql_query(sql, database='default', boto3_session=self.session)
      df_nginx['date'] = pd.to_datetime(df_nginx['date'])
      df_get = df_nginx[(df_nginx['request_method'] == 'GET')]
      df_post = df_nginx[(df_nginx['request_method'] == 'POST')]

      # GAのPV数
      sql = f"SELECT date, count(*) as count FROM ga_pv WHERE dt < CAST('{today}' as timestamp) group by date order by date".format(today=today.strftime("%Y-%m-%d"))
      df_ga_pv = wr.athena.read_sql_query(sql, database='default', boto3_session=self.session)
      df_ga_pv = df_ga_pv[df_ga_pv['date'] != 'date']
      df_ga_pv['date'] = pd.to_datetime(df_ga_pv['date'], format='%Y%m%d')

      #fig = go.Figure()
      fig = make_subplots(specs=[[{"secondary_y": True}]])
      fig.add_trace(go.Bar(x=df_ga_pv["date"], y=df_ga_pv["count"], name='PV', marker_color='rgba(0, 255, 0, 0.5)'), secondary_y=True)
      fig.add_trace(go.Scatter(x=df_get["date"], y=df_get["count"], name='GET', line=dict(color='red', width=2)))
      fig.add_trace(go.Scatter(x=df_post["date"], y=df_post["count"], name='POST', line=dict(color='blue', width=2)))

      fig.update_layout(width=500,
                        height=500,
                        title='日別アクセス件数',
                        legend={"x": 0.8, "y": 1.3},
                        xaxis_tickformat = '%Y-%m-%d',
                        xaxis_tickangle=-45,
                        xaxis_title='Date',
                        yaxis_title='Count')

      '''
      data = [
         go.Scatter(x=df["date"], y=df["count"], name="Birth Rate")
      ]
      layout = go.Layout(
         width=500,
         height=500,
         title="Births and Birth Rate in Japan",
         legend={"x": 0.8, "y": 0.1},
         xaxis={"title": "Year"},
         yaxis={"title": "Births"},
      )
      fig = go.Figure(data=data, layout=layout)
      '''

      '''
      fig = px.line(df, x='date', y='count', color='request_method', title='日別アクセス件数', width=500, height=500)
      fig.layout.xaxis.tickformat = '%Y-%m-%d'
      '''

      '''
      fig.update_layout(
         autosize=False,
         width=500,
         height=500,
      )
      '''
      plot_fig = plot(fig, output_type='div', include_plotlyjs=False)

      return plot_fig

   # user agent別の数（円グラフ)
   def get_agent_plot(self, today):
      sql = f"SELECT agent, count(*) as count FROM log_k245 WHERE time < CAST('{today}' as timestamp) group by agent order by count desc".format(today=today.strftime("%Y-%m-%d"))
      df = wr.athena.read_sql_query(sql, database='default', boto3_session=self.session)
      df['agent_s'] = df['agent'].str.split(pat=' ', expand=True)[0] # user agent文字列をスペースで区切った最初の文字
      df['agent_s'] = df['agent_s'].str.split(pat='/', expand=True)[0]

      df2 = df[['agent_s', 'count']].groupby('agent_s').sum().reset_index()
      df2 = df2.sort_values(by=["count"], ascending=False)
      df2 = df2[df2['count'] > 1]
      #print(df2)

      #df2 = df2[:5]
      fig = px.pie(df2, values='count', names='agent_s', title='ユーザーエージェント別件数', width=400, height=400)
      for ser in fig['data']:
         #ser['text'] = list(set([d.strftime('%Y-%m-%d') for d in df['dates']]))
         ser['hovertemplate'] = '%{label}<br>count=%{value}<extra></extra>'

      plot_fig = plot(fig, output_type='div', include_plotlyjs=False)
      return plot_fig

   # url別の数（円グラフ)
   def get_url_plot(self, today):
      sql = f"SELECT request_url, count(*) as count FROM log_k245 WHERE time < CAST('{today}' as timestamp) group by request_url order by count desc".format(today=today.strftime("%Y-%m-%d"))
      df = wr.athena.read_sql_query(sql, database='default', boto3_session=self.session)
      df['url'] = df['request_url'].str.split(pat='?', expand=True)[0]  # user agent文字列をスペースで区切った最初の文字
      #df['url'] = df['url'].str.split(pat='%', expand=True)[0]
      df = df[df['url'] != '/']
      df = df[~df['url'].str.contains('/wp')]
      df = df[~df['url'].str.contains('xmlrpc')]
      df = df[~df['url'].str.contains('favicon.ico')]
      df = df[~df['url'].str.contains('robots.txt')]
      df = df[~df['url'].str.contains('/apple')]
      df = df[~df['url'].str.contains('/sitemap')]
      df = df[~df['url'].str.contains('/feed')]

      df2 = df[['url', 'count']].groupby('url').sum().reset_index()
      df2 = df2.sort_values(by=["count"], ascending=False)
      df2 = df2[df2['count'] > 1]
      # print(df2)

      df2 = df2[:20]

      fig = px.pie(df2, values='count', names='url', title='URL別件数', width=700, height=400)
      for ser in fig['data']:
         # ser['text'] = list(set([d.strftime('%Y-%m-%d') for d in df['dates']]))
         ser['hovertemplate'] = '%{label}<br>count=%{value}<extra></extra>'


      '''
      fig = go.Figure()
      fig.add_trace(go.Pie(labels=df2["url"], values=df2["count"]))
      '''

      fig.update_layout(legend={"x": 1.8, "y": 1.3})

      plot_fig = plot(fig, output_type='div', include_plotlyjs=False)
      return plot_fig

   def get(self, request, **kwargs):
      today = dt.date.today()

      plot_access = self.get_access_plot(today)
      plot_agent  = self.get_agent_plot(today)
      plot_url    = self.get_url_plot(today)

      context = {
         'plot_access': plot_access,
         'plot_agent': plot_agent,
         'plot_url': plot_url
      }
      return self.render_to_response(context)


# 時間別アクセス数
class HourlyAccessView(TemplateView):
   template_name = 'app05/hourly.html'

   def __init__(self):
      super().__init__()
      self.session = boto3.Session(aws_access_key_id=settings.AWS_ACCESS_KEY, aws_secret_access_key=settings.AWS_SECRET_KEY, region_name=settings.AWS_REZGION)

   # アクセス数(GET, PUT)（折れ線グラフ)
   def get_access_plot(self, today):
      # nginxのアクセス数
      sql = f"SELECT hour(time) as hour, request_method, count(*) as count FROM log_k245 WHERE time < CAST('{today}' as timestamp) group by hour(time), request_method order by hour(time), request_method".format(today=today.strftime("%Y-%m-%d"))
      df_nginx = wr.athena.read_sql_query(sql, database='default', boto3_session=self.session)
      #df_nginx = nginx_access_filter(df_nginx)

      df_get = df_nginx[(df_nginx['request_method'] == 'GET')]
      df_post = df_nginx[(df_nginx['request_method'] == 'POST')]

      fig = go.Figure()
      fig.add_trace(go.Bar(x=df_get["hour"], y=df_get["count"], name='GET', marker_color='rgba(255, 0, 0, 0.5)'))
      fig.add_trace(go.Bar(x=df_post["hour"], y=df_post["count"], name='POST', marker_color='rgba(0, 0, 255, 0.5)'))

      fig.update_layout(width=500,
                        height=500,
                        title='時間アクセス件数',
                        legend={"x": 0.8, "y": 1.3},
                        xaxis_title='Hour',
                        yaxis_title='Count')

      plot_fig = plot(fig, output_type='div', include_plotlyjs=False)
      return plot_fig

   def get(self, request, **kwargs):
      today = dt.date.today()

      plot_access = self.get_access_plot(today)

      context = {
         'plot_access': plot_access,
      }
      return self.render_to_response(context)

# 曜日別アクセス数
class DWAccessView(TemplateView):
   template_name = 'app05/dw.html'

   def __init__(self):
      super().__init__()
      self.session = boto3.Session(aws_access_key_id=settings.AWS_ACCESS_KEY, aws_secret_access_key=settings.AWS_SECRET_KEY, region_name=settings.AWS_REZGION)

   # アクセス数(GET, PUT)（折れ線グラフ)
   def get_access_plot(self, today):
      # nginxのアクセス数
      sql = f"SELECT day_of_week(time) as dw, request_method, count(*) as count FROM log_k245 WHERE time < CAST('{today}' as timestamp) group by day_of_week(time), request_method order by day_of_week(time), request_method".format(today=today.strftime("%Y-%m-%d"))
      df_nginx = wr.athena.read_sql_query(sql, database='default', boto3_session=self.session)

      # 1:Mon 2:Tue 3:Wed 4:Thu 5:Fri 6:Sat 7:Sun
      df_nginx = df_nginx.sort_values(by=["dw"], ascending=True)
      df_nginx.loc[df_nginx['dw'] == 1, 'week'] = 'Mon'
      df_nginx.loc[df_nginx['dw'] == 2, 'week'] = 'Tue'
      df_nginx.loc[df_nginx['dw'] == 3, 'week'] = 'Wed'
      df_nginx.loc[df_nginx['dw'] == 4, 'week'] = 'Thu'
      df_nginx.loc[df_nginx['dw'] == 5, 'week'] = 'Fri'
      df_nginx.loc[df_nginx['dw'] == 6, 'week'] = 'Sat'
      df_nginx.loc[df_nginx['dw'] == 7, 'week'] = 'Sun'

      df_get = df_nginx[(df_nginx['request_method'] == 'GET')]
      df_post = df_nginx[(df_nginx['request_method'] == 'POST')]

      fig = go.Figure()
      fig.add_trace(go.Bar(x=df_get["week"], y=df_get["count"], name='GET', marker_color='rgba(255, 0, 0, 0.5)'))
      fig.add_trace(go.Bar(x=df_post["week"], y=df_post["count"], name='POST', marker_color='rgba(0, 0, 255, 0.5)'))

      fig.update_layout(width=500,
                        height=500,
                        title='曜日別アクセス件数',
                        legend={"x": 0.8, "y": 1.3},
                        xaxis_title='Hour',
                        yaxis_title='Count')

      plot_fig = plot(fig, output_type='div', include_plotlyjs=False)
      return plot_fig

   def get(self, request, **kwargs):
      today = dt.date.today()

      plot_access = self.get_access_plot(today)

      context = {
         'plot_access': plot_access,
      }
      return self.render_to_response(context)

