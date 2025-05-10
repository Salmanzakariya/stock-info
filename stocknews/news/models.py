from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Company(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    sector = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"

class Article(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    source = models.CharField(max_length=100, db_index=True)
    url = models.URLField(unique=True)
    content = models.TextField()
    summary = models.TextField(blank=True)
    sentiment = models.CharField(max_length=20, choices=[
        ('POSITIVE', 'Positive'),
        ('NEUTRAL', 'Neutral'),
        ('NEGATIVE', 'Negative')
    ])
    published_at = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    companies = models.ManyToManyField(Company, related_name='articles')
    
    class Meta:
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['content']),
            models.Index(fields=['published_at']),
        ]
    
    @classmethod
    def search(cls, query):
        return cls.objects.filter(
            models.Q(title__icontains=query) |
            models.Q(companies__name__icontains=query) |
            models.Q(companies__symbol__icontains=query)
        ).distinct()
    
    def __str__(self):
        return self.title

    @classmethod
    def todays_news(cls):
        """Return articles published today"""
        today = timezone.now().date()
        return cls.objects.filter(
            published_at__date=today
        ).order_by('-published_at')

class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_sectors = models.CharField(max_length=255, blank=True)
    preferred_companies = models.CharField(max_length=255, blank=True)
    daily_digest_enabled = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Preferences for {self.user.username}"
