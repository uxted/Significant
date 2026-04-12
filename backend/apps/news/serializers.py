"""Serializers for news."""

from rest_framework import serializers
from .models import NewsArticle, NewsSource, NewsCategory


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsSource
        fields = ("id", "name", "url", "tier")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsCategory
        fields = ("id", "code", "name")


class NewsArticleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view."""

    source = SourceSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = NewsArticle
        fields = (
            "id",
            "title",
            "summary",
            "source",
            "category",
            "significance_level",
            "published_at",
            "processed_at",
            "assets",
            "original_url",
            "is_bookmarked",
        )

    def get_is_bookmarked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.userbookmark_set.filter(user=request.user).exists()
        return False


class NewsArticleDetailSerializer(serializers.ModelSerializer):
    """Full serializer for detail view."""

    source = SourceSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = NewsArticle
        fields = (
            "id",
            "title",
            "summary",
            "full_text",
            "source",
            "category",
            "significance_level",
            "confidence_score",
            "published_at",
            "processed_at",
            "assets",
            "original_url",
            "is_bookmarked",
            "is_unconfirmed",
            "needs_moderation",
        )

    def get_is_bookmarked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.userbookmark_set.filter(user=request.user).exists()
        return False
