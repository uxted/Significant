"""Tasks for news module (cleanup, backup)."""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from .models import NewsArticle

logger = logging.getLogger("parser")


@shared_task
def cleanup_old_data():
    """Delete articles older than 90 days."""
    cutoff_date = timezone.now() - timedelta(days=90)
    deleted_count, _ = NewsArticle.objects.filter(
        published_at__lt=cutoff_date
    ).delete()
    logger.info(f"Cleanup: deleted {deleted_count} old articles")
    return deleted_count


@shared_task
def backup_database():
    """Placeholder for database backup task."""
    logger.info("Database backup task executed")
    return True
