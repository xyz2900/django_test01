"""test01 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from accounts.views import LoginView, LogoutView, SignupView

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('accounts/', include('allauth.urls')),
    path('app00/', include('app00.urls')),
    path('app01/', include('app01.urls')),
    path('app02/', include('app02.urls')),
    path('app03/', include('app03.urls')),
    path('app04/', include('app04.urls')),
    path('app05/', include('app05.urls')),
    path('athena01/', include('athena01.urls')),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('signup', SignupView.as_view(), name='signup'),

    #path('accounts/login/', TemplateView.as_view(template_name = 'login.html'), name='login'),
    #path('accounts/logout/', TemplateView.as_view(template_name = 'logout.html'), name='logout'),
    #path('accounts/signup/', TemplateView.as_view(template_name = 'signup.html'), name='signup'),

    path('admin/', admin.site.urls),
]
