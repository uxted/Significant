"""Signals for full-text search indexing."""

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.postgres.search import SearchVector
from .models import NewsArticle


@receiver(pre_save, sender=NewsArticle)
def update_search_vector(sender, instance, **kwargs):
    """Update search_vector before saving."""
    instance.search_vector = (
        SearchVector("title", weight="A", config="russian")
        + SearchVector("summary", weight="B", config="russian")
    )
