"""Integration tests for full parsing cycle."""

import pytest
from unittest.mock import patch, MagicMock
from apps.news.models import NewsArticle, NewsSource, NewsCategory
from apps.parsers.tasks import _parse_single_rss


@pytest.mark.django_db
@patch("apps.parsers.tasks.parse_feed")
@patch("apps.parsers.tasks.classify_article")
def test_full_rss_parsing_cycle(mock_classify, mock_parse_feed):
    """Test complete RSS parsing: parse → dedup → classify → save."""
    # Setup mock RSS data
    mock_entry = MagicMock()
    mock_entry.title = "ЦБ повысил ключевую ставку"
    mock_entry.summary = "Совет директоров Банка России принял решение..."
    mock_entry.link = "https://cbr.ru/news/123"
    mock_entry.published_parsed = (2026, 3, 15, 14, 30, 0, 0, 0, 0)

    mock_feed = MagicMock()
    mock_feed.entries = [mock_entry]
    mock_parse_feed.return_value = mock_feed

    # Mock ML classification
    mock_classify.return_value = (True, 0.85)

    # Create source
    source = NewsSource.objects.create(
        name="ЦБ РФ",
        url="https://cbr.ru",
        tier=1,
        feed_url="https://cbr.ru/rss/",
    )

    # Run parsing
    count = _parse_single_rss(source)

    assert count == 1
    assert NewsArticle.objects.filter(title_hash__isnull=False).count() == 1

    article = NewsArticle.objects.first()
    assert article.is_significant is True
    assert article.confidence_score == 0.85


@pytest.mark.django_db
def test_deduplication_prevents_duplicates():
    """Test that duplicate titles are not created."""
    from apps.parsers.tasks import _is_duplicate
    from apps.news.models import NewsArticle, NewsSource

    source = NewsSource.objects.create(
        name="Test", url="https://test.ru", tier=2
    )
    NewsArticle.objects.create(
        title="Test Article",
        source=source,
        title_hash="same_hash_123",
    )

    assert _is_duplicate("same_hash_123") is True
    assert _is_duplicate("different_hash") is False


@pytest.mark.django_db
def test_rule_based_filter_skips_non_economic():
    """Test that rule-based filter skips non-economic news."""
    from apps.parsers.tasks import _rule_based_filter
    from apps.news.models import NewsSource

    source = NewsSource.objects.create(
        name="Sport News", url="https://sport.ru", tier=3
    )

    assert _rule_based_filter("Сборная России выиграла чемпионат", source) is False
    assert _rule_based_filter("ЦБ повысил ставку", source) is True
