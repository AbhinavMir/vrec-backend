# api_app/management/commands/fetch_transcriptions_weekly.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from api_app.views import FetchAllTranscriptions

class Command(BaseCommand):
    help = 'Fetch transcriptions weekly'

    def handle(self, *args, **options):
        today = timezone.now().date()
        # Check if today is Monday
        if today.weekday() == 0:
            FetchAllTranscriptions().get(None)
        else:
            self.stdout.write(self.style.SUCCESS("Today is not Monday. Skipping weekly transcription fetching."))
