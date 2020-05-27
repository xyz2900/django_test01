# myblog/accounts/urls.py

from django.urls import path

from . import views

app_name = 'app04'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('test01', views.Test01.as_view(), name='test01'),
    path('plot/<int:pk>/', views.get_svg, name='plot'),
    path('plot2/<int:kind>/<str:no>/<int:period>/', views.plot2, name='plot2'),
]