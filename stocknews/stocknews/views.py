from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Set the backend to Agg
import matplotlib.pyplot as plt
import io
import base64
import logging
import urllib.parse
import os
import wikipedia

# Set up logging
logger = logging.getLogger(__name__)

# News API Key
NEWS_API_KEY = 'f101063abfc44c73917f5f5856d33dbd'  # Updated News API key

def generate_price_graph(hist):
    try:
        plt.figure(figsize=(10, 6))
        
        # Calculate price differences
        hist['Price_Diff'] = hist['Close'].diff()
        
        # Plot price differences
        plt.plot(hist.index, hist['Price_Diff'], marker='o', linestyle='-', color='blue', linewidth=2)
        
        # Add zero line
        plt.axhline(y=0, color='r', linestyle='--', alpha=0.3)
        
        # Style the plot
        plt.title('Daily Price Differences', fontsize=14, pad=15)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Price Difference ($)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Save plot to a bytes buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        plt.close()
        
        # Convert to base64 string
        image_png = buffer.getvalue()
        buffer.close()
        graph = base64.b64encode(image_png).decode('utf-8')
        
        return graph
    except Exception as e:
        logger.error(f"Error generating price graph: {str(e)}")
        return None

def get_stock_info(request):
    try:
        # Get stock symbol, exchange and period from request parameters
        symbol = request.GET.get('symbol', '').strip().upper()
        exchange = request.GET.get('exchange', 'NSE')
        period = request.GET.get('period', '15')

        if not symbol:
            return JsonResponse({
                'status': 'error',
                'message': 'Please enter a stock symbol'
            }, status=400)

        # Format symbol based on exchange
        if exchange == 'NSE':
            yahoo_symbol = f"{symbol}.NS"
        elif exchange == 'BSE':
            yahoo_symbol = f"{symbol}.BO"
        elif exchange == 'NYSE':
            yahoo_symbol = symbol
        else:  # NASDAQ
            yahoo_symbol = symbol

        try:
            # Get stock data using yfinance
            stock = yf.Ticker(yahoo_symbol)
            
            # Get historical data based on selected period
            end_date = datetime.now()
            start_date = end_date - timedelta(days=int(period))
            
            hist = stock.history(start=start_date, end=end_date, interval='1d')
            
            if hist.empty:
                return JsonResponse({
                    'status': 'error',
                    'message': f'No data found for {symbol} on {exchange}. Please check if the symbol is correct.'
                }, status=404)

            # Generate price difference graph
            price_graph = generate_price_graph(hist)

            # Get current stock info
            info = stock.info
            
            if not info:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Could not fetch information for {symbol} on {exchange}. Please try again later.'
                }, status=404)

            current_price = info.get('currentPrice', 0)
            company_name = info.get('longName', symbol)
            market_cap = info.get('marketCap', 0)
            previous_close = info.get('previousClose', 0)
            
            # Calculate price change
            price_change = current_price - previous_close
            price_change_percent = (price_change / previous_close) * 100 if previous_close else 0

            # Format historical data
            price_history = []
            for index, row in hist.iterrows():
                price_history.append({
                    'date': index.strftime('%Y-%m-%d'),
                    'open': round(row['Open'], 2),
                    'high': round(row['High'], 2),
                    'low': round(row['Low'], 2),
                    'close': round(row['Close'], 2),
                    'volume': int(row['Volume'])
                })

            # Format market cap
            if market_cap >= 1e12:
                market_cap = f"${market_cap/1e12:.2f}T"
            elif market_cap >= 1e9:
                market_cap = f"${market_cap/1e9:.2f}B"
            elif market_cap >= 1e6:
                market_cap = f"${market_cap/1e6:.2f}M"

            # Get Wikipedia information
            wiki_info = ""
            try:
                wiki_page = wikipedia.page(company_name)
                wiki_info = wikipedia.summary(company_name, sentences=3)
            except:
                try:
                    # Try with symbol
                    wiki_page = wikipedia.page(symbol)
                    wiki_info = wikipedia.summary(symbol, sentences=3)
                except:
                    wiki_info = "Wikipedia information not available."

            # Get news from multiple sources
            news_items = []
            
            # 1. Get news from News API
            try:
                newsapi_url = 'https://newsapi.org/v2/everything'
                newsapi_params = {
                    'q': f'{symbol} stock',
                    'apiKey': NEWS_API_KEY,
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'pageSize': 5
                }
                
                newsapi_response = requests.get(newsapi_url, params=newsapi_params, timeout=10)
                newsapi_response.raise_for_status()
                newsapi_data = newsapi_response.json()
                
                if newsapi_data.get('status') == 'ok':
                    for article in newsapi_data.get('articles', []):
                        news_items.append({
                            'title': article['title'],
                            'link': article['url'],
                            'published': article['publishedAt'],
                            'source': article['source']['name'],
                            'description': article['description']
                        })
            except Exception as e:
                logger.error(f"Error fetching news from News API: {str(e)}")

            # 2. Get news from Google News
            try:
                search_query = urllib.parse.quote(f"{symbol} stock")
                google_news_url = f'https://news.google.com/search?q={search_query}&hl=en-IN&gl=IN&ceid=IN%3Aen'
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                response = requests.get(google_news_url, headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all article elements
                articles = soup.find_all('div', {'class': 'NiLAwe'})
                
                for article in articles[:5]:  # Get top 5 from Google News
                    try:
                        # Find title and link
                        title_elem = article.find('h3', {'class': 'ipQwMb'})
                        link_elem = article.find('a', {'class': 'VDXfz'})
                        
                        # Find time and source
                        time_elem = article.find('time')
                        source_elem = article.find('div', {'class': 'vr1PYe'})
                        
                        if title_elem and link_elem:
                            link = link_elem.get('href', '')
                            if link.startswith('./'):
                                link = 'https://news.google.com' + link[1:]
                            
                            news_items.append({
                                'title': title_elem.text.strip(),
                                'link': link,
                                'published': time_elem.text.strip() if time_elem else '',
                                'source': source_elem.text.strip() if source_elem else 'Google News',
                                'description': ''
                            })
                    except Exception as e:
                        logger.error(f"Error parsing Google News article: {str(e)}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error fetching news from Google News: {str(e)}")

            return JsonResponse({
                'status': 'success',
                'data': {
                    'company_name': company_name,
                    'current_price': round(current_price, 2),
                    'price_change': round(price_change, 2),
                    'price_change_percent': round(price_change_percent, 2),
                    'price_history': price_history,
                    'market_cap': market_cap,
                    'wiki_info': wiki_info,
                    'news': news_items,
                    'price_graph': price_graph
                }
            })

        except Exception as e:
            logger.error(f"Error fetching stock data: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error fetching data for {symbol} on {exchange}. Please check if the symbol is correct and try again.'
            }, status=404)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'An unexpected error occurred. Please try again later.'
        }, status=500)

def index(request):
    return render(request, 'index.html') 