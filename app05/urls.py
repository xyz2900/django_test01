# myblog/accounts/urls.py

from django.urls import path

from . import views

app_name = 'app05'

urlpatterns = [
    path('daily', views.DailyAccessView.as_view(), name='daily'),
    path('hourly', views.HourlyAccessView.as_view(), name='hourly'),
    path('dw', views.DWAccessView.as_view(), name='dw'),
]