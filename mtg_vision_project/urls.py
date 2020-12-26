"""mtg_vision_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView

from mtg_vision_project import views, serializers

urlpatterns = [
    path('', views.index, name='index'),
    path('', include('password_reset.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', views.signup, name='signup'),
    path('home/', views.info, name='home'),
    path('info/', views.info, name='info'),
    path('admin/', admin.site.urls),
    path('drag_n_drop', TemplateView.as_view(template_name='drag_and_drop.html'),
         name='drag_n_drop'),
    path('drag_n_drop/upload', serializers.upload_api_view, name='upload_image'),
    path('ebay_auth_code/', views.ebay_auth_code, name='ebay_auth_code'),
    path('ebay_sign_in/', views.ebay_sign_in, name='ebay_sign_in'),
]
