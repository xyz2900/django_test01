# myblog/accounts/urls.py

from django.urls import path

from . import views

app_name = 'app03'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
]