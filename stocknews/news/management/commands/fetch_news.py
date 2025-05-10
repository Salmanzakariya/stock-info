import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils import timezone
from news.models import Article
from datetime import datetime
import time

class Command(BaseCommand):
    help = 'Fetches and processes stock news'

    def handle(self, *args, **options):
        try:
            print("Fetching stock news...")
            
            # Use Yahoo Finance RSS feed
            url = 'https://feeds.finance.yahoo.com/rss/2.0/headline?s=marketnews&region=US&lang=en-US'
            
            max_retries = 3
            retry_delay = 5  # seconds
            
            for attempt in range(max_retries):
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    break
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:
                        print(f"Rate limited. Waiting {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        raise
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        raise
                    print(f"Request failed, retrying... ({attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2
            
            # Parse RSS feed
            soup = BeautifulSoup(response.text, 'xml')
            
            # Get news items
            items = soup.find_all('item')
            
            for item in items:
                try:
                    title = item.find('title').text.strip()
                    link = item.find('link').text.strip()
                    
                    # Get timestamp
                    timestamp = item.find('pubDate')
                    if timestamp:
                        published_at = datetime.strptime(timestamp.text, '%a, %d %b %Y %H:%M:%S %Z')
                    else:
                        published_at = datetime.now()
                        
                    # Check if article already exists
                    if Article.objects.filter(url=link).exists():
                        continue

                    # Create new article
                    article = Article.objects.create(
                        title=title,
                        url=link,
                        published_at=timezone.make_aware(published_at)
                    )

                    print(f'Successfully processed article: {article.title}')

                except Exception as e:
                    print(f"Error processing news item: {str(e)}")
            
            print(f"Successfully fetched {len(items)} news items")
            
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
