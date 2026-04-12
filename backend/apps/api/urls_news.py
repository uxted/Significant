"""News API URLs."""

from django.urls import path
from .views_news import NewsListView, NewsDetailView, SourceListView, CategoryListView

urlpatterns = [
    path("news/", NewsListView.as_view(), name="news-list"),
    path("news/<int:pk>/", NewsDetailView.as_view(), name="news-detail"),
    path("sources/", SourceListView.as_view(), name="source-list"),
    path("categories/", CategoryListView.as_view(), name="category-list"),
]
