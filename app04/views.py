from django.shortcuts import render, HttpResponse
from django.views.generic import TemplateView, DetailView
from django_pandas.io import read_frame
import seaborn as sns
from sklearn.linear_model import LinearRegression
import io
import matplotlib.pyplot as plt
import numpy as np
from .models import DatForex

class IndexView(TemplateView):
   template_name = 'app04/index.html'

   def get(self, request, **kwargs):
      context = {
         'items': 'TEST'
      }
      return self.render_to_response(context)

class Test01(TemplateView):
   template_name = 'app04/test01.html'


# グラフ作成
def setPlt(pk):
   # 折れ線グラフを出力
   # TODO: 本当はpkを基にしてモデルからデータを取得する。
   x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
   y = np.array([20, 90, 50, 30, 100, 80, 10, 60, 40, 70])
   plt.plot(x, y)


# svgへの変換
def pltToSvg():
   buf = io.BytesIO()
   plt.savefig(buf, format='svg', bbox_inches='tight')
   s = buf.getvalue()
   buf.close()
   return s

def get_svg(request, pk):
   setPlt(pk)  # create the plot
   svg = pltToSvg()  # convert plot to SVG
   plt.cla()  # clean up plt so it can be re-used
   response = HttpResponse(svg, content_type='image/svg+xml')
   return response

def plot2(request, kind, no, period):
   _data = DatForex.objects.filter(no=no).all()
   df = read_frame(_data, fieldnames=['dtime', 'open', 'high', 'low', 'close'])
   df = df.set_index('dtime')

   # リサンプリング
   conversion = {'open': 'first',
                 'high': 'max',
                 'low': 'min',
                 'close': 'last'}

   df = df.resample('%dMin' % (period)).agg(conversion).copy()

   if kind == 1:
      df['close'].plot()

   elif kind == 2:
      #_dohlc = np.log(df.diff().dropna())
      sns.pairplot(df)

   elif kind == 3:
      df['oc'] = df['close'] - df['open']
      df['next_oc'] = df['oc'].shift(-1)
      sns.regplot(x="oc", y="next_oc", data=df)

   elif kind == 4:
      df['oc'] = df['close'] - df['open']
      df['next_oc'] = df['oc'].shift(-1)
      df2 = df[['oc', 'next_oc']]
      df2 = df2.dropna(how='any', axis=0) # 欠損値が一つでも含まれる行・列を削除する

      lr = LinearRegression()

      X = df2[['oc']].values
      #X2 = [[x] for x in X]
      Y = df2['next_oc'].values

      lr.fit(X, Y)  # 線形モデルの重みを学習
      print('coefficient = ', lr.coef_[0])  # 説明変数の係数を出力
      print('intercept = ', lr.intercept_)  # 切片を出力

      plt.scatter(X, Y, color='blue')  # 説明変数と目的変数のデータ点の散布図をプロット
      plt.plot(X, lr.predict(X), color='red')  # 回帰直線をプロット

      plt.title('coefficient=%5.4f intercept=%5.4f' % (lr.coef_[0], lr.intercept_))  # 図のタイトル

   svg = pltToSvg()  # convert plot to SVG
   plt.cla()  # clean up plt so it can be re-used
   response = HttpResponse(svg, content_type='image/svg+xml')
   return response

