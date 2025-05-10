import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from news.models import Article, Company
from datetime import datetime
from django.conf import settings
from bs4 import BeautifulSoup

class Command(BaseCommand):
    help = 'Fetches and processes news articles'

    def handle(self, *args, **options):
        try:
            print("Fetching stock news...")
            url = 'https://finance.yahoo.com/news'
            
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            
            # Find news articles
            news_items = soup.find_all('h3')
            
            for item in news_items:
                try:
                    title = item.text.strip()
                    link = item.find('a')
                    if link and 'href' in link.attrs:
                        url = f'https://finance.yahoo.com{link["href"]}'
                    else:
                        url = ''
                        
                    articles.append({
                        'title': title,
                        'url': url,
                        'publishedAt': datetime.now().isoformat()
                    })
                except Exception as e:
                    print(f"Error processing news item: {str(e)}")
                    continue
            
            print(f"Found {len(articles)} articles")
            
            for article_data in articles:
                try:
                    if Article.objects.filter(url=article_data['url']).exists():
                        continue

                    article = Article.objects.create(
                        title=article_data['title'],
                        url=article_data['url'],
                        published_at=timezone.make_aware(
                            datetime.fromisoformat(article_data['publishedAt'])
                        )
                    )

                    print(f'Successfully processed article: {article.title}')

                except Exception as e:
                    print(f'Error saving article: {str(e)}')
                    continue

        except requests.exceptions.RequestException as e:
            print(f"Error fetching news: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
