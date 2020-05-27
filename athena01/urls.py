# myblog/accounts/urls.py

from django.urls import path

from . import views

app_name = 'athena01'

urlpatterns = [
    path('', views.test00, name='test00'),
    path('test01', views.Test01.as_view(), name='test01'),
    path('test02', views.Test02.as_view(), name='test02'),
]