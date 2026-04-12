"""Admin API URLs."""

from django.urls import path
from .views_admin import (
    AdminSourceListView,
    AdminSourceDetailView,
    AdminModerationView,
    AdminModerationActionView,
)

urlpatterns = [
    path("admin/sources/", AdminSourceListView.as_view(), name="admin-sources"),
    path("admin/sources/<int:pk>/", AdminSourceDetailView.as_view(), name="admin-source-detail"),
    path("admin/moderation/", AdminModerationView.as_view(), name="admin-moderation"),
    path("admin/moderation/<int:article_id>/", AdminModerationActionView.as_view(), name="admin-moderation-action"),
]
