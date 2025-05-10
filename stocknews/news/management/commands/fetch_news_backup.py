import json
from django.core.management.base import BaseCommand
from django.utils import timezone
from news.models import Article, Company
from datetime import datetime
from django.conf import settings
from googlefinance import getQuotes

class Command(BaseCommand):
    help = 'Fetches and processes stock news using Google Finance'

    def handle(self, *args, **options):
        try:
            print("Fetching stock news using Google Finance API...")
            
            # Get stock quotes (this will also include news)
            stocks = ['AAPL', 'GOOGL', 'MSFT']  # Example stocks
            quotes = getQuotes(stocks)
            
            articles = []
            
            # Process each stock's news
            for quote in quotes:
                try:
                    # Extract news from the quote
                    news = quote.get('News', [])
                    for news_item in news:
                        try:
                            title = news_item.get('title', '')
                            url = news_item.get('url', '')
                            source = news_item.get('source', 'Google Finance')
                            
                            if title and url:
                                articles.append({
                                    'title': title,
                                    'url': url,
                                    'source': source,
                                    'publishedAt': datetime.now().isoformat()
                                })
                        except Exception as e:
                            print(f"Error processing news item: {str(e)}")
                            continue
                except Exception as e:
                    print(f"Error processing stock news: {str(e)}")
                    continue
            
            print(f"Found {len(articles)} articles")
            
            # Save articles to database
            for article_data in articles:
                try:
                    if Article.objects.filter(url=article_data['url']).exists():
                        continue

                    article = Article.objects.create(
                        title=article_data['title'],
                        source=article_data['source'],
                        url=article_data['url'],
                        published_at=timezone.make_aware(
                            datetime.fromisoformat(article_data['publishedAt'])
                        )
                    )

                    print(f'Successfully processed article: {article.title}')

                except Exception as e:
                    print(f'Error saving article: {str(e)}')
                    continue

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
                return

            # Process articles
            for article_data in articles:
                try:
                    # Skip if article already exists
                    if Article.objects.filter(url=article_data['url']).exists():
                        continue

                    # Extract company symbols from content and title
                    content = (article_data.get('content', '') or 
                              article_data.get('description', '') or 
                              article_data.get('title', ''))
                    companies = self.extract_companies(content)

                    # Create article
                    article = Article.objects.create(
                        title=article_data['title'],
                        source=article_data['source'],
                        url=article_data['url'],
                        content=article_data.get('content', ''),
                        summary=article_data.get('description', ''),
                        sentiment=self.get_ai_sentiment(content),
                        published_at=timezone.make_aware(
                            datetime.fromisoformat(article_data['publishedAt'].replace('Z', '+00:00'))
                        )
                    )

                    # Link companies
                    for company_data in companies:
                        company, created = Company.objects.get_or_create(
                            symbol=company_data['symbol'],
                            defaults={
                                'name': company_data['name'],
                                'sector': company_data['sector']
                            }
                        )
                        article.companies.add(company)

                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully processed article: {article.title}')
                    )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing article: {str(e)}')
                    )
                    continue

            if articles['status'] != 'ok':
                self.stdout.write(
                    self.style.ERROR(f"Error fetching news: {articles.get('message', 'Unknown error')}")
                )
                return

            print(f"Found {len(articles['articles'])} articles")

            for article_data in articles['articles']:
                try:
                    # Skip if article already exists
                    if Article.objects.filter(url=article_data['url']).exists():
                        continue

                    # Extract company symbols from content and title
                    content = (article_data.get('content', '') or 
                              article_data.get('description', '') or 
                              article_data.get('title', ''))
                    companies = self.extract_companies(content)

                    # Create article
                    article = Article.objects.create(
                        title=article_data['title'],
                        source=article_data['source']['name'],
                        url=article_data['url'],
                        content=article_data.get('content', ''),
                        summary=article_data.get('description', ''),
                        sentiment=self.get_ai_sentiment(content),
                        published_at=timezone.make_aware(
                            datetime.fromisoformat(article_data['publishedAt'].replace('Z', '+00:00'))
                        )
                    )

                    # Link companies
                    for company_data in companies:
                        company, created = Company.objects.get_or_create(
                            symbol=company_data['symbol'],
                            defaults={
                                'name': company_data['name'],
                                'sector': company_data['sector']
                            }
                        )
                        article.companies.add(company)

                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully processed article: {article.title}')
                    )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing article: {str(e)}')
                    )
                    continue

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error in fetch_news command: {str(e)}')
            )
            raise

        if articles['status'] != 'ok':
            print(f"Error fetching news: {articles.get('message', 'Unknown error')}")
            return

        print(f"Found {len(articles['articles'])} articles")

        for article_data in articles['articles']:
            # Skip if article already exists
            if Article.objects.filter(url=article_data['url']).exists():
                continue

            # Extract company symbols from content and title
            content = (article_data.get('content', '') or 
                      article_data.get('description', '') or 
                      article_data.get('title', ''))
            companies = self.extract_companies(content)

            # Create article
            article = Article.objects.create(
                title=article_data['title'],
                source=article_data['source']['name'],
                url=article_data['url'],
                content=article_data.get('content', ''),
                summary=article_data.get('description', ''),
                sentiment=self.get_ai_sentiment(content),
                published_at=timezone.make_aware(
                    datetime.fromisoformat(article_data['publishedAt'].replace('Z', '+00:00'))
                )
            )

            # Link companies
            for company_data in companies:
                company, created = Company.objects.get_or_create(
                    symbol=company_data['symbol'],
                    defaults={
                        'name': company_data['name'],
                        'sector': company_data['sector']
                    }
                )
                article.companies.add(company)

            self.stdout.write(
                self.style.SUCCESS(f'Successfully processed article: {article.title}')
            )

    def extract_companies(self, content):
        """Extract company symbols from article content using simple pattern matching"""
        # This is a basic implementation - you might want to enhance it with NLP
        companies = []
        # Add more company patterns as needed
        patterns = {
            'INFY': {'name': 'Infosys', 'sector': 'IT'},
            'RELIANCE': {'name': 'Reliance Industries', 'sector': 'Energy'},
            'TCS': {'name': 'Tata Consultancy Services', 'sector': 'IT'},
            'HDFCBANK': {'name': 'HDFC Bank', 'sector': 'Banking'},
            'ICICIBANK': {'name': 'ICICI Bank', 'sector': 'Banking'}
        }
        
        for symbol, company_data in patterns.items():
            if symbol in content.upper():
                companies.append(company_data)
        
        return companies

    def get_ai_sentiment(self, content):
        """Simple sentiment analysis - you can enhance this with DeepSeek API"""
        # This is a basic implementation - you might want to enhance it
        content = content.lower()
        
        positive_words = ['gains', 'rises', 'up', 'positive', 'bullish']
        negative_words = ['falls', 'drops', 'down', 'negative', 'bearish']
        
        positive_count = sum(word in content for word in positive_words)
        negative_count = sum(word in content for word in negative_words)
        
        if positive_count > negative_count:
            return 'POSITIVE'
        elif negative_count > positive_count:
            return 'NEGATIVE'
        else:
            return 'NEUTRAL'
