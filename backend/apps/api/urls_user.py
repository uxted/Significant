"""User API URLs."""

from django.urls import path
from .views_user import (
    UserSubscriptionView,
    UserBookmarkView,
    BookmarkDetailView,
)

urlpatterns = [
    path("user/subscriptions/", UserSubscriptionView.as_view(), name="user-subscriptions"),
    path("user/bookmarks/", UserBookmarkView.as_view(), name="user-bookmarks"),
    path("user/bookmarks/<int:pk>/", BookmarkDetailView.as_view(), name="bookmark-detail"),
]
