"""
URL configuration for stocknews project.
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('get_stock_info/', views.get_stock_info, name='get_stock_info'),
]
