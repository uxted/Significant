"""Unit tests for news API endpoint."""

import pytest
from apps.news.models import NewsArticle, NewsSource, NewsCategory


@pytest.mark.django_db
def test_news_list_returns_paginated_response(auth_client):
    """Test that news list returns paginated response."""
    response = auth_client.get("/api/news/")
    assert response.status_code == 200
    assert "count" in response.data
    assert "results" in response.data


@pytest.mark.django_db
def test_news_list_filter_by_significance(auth_client):
    """Test filtering news by significance level."""
    source = NewsSource.objects.create(
        name="Test Source", url="https://test.ru", tier=2
    )
    category = NewsCategory.objects.create(
        code="macro", name="Макроэкономика"
    )
    NewsArticle.objects.create(
        title="ЦБ повысил ставку",
        significance_level="HIGH",
        source=source,
        category=category,
        title_hash="abc123",
    )

    response = auth_client.get("/api/news/?significance__in=HIGH")
    assert response.status_code == 200
    assert response.data["count"] >= 1
    assert response.data["results"][0]["significance_level"] == "HIGH"


@pytest.mark.django_db
def test_news_detail_view(auth_client):
    """Test news detail endpoint."""
    source = NewsSource.objects.create(
        name="Test Source", url="https://test.ru", tier=2
    )
    article = NewsArticle.objects.create(
        title="Test Article",
        summary="Test summary",
        significance_level="MEDIUM",
        source=source,
        title_hash="def456",
    )

    response = auth_client.get(f"/api/news/{article.id}/")
    assert response.status_code == 200
    assert response.data["title"] == "Test Article"


@pytest.mark.django_db
def test_news_search(auth_client):
    """Test full-text search on news."""
    source = NewsSource.objects.create(
        name="Test Source", url="https://test.ru", tier=2
    )
    NewsArticle.objects.create(
        title="ЦБ повысил ключевую ставку до 16%",
        summary="Совет директоров принял решение",
        significance_level="HIGH",
        source=source,
        title_hash="ghi789",
    )

    response = auth_client.get("/api/news/?search=ключевая ставка")
    assert response.status_code == 200
