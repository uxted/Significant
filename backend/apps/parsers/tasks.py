import logging
import time
import json
from datetime import timedelta, datetime
from celery import shared_task
from django.utils import timezone
from feedparser import parse as parse_feed
from bs4 import BeautifulSoup

from apps.news.models import NewsArticle, NewsSource, NewsCategory
# Если у вас еще нет ML классификатора с такими функциями, закомментируйте эти строки и используйте заглушки ниже
try:
    from apps.ml_service.classifier import classify_article, assign_significance_level
except ImportError:
    # Заглушки, если ML модуль не готов или имена функций другие
    def classify_article(title, summary):
        return True, 0.9
    
    def assign_significance_level(confidence, tier, title, summary):
        return "HIGH" if tier <= 2 else "NORMAL"

# Исправленные импорты из utils и filters
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
            
            # Обновляем время последнего парсинга, если поле существует
            if hasattr(source, 'last_parsed'):
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
    # Ищем источники без RSS (только веб-страницы)
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
            
            if hasattr(source, 'last_parsed'):
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

    feed_url = source.feed_url if source.feed_url else source.url
    
    try:
        response = fetch_url(feed_url, timeout=30)
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

        summary = entry.get("summary", "") or entry.get("description", "")
        full_content = entry.get("content", [{}])[0].get("value", "") if hasattr(entry, "content") else ""

        title_hash = calculate_title_hash(title)

        # Используем функцию из utils
        if is_duplicate(title_hash):
            logger.debug(f"Duplicate article detected: {title[:50]}...")
            filtered_count += 1
            continue

        filter_result = filter_news(
            title=title,
            description=summary,
            content=full_content,
            source_tier=source.tier
        )

        if not filter_result.get('passed', False):
            logger.debug(f"Article filtered out: {title[:50]}... Reason: {filter_result.get('reason', 'Unknown')}")
            filtered_count += 1
            continue

        published_at = _parse_published_date(entry)

        article = _create_article(
            source=source,
            title=title,
            summary=summary,
            full_text=full_content,
            original_url=entry.get("link", ""),
            published_at=published_at,
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

    html_content = fetch_url(source.url, timeout=10)
    if not html_content:
        logger.warning(f"Failed to fetch web page for {source.name}")
        return 0, 0

    cleaned_text = clean_html(html_content)
    count = 0
    filtered_count = 0

    soup = BeautifulSoup(html_content, 'html.parser')
    articles = soup.find_all(["article", "div"], class_=lambda x: x and any(word in str(x) for word in ["news", "article", "post", "item"]))
    
    if not articles:
        articles = soup.find_all(["h1", "h2", "h3"])

    for article_tag in articles[:20]:
        title_tag = article_tag.find(["h1", "h2", "h3", "a"]) or article_tag
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)[:200]
        if not title or len(title) < 10:
            continue

        title_hash = calculate_title_hash(title)

        if is_duplicate(title_hash):
            filtered_count += 1
            continue

        link_tag = article_tag.find("a", href=True)
        summary_tag = article_tag.find("p")

        summary = summary_tag.get_text(strip=True)[:500] if summary_tag else ""
        original_url = link_tag["href"] if link_tag and link_tag.has_attr("href") else source.url

        filter_result = filter_news(
            title=title,
            description=summary,
            content=cleaned_text[:1000],
            source_tier=source.tier
        )

        if not filter_result.get('passed', False):
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


def is_duplicate(title_hash: str) -> bool:
    """Check if article with same title hash exists in last 24 hours."""
    cutoff = timezone.now() - timedelta(hours=24)
    return NewsArticle.objects.filter(
        title_hash=title_hash,
        published_at__gte=cutoff, # Исправлено на published_at, так как created_at может быть временем импорта
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
    if published_at is None:
        published_at = timezone.now()

    # ML классификация
    is_significant, confidence = classify_article(title, summary)

    if not is_significant:
        significance_level = "LOW"
    else:
        significance_level = assign_significance_level(
            confidence, source.tier, title, summary
        )

    category = _detect_category(title, summary)

    # Формируем словарь данных, адаптируясь под возможные имена полей в модели
    article_data = {
        'title': title[:200],
        'summary': summary[:1000],
        'full_text': full_text[:5000],      
        'source': source,
        'category': category,
        'is_significant': is_significant,
        'significance_level': significance_level, 
        'confidence_score': confidence,
        'original_url': original_url[:1000],       
        'published_at': published_at,
        'title_hash': title_hash,
    }
    
    # Добавляем опциональные поля, если они есть в модели
    # if hasattr(NewsArticle, 'needs_moderation'):
    #     article_data['needs_moderation'] = (0.4 <= confidence <= 0.6)
    
    try:
        article = NewsArticle.objects.create(**article_data)
        return article
    except Exception as e:
        logger.error(f"Error creating article: {e}")
        return None


def _detect_category(title: str, summary: str) -> NewsCategory:
    """Simple category detection by keywords."""
    text = f"{title} {summary}".lower()

    category_keywords = {
        "MACRO": ["ставка", "инфляци", "ввп", "безработиц", "цб росс", "ключевая ставка"],
        "BANKS": ["банк", "кредит", "депозит", "ипотек", "финанс"],
        "OIL_GAS": ["нефт", "газ", "лукойл", "газпром", "транснефт"],
        "IT_TELECOM": ["it", "телеком", "интернет", "софт", "цифр", "яндекс"],
        "INDUSTRY": ["завод", "производств", "металл", "пром", "строй"],
    }

    # Пытаемся найти категорию по коду
    for code, keywords in category_keywords.items():
        for kw in keywords:
            if kw in text:
                try:
                    return NewsCategory.objects.get(code=code)
                except NewsCategory.DoesNotExist:
                    continue

    # Возвращаем первую попавшуюся категорию, если ничего не найдено
    return NewsCategory.objects.first()


def _parse_published_date(entry) -> datetime:
    """Parse published date from RSS entry."""
    import email.utils
    
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            dt = datetime(*entry.published_parsed[:6])
            return timezone.make_aware(dt)
        except (TypeError, ValueError):
            pass
    
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        try:
            dt = datetime(*entry.updated_parsed[:6])
            return timezone.make_aware(dt)
        except (TypeError, ValueError):
            pass
            
    return timezone.now()