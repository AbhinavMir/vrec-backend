from celery import shared_task
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Transcription, Summary
from .summarizer import SUMMARIZE  # Replace this with your actual summarization function

@shared_task
def generate_summaries():
    today = timezone.now().date()
    last_monday = today - timedelta(days=today.weekday(), weeks=1)

    transcriptions_to_summarize = Transcription.objects.filter(date__gte=last_monday, date__lt=last_monday + timedelta(days=7))

    for transcription in transcriptions_to_summarize:
        # Assuming SUMMARIZE() returns a summary
        summary_text = SUMMARIZE(transcription.transcript) if transcription.transcript else None

        # Create a new summary entry or update an existing one
        summary, created = Summary.objects.get_or_create(
            user=transcription.user,
            date=last_monday,
            defaults={'mood': 'neutral', 'summary': summary_text}
        )

        if not created:
            # Update the existing summary
            summary.summary = summary_text
            summary.save()
