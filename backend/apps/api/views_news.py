"""News API views."""

from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.postgres.search import SearchQuery, SearchRank

from apps.news.models import NewsArticle, NewsSource, NewsCategory
from apps.news.serializers import (
    NewsArticleListSerializer,
    NewsArticleDetailSerializer,
    SourceSerializer,
    CategorySerializer,
)


class NewsListView(generics.ListAPIView):
    """News list with filters, search, pagination."""

    permission_classes = []  # Public read
    serializer_class = NewsArticleListSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    filterset_fields = {
        "significance_level": ["in"],
        "category": ["exact", "in"],
        "source": ["exact", "in"],
        "published_at": ["gte", "lte"],
    }
    ordering_fields = ["published_at", "processed_at"]
    ordering = ["-published_at"]

    def get_queryset(self):
        queryset = NewsArticle.objects.select_related(
            "source", "category"
        ).all()

        # Full-text search
        search_query = self.request.query_params.get("search", None)
        if search_query:
            query = SearchQuery(search_query, config="russian")
            queryset = queryset.annotate(
                rank=SearchRank("search_vector", query)
            ).filter(search_vector=query).order_by("-rank", "-published_at")

        # Filter by assets
        assets = self.request.query_params.get("assets", None)
        if assets:
            asset_list = [a.strip() for a in assets.split(",")]
            # JSON field contains check
            from django.db.models import Q
            asset_query = Q()
            for asset in asset_list:
                asset_query |= Q(assets__contains=[asset])
            queryset = queryset.filter(asset_query)

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class NewsDetailView(generics.RetrieveAPIView):
    """News detail view."""

    permission_classes = []  # Public read
    queryset = NewsArticle.objects.select_related("source", "category").all()
    serializer_class = NewsArticleDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class SourceListView(generics.ListAPIView):
    """List all news sources."""

    permission_classes = []
    queryset = NewsSource.objects.filter(is_active=True).order_by("tier", "name")
    serializer_class = SourceSerializer


class CategoryListView(generics.ListAPIView):
    """List all news categories."""

    permission_classes = []
    queryset = NewsCategory.objects.all().order_by("id")
    serializer_class = CategorySerializer
