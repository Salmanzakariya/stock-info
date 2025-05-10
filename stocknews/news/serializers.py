from rest_framework import serializers
from .models import Article, Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'symbol', 'name', 'sector', 'description']

class ArticleSerializer(serializers.ModelSerializer):
    companies = CompanySerializer(many=True, read_only=True)
    
    class Meta:
        model = Article
        fields = ['id', 'title', 'source', 'url', 'content', 'summary', 
                 'sentiment', 'published_at', 'companies']

class ArticleListSerializer(serializers.ModelSerializer):
    companies = CompanySerializer(many=True, read_only=True)
    
    class Meta:
        model = Article
        fields = ['id', 'title', 'source', 'url', 'summary', 
                 'sentiment', 'published_at', 'companies']
