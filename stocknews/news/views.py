from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from .models import Article, Company
from .serializers import ArticleSerializer, CompanySerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response

@login_required
def dashboard(request):
    latest_articles = Article.objects.order_by('-published_at')[:20]
    trending_companies = Company.objects.annotate(
        article_count=Count('articles', filter=Q(articles__published_at__gte=timezone.now() - timezone.timedelta(days=1)))
    ).order_by('-article_count')[:10]
    
    context = {
        'latest_articles': latest_articles,
        'trending_companies': trending_companies,
    }
    return render(request, 'news/dashboard.html', context)

@login_required
def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    return render(request, 'news/article_detail.html', {'article': article})

@login_required
def search(request):
    query = request.GET.get('q', '')
    articles = Article.objects.all()
    
    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(companies__name__icontains=query) |
            Q(companies__symbol__icontains=query)
        ).distinct()
    
    return render(request, 'news/search.html', {
        'articles': articles,
        'query': query
    })

@api_view(['GET'])
def api_articles(request):
    articles = Article.objects.all().order_by('-published_at')
    serializer = ArticleListSerializer(articles, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_trending_companies(request):
    trending_companies = Company.objects.annotate(
        article_count=Count('articles', filter=models.Q(articles__published_at__gte=timezone.now() - timezone.timedelta(days=1)))
    ).order_by('-article_count')[:10]
    serializer = CompanySerializer(trending_companies, many=True)
    return Response(serializer.data)
