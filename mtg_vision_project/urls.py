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
from . import settings
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

import mtg_vision_project.views
from mtg_vision_project import views, serializers
from image_matcher.views import new_listing
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('', views.index, name='index'),
    path('', include('password_reset.urls')),
    path('', include('image_matcher.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', views.signup, name='signup'),
    path('home/', views.info, name='home'),
    path('info/', views.info, name='info'),
    path('admin/', admin.site.urls),
    path('drag_n_drop', TemplateView.as_view(template_name='drag_and_drop.html'),
         name='drag_n_drop'),
    path('drag_n_drop/upload', views.upload_api_view, name='upload_image'),
    path('drag_n_drop/confirm_selected',
         views.upload_selected_images_to_ebay_view, name='confirm_selected'),

    path('listing_redirect/', views.create_listing_redirect_view,
         name='listing-redirect'),

    path('new_listing/<pk>', views.create_listing_view, name='listing-detail'),

    path('ebay_settings/', views.ebay_settings_view, name='ebay_settings'),
    path('sell_settings/', views.sell_settings_view, name='sell_settings'),

    path('ebay_auth_code/', views.ebay_auth_code, name='ebay_auth_code'),
    path('ebay_sign_in/', views.ebay_sign_in, name='ebay_sign_in'),
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
