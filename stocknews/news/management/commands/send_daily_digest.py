from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from news.models import Article, UserPreferences
from django.conf import settings
import json

class Command(BaseCommand):
    help = 'Sends daily email digest of top market news'

    def handle(self, *args, **options):
        # Get articles from last 24 hours
        start_time = timezone.now() - timezone.timedelta(days=1)
        articles = Article.objects.filter(
            published_at__gte=start_time
        ).order_by('-published_at')[:5]

        # Get users who want daily digest
        users = UserPreferences.objects.filter(
            daily_digest_enabled=True
        ).select_related('user')

        for user_pref in users:
            user = user_pref.user
            
            # Render email template
            email_content = render_to_string('news/email/daily_digest.html', {
                'user': user,
                'articles': articles,
                'start_time': start_time
            })

            # Send email
            send_mail(
                subject=f'Daily Market News Digest - {timezone.now().strftime("%B %d, %Y")}',
                message='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=email_content,
                fail_silently=False,
            )

            self.stdout.write(
                self.style.SUCCESS(f'Sent daily digest to {user.email}')
            )
