"""Celery tasks for parsing."""

import logging
import time
from celery import shared_task
from django.utils import timezone
from feedparser import parse as parse_feed
from bs4 import BeautifulSoup
import requests
import hashlib

from apps.news.models import NewsArticle, NewsSource, NewsCategory
from apps.ml_service.classifier import classify_article, assign_significance_level

logger = logging.getLogger("parser")


@shared_task(bind=True, max_retries=3)
def parse_rss_sources(self):
    """Parse all active RSS sources."""
    sources = NewsSource.objects.filter(is_active=True).exclude(feed_url="")
    total_parsed = 0

    for source in sources:
        try:
            count = _parse_single_rss(source)
            total_parsed += count
            source.last_parsed = timezone.now()
            source.save(update_fields=["last_parsed"])
        except Exception as exc:
            logger.error(f"Error parsing RSS source {source.name}: {exc}")
            self.retry(exc=exc, countdown=300)

    logger.info(f"RSS parsing completed: {total_parsed} articles parsed")
    return total_parsed


@shared_task(bind=True, max_retries=3)
def parse_web_sources(self):
    """Parse web sources using BeautifulSoup."""
    sources = NewsSource.objects.filter(is_active=True).filter(feed_url="")
    total_parsed = 0

    for source in sources:
        try:
            count = _parse_single_web(source)
            total_parsed += count
            source.last_parsed = timezone.now()
            source.save(update_fields=["last_parsed"])
        except Exception as exc:
            logger.error(f"Error parsing web source {source.name}: {exc}")
            self.retry(exc=exc, countdown=600)

    logger.info(f"Web parsing completed: {total_parsed} articles parsed")
    return total_parsed


def _parse_single_rss(source: NewsSource) -> int:
    """Parse a single RSS feed."""
    start_time = time.time()
    feed = parse_feed(source.feed_url)
    count = 0

    for entry in feed.entries:
        title = entry.get("title", "")
        if not title:
            continue

        # Deduplication
        title_hash = hashlib.sha256(title.encode("utf-8")).hexdigest()
        if _is_duplicate(title_hash):
            continue

        # Create article
        article = _create_article(
            source=source,
            title=title,
            summary=entry.get("summary", ""),
            full_text=entry.get("description", ""),
            original_url=entry.get("link", ""),
            published_at=_parse_published_date(entry),
            title_hash=title_hash,
        )
        if article:
            count += 1

    duration = time.time() - start_time
    logger.info(
        f"RSS source '{source.name}': {count} articles in {duration:.2f}s"
    )
    return count


def _parse_single_web(source: NewsSource) -> int:
    """Parse a single web page."""
    start_time = time.time()
    response = requests.get(source.url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    count = 0

    # Generic parsing logic — customize per source
    articles = soup.find_all("article") or soup.find_all(
        "div", class_=["news-item", "article", "post"]
    )

    for article_tag in articles:
        title_tag = article_tag.find("h1") or article_tag.find("h2") or article_tag.find("a")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        title_hash = hashlib.sha256(title.encode("utf-8")).hexdigest()

        if _is_duplicate(title_hash):
            continue

        link_tag = article_tag.find("a", href=True)
        summary = ""
        summary_tag = article_tag.find("p")
        if summary_tag:
            summary = summary_tag.get_text(strip=True)[:500]

        article = _create_article(
            source=source,
            title=title,
            summary=summary,
            original_url=link_tag["href"] if link_tag else source.url,
            published_at=timezone.now(),
            title_hash=title_hash,
        )
        if article:
            count += 1

    duration = time.time() - start_time
    logger.info(
        f"Web source '{source.name}': {count} articles in {duration:.2f}s"
    )
    return count


def _is_duplicate(title_hash: str) -> bool:
    """Check if article with same title hash exists in last 24 hours."""
    from datetime import timedelta

    cutoff = timezone.now() - timedelta(hours=24)
    return NewsArticle.objects.filter(
        title_hash=title_hash,
        created_at__gte=cutoff,
    ).exists()


def _create_article(source, title, summary="", full_text="",
                    original_url="", published_at=None, title_hash="") -> NewsArticle:
    """Create article with ML classification."""
    from datetime import datetime

    if published_at is None:
        published_at = timezone.now()

    # Rule-based filter
    if _rule_based_filter(title, source):
        # ML classification
        is_significant, confidence = classify_article(title, summary)

        if not is_significant:
            # Store but mark as not significant
            significance_level = "LOW"
        else:
            significance_level = assign_significance_level(
                confidence, source.tier, title, summary
            )

        article = NewsArticle.objects.create(
            title=title,
            summary=summary[:1000],
            full_text=full_text[:5000],
            source=source,
            category=_detect_category(title, summary),
            is_significant=is_significant,
            significance_level=significance_level,
            confidence_score=confidence,
            original_url=original_url[:1000],
            published_at=published_at,
            title_hash=title_hash,
            needs_moderation=(0.4 <= confidence <= 0.6),
        )
        return article

    return None


def _rule_based_filter(title: str, source: NewsSource) -> bool:
    """Rule-based filter to skip obviously non-significant news."""
    skip_keywords = ["спорт", "развлечения", "погода", "афиша", "рецепты"]
    title_lower = title.lower()

    # Skip if source tier 3+ and title contains skip words
    if source.tier >= 3:
        for keyword in skip_keywords:
            if keyword in title_lower:
                return False
    return True


def _detect_category(title: str, summary: str) -> NewsCategory:
    """Simple category detection by keywords."""
    text = f"{title} {summary}".lower()

    category_keywords = {
        "macro": ["ставка", "инфляци", "ввп", "безработиц", "цб росс", "ключевая ставка"],
        "corporate": ["отчёт", "дивиденд", "выручк", "прибыл", "ipo", "слиян", "поглощен"],
        "regulatory": ["закон", "санкци", "лицензи", "налог", "регулирован"],
        "market": ["торг", "листинг", "делистинг", "дефолт", "остановк"],
        "geopolitics": ["санкци", "ограничен", "экспорт", "импорт", "логистик"],
    }

    for code, keywords in category_keywords.items():
        for kw in keywords:
            if kw in text:
                return NewsCategory.objects.get(code=code)

    # Default
    return NewsCategory.objects.first()


def _parse_published_date(entry) -> timezone.datetime:
    """Parse published date from RSS entry."""
    from datetime import datetime
    import email.utils

    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return timezone.make_aware(
            datetime(*entry.published_parsed[:6])
        )
    return timezone.now()
