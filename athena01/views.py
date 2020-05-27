from django.shortcuts import render, HttpResponse
from django.views.generic import TemplateView, DetailView
import io
import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np
import PIL
import base64
import awswrangler as wr
import plotly.figure_factory as ff
import plotly.graph_objects as go
from plotly.offline import plot


class Test01(TemplateView):
   template_name = 'athena01/test01.html'

   def create_graphic(self):
      df = wr.athena.read_sql_query('SELECT * FROM dat_forex order by dtime LIMIT 10000', database='default')

      df = df.set_index('dtime')
      conversion = {'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last',
                    'volume': 'sum'}

      df = df.resample('60Min').agg(conversion).copy()
      # 欠損値が一つでも含まれる行・列を削除する
      df = df.dropna(how='any', axis=0)

      df = df.rename(columns={'open':'Open', 'high':'High', 'low':'Low', 'close':'Close', 'volume':'Volume'})

      fig, ax = plt.subplots()
      width = 0.8
      buffer = io.BytesIO()

      # ローソク足
      mpf.plot(df, type='candle', volume=True, mav=(5,25,75), figratio=(15,10), figscale=1.0, title='USD_JPY', style='yahoo', savefig=dict(fname=buffer,dpi=100,pad_inches=0.55))
      buffer.seek(0)

      # PNG変換　base64
      '''
      canvas = fig.canvas
      buf, size = canvas.print_to_buffer()
      image = PIL.Image.frombuffer('RGBA', size, buf, 'raw', 'RGBA', 0, 1)
      buffer = io.BytesIO()
      image.save(buffer, 'PNG')
      graphic = buffer.getvalue()
      graphic = base64.b64encode(graphic).decode('ascii')
      buffer.close()
      '''

      graphic = buffer.getvalue()
      graphic = base64.b64encode(graphic).decode('ascii')
      buffer.close()
      return graphic

   def get(self, request, **kwargs):
      graphic = self.create_graphic()

      context = {
         'chart01': graphic
      }
      return self.render_to_response(context)

class Test02(TemplateView):
   template_name = 'athena01/test02.html'

   def get(self, request, **kwargs):
      df = wr.athena.read_sql_query('SELECT * FROM dat_forex order by dtime LIMIT 10000', database='default')

      df = df.set_index('dtime')
      conversion = {'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last',
                    'volume': 'sum'}

      df = df.resample('60Min').agg(conversion).copy()
      # 欠損値が一つでも含まれる行・列を削除する
      df = df.dropna(how='any', axis=0)

      '''
      fig = ff.create_candlestick(df.open, df.high, df.low, df.close, dates=df.index)
      xtick0 = (5 - df.index[0].weekday()) % 5  # 最初の月曜日のインデックス
      fig['layout'].update({
         'xaxis': {
            'showgrid': True,
            'ticktext': [x.strftime('%Y-%m-%d') for x in df.index][xtick0::5],
            'tickvals': np.arange(xtick0, len(df), 5)
         }
      })
      '''

      fig = go.Figure(data=[go.Candlestick(x=df.index,
                                           open=df['open'],
                                           high=df['high'],
                                           low=df['low'],
                                           close=df['close'])])

      plot_fig = plot(fig, output_type='div', include_plotlyjs=False)

      context = {
         'plot_data': plot_fig
      }
      return self.render_to_response(context)


def test00(request):
   x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
   y = np.array([20, 90, 50, 30, 100, 80, 10, 60, 40, 70])
   plt.plot(x, y)

   svg = pltToSvg()  # convert plot to SVG
   plt.cla()  # clean up plt so it can be re-used
   response = HttpResponse(svg, content_type='image/svg+xml')
   return response

# svgへの変換
def pltToSvg():
   buf = io.BytesIO()
   plt.savefig(buf, format='svg', bbox_inches='tight')
   s = buf.getvalue()
   buf.close()
   return s