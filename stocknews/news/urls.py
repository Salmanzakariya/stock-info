from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('article/<int:pk>/', views.article_detail, name='article_detail'),
    path('search/', views.search, name='search'),
    
    # API endpoints
    path('api/articles/', views.api_articles, name='api_articles'),
    path('api/trending/', views.api_trending_companies, name='api_trending'),
]
