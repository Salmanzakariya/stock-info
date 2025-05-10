import schedule
import time
from django.core.management import call_command

def schedule_news_fetch():
    """Schedule news fetching to run every hour"""
    schedule.every().hour.do(call_command, 'fetch_news')
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == '__main__':
    schedule_news_fetch()
