"""Celery tasks for parsing."""

import logging
import time
import json
from datetime import timedelta
from celery import shared_task
from django.utils import timezone
from feedparser import parse as parse_feed
from bs4 import BeautifulSoup

from apps.news.models import NewsArticle, NewsSource, NewsCategory
from apps.ml_service.classifier import classify_article, assign_significance_level
from apps.parsers.utils import (
    fetch_url,
    clean_html,
    calculate_title_hash,
)
from apps.parsers.filters import filter_news

logger = logging.getLogger("parser")


@shared_task(bind=True, max_retries=3)
def parse_rss_sources(self):
    """Parse all active RSS sources with enhanced logging and error handling."""
    start_time = time.time()
    sources = NewsSource.objects.filter(is_active=True).exclude(feed_url="")
    total_parsed = 0
    total_filtered = 0
    total_errors = 0

    logger.info(json.dumps({
        "event": "rss_parsing_started",
        "sources_count": sources.count(),
        "timestamp": timezone.now().isoformat()
    }))

    for source in sources:
        try:
            parsed_count, filtered_count = _parse_single_rss(source)
            total_parsed += parsed_count
            total_filtered += filtered_count
            source.last_parsed = timezone.now()
            source.save(update_fields=["last_parsed"])

            logger.info(json.dumps({
                "event": "rss_source_parsed",
                "source_id": source.id,
                "source_name": source.name,
                "source_tier": source.tier,
                "articles_parsed": parsed_count,
                "articles_filtered": filtered_count,
                "timestamp": timezone.now().isoformat()
            }))
        except Exception as exc:
            total_errors += 1
            logger.error(json.dumps({
                "event": "rss_source_error",
                "source_id": source.id,
                "source_name": source.name,
                "error": str(exc),
                "timestamp": timezone.now().isoformat()
            }))
            # Не делаем retry для отдельных источников, продолжаем дальше
            continue

    duration = time.time() - start_time
    logger.info(json.dumps({
        "event": "rss_parsing_completed",
        "total_articles_parsed": total_parsed,
        "total_articles_filtered": total_filtered,
        "total_errors": total_errors,
        "duration_seconds": round(duration, 2),
        "timestamp": timezone.now().isoformat()
    }))

    return {"parsed": total_parsed, "filtered": total_filtered, "errors": total_errors}


@shared_task(bind=True, max_retries=3)
def parse_web_sources(self):
    """Parse web sources using BeautifulSoup with enhanced logging."""
    start_time = time.time()
    sources = NewsSource.objects.filter(is_active=True).filter(feed_url="")
    total_parsed = 0
    total_filtered = 0
    total_errors = 0

    logger.info(json.dumps({
        "event": "web_parsing_started",
        "sources_count": sources.count(),
        "timestamp": timezone.now().isoformat()
    }))

    for source in sources:
        try:
            parsed_count, filtered_count = _parse_single_web(source)
            total_parsed += parsed_count
            total_filtered += filtered_count
            source.last_parsed = timezone.now()
            source.save(update_fields=["last_parsed"])

            logger.info(json.dumps({
                "event": "web_source_parsed",
                "source_id": source.id,
                "source_name": source.name,
                "source_tier": source.tier,
                "articles_parsed": parsed_count,
                "articles_filtered": filtered_count,
                "timestamp": timezone.now().isoformat()
            }))
        except Exception as exc:
            total_errors += 1
            logger.error(json.dumps({
                "event": "web_source_error",
                "source_id": source.id,
                "source_name": source.name,
                "error": str(exc),
                "timestamp": timezone.now().isoformat()
            }))
            continue

    duration = time.time() - start_time
    logger.info(json.dumps({
        "event": "web_parsing_completed",
        "total_articles_parsed": total_parsed,
        "total_articles_filtered": total_filtered,
        "total_errors": total_errors,
        "duration_seconds": round(duration, 2),
        "timestamp": timezone.now().isoformat()
    }))

    return {"parsed": total_parsed, "filtered": total_filtered, "errors": total_errors}


def _parse_single_rss(source: NewsSource) -> tuple:
    """Parse a single RSS feed with enhanced deduplication and filtering."""
    start_time = time.time()

    # Загружаем RSS ленту с таймаутом
    try:
        response = fetch_url(source.feed_url, timeout=10)
        if not response:
            logger.warning(f"Failed to fetch RSS feed for {source.name}")
            return 0, 0
        feed = parse_feed(response)
    except Exception as e:
        logger.error(f"Error parsing RSS feed for {source.name}: {e}")
        return 0, 0

    count = 0
    filtered_count = 0

    for entry in feed.entries:
        title = entry.get("title", "")
        if not title:
            continue

        # Извлекаем описание и контент
        summary = entry.get("summary", "") or entry.get("description", "")
        full_content = entry.get("content", [{}])[0].get("value", "") if hasattr(entry, "content") else ""

        # Вычисляем хеш заголовка для дедупликации
        title_hash = calculate_title_hash(title)

        # Проверяем на дубликат (за последние 24 часа)
        if _is_duplicate(title_hash):
            logger.debug(f"Duplicate article detected: {title[:50]}...")
            filtered_count += 1
            continue

        # Применяем rule-based фильтрацию
        filter_result = filter_news(
            title=title,
            description=summary,
            content=full_content,
            source_tier=source.tier
        )

        if not filter_result['passed']:
            logger.debug(f"Article filtered out: {title[:50]}... Reason: {filter_result['reason']}")
            filtered_count += 1
            continue

        # Создаем статью
        article = _create_article(
            source=source,
            title=title,
            summary=summary,
            full_text=full_content,
            original_url=entry.get("link", ""),
            published_at=_parse_published_date(entry),
            title_hash=title_hash,
            filter_result=filter_result,
        )
        if article:
            count += 1

    duration = time.time() - start_time
    logger.info(json.dumps({
        "event": "rss_source_parsed_detail",
        "source_name": source.name,
        "articles_parsed": count,
        "articles_filtered": filtered_count,
        "duration_seconds": round(duration, 2)
    }))
    return count, filtered_count


def _parse_single_web(source: NewsSource) -> tuple:
    """Parse a single web page with enhanced HTML cleaning."""
    start_time = time.time()

    # Загружаем страницу с таймаутом и ротацией User-Agent
    html_content = fetch_url(source.url, timeout=10)
    if not html_content:
        logger.warning(f"Failed to fetch web page for {source.name}")
        return 0, 0

    # Очищаем HTML от мусора
    cleaned_text = clean_html(html_content)

    count = 0
    filtered_count = 0

    # Простая эвристика для выделения отдельных новостей из страницы
    # В реальном проекте нужно парсить конкретную структуру каждого сайта
    soup = BeautifulSoup(html_content, 'html.parser')

    # Ищем заголовки новостей
    articles = soup.find_all(["article", "div"], class_=lambda x: x and any(word in str(x) for word in ["news", "article", "post", "item"]))
    if not articles:
        # Если не нашли структурированные элементы, пробуем найти все заголовки
        articles = soup.find_all(["h1", "h2", "h3"])

    for article_tag in articles[:20]:  # Ограничиваем количество обрабатываемых элементов
        title_tag = article_tag.find(["h1", "h2", "h3", "a"]) or article_tag
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)[:200]
        if not title or len(title) < 10:
            continue

        title_hash = calculate_title_hash(title)

        if _is_duplicate(title_hash):
            filtered_count += 1
            continue

        # Пробуем найти ссылку и описание
        link_tag = article_tag.find("a", href=True)
        summary_tag = article_tag.find("p")

        summary = summary_tag.get_text(strip=True)[:500] if summary_tag else ""
        original_url = link_tag["href"] if link_tag and link_tag.has_attr("href") else source.url

        # Применяем фильтрацию
        filter_result = filter_news(
            title=title,
            description=summary,
            content=cleaned_text[:1000],
            source_tier=source.tier
        )

        if not filter_result['passed']:
            filtered_count += 1
            continue

        article = _create_article(
            source=source,
            title=title,
            summary=summary,
            full_text=cleaned_text[:2000],
            original_url=original_url,
            published_at=timezone.now(),
            title_hash=title_hash,
            filter_result=filter_result,
        )
        if article:
            count += 1

    duration = time.time() - start_time
    logger.info(json.dumps({
        "event": "web_source_parsed_detail",
        "source_name": source.name,
        "articles_parsed": count,
        "articles_filtered": filtered_count,
        "duration_seconds": round(duration, 2)
    }))
    return count, filtered_count


def _is_duplicate(title_hash: str) -> bool:
    """Check if article with same title hash exists in last 24 hours."""
    cutoff = timezone.now() - timedelta(hours=24)
    return NewsArticle.objects.filter(
        title_hash=title_hash,
        created_at__gte=cutoff,
    ).exists()


def _create_article(
    source,
    title,
    summary="",
    full_text="",
    original_url="",
    published_at=None,
    title_hash="",
    filter_result=None,
):
    """Create article with ML classification and enhanced filtering."""
    from datetime import datetime

    if published_at is None:
        published_at = timezone.now()

    # ML классификация (используем fallback TF-IDF + Logistic Regression)
    is_significant, confidence = classify_article(title, summary)

    if not is_significant:
        significance_level = "LOW"
    else:
        significance_level = assign_significance_level(
            confidence, source.tier, title, summary
        )

    # Определяем категорию
    category = _detect_category(title, summary)

    # Создаем статью
    article = NewsArticle.objects.create(
        title=title[:200],  # Ограничиваем длину заголовка
        summary=summary[:1000],
        full_text=full_text[:5000],
        source=source,
        category=category,
        is_significant=is_significant,
        significance_level=significance_level,
        confidence_score=confidence,
        original_url=original_url[:1000],
        published_at=published_at,
        title_hash=title_hash,
        needs_moderation=(0.4 <= confidence <= 0.6),
        filter_data=filter_result or {},  # Сохраняем результаты фильтрации
    )
    return article


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