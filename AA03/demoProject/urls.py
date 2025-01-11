"""demoProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from demoApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('homepage', views.homepage, name='homepage'),
    path('credits', views.credits, name='credits'),
    path('results', views.results, name='results'),
    path('airport', views.airport, name='airport'),
    path('traffic', views.traffic, name='traffic'),
    path('get_closest_cam', views.get_closest_camera, name='get_closest_cam'),
    path('weather', views.weather, name='weather'),
    path('results2', views.results2, name='results2'),
    path('', include('demoApp.urls')),
    re_path('', include('pwa.urls')),
    path('get_location_id/', views.get_location_id, name='get_location_id'),
    path('test_get_location_id/', views.test_get_location_id, name='test_get_location_id'),
    path('test_get_hotels/', views.test_get_hotels, name='test_get_hotels'),
    path('test_get_attractions/', views.test_get_attractions, name='test_get_attractions'),
    path('test_get_restaurants/', views.test_get_restaurants, name='test_get_restaurants'),
    path('get_hotels/', views.get_hotels, name='get_hotels'),
    path('get_attractions/', views.get_attractions, name='get_attractions'),
    path('get_restaurants/', views.get_restaurants, name='get_restaurants'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
