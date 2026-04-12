"""Admin API views."""

import logging
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from apps.news.models import NewsArticle, NewsSource
from apps.news.serializers import SourceSerializer

logger = logging.getLogger("audit")


class AdminSourceListView(generics.ListCreateAPIView):
    """List/create news sources (admin only)."""

    permission_classes = [IsAdminUser]
    queryset = NewsSource.objects.all().order_by("tier", "name")
    serializer_class = SourceSerializer

    def perform_create(self, serializer):
        source = serializer.save()
        logger.info(
            f"Admin {self.request.user.email} created source: {source.name}",
            extra={
                "admin_user": self.request.user.email,
                "action": "source_created",
                "target_object": f"NewsSource(id={source.id})",
            },
        )


class AdminSourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Update/delete a source (admin only)."""

    permission_classes = [IsAdminUser]
    queryset = NewsSource.objects.all()
    serializer_class = SourceSerializer

    def perform_update(self, serializer):
        old_values = {
            "is_active": self.get_object().is_active,
        }
        source = serializer.save()
        logger.info(
            f"Admin {self.request.user.email} updated source: {source.name}",
            extra={
                "admin_user": self.request.user.email,
                "action": "source_updated",
                "target_object": f"NewsSource(id={source.id})",
                "old_value": old_values,
                "new_value": {"is_active": source.is_active},
            },
        )

    def perform_destroy(self, instance):
        logger.info(
            f"Admin {self.request.user.email} deleted source: {instance.name}",
            extra={
                "admin_user": self.request.user.email,
                "action": "source_deleted",
                "target_object": f"NewsSource(id={instance.id})",
            },
        )
        instance.delete()


class AdminModerationView(generics.ListAPIView):
    """List articles needing moderation."""

    permission_classes = [IsAdminUser]
    serializer_class = SourceSerializer  # placeholder — use news serializers

    def get_queryset(self):
        return NewsArticle.objects.filter(needs_moderation=True).order_by(
            "-published_at"
        )


class AdminModerationActionView(generics.GenericAPIView):
    """Perform moderation action on an article."""

    permission_classes = [IsAdminUser]

    def put(self, request, article_id):
        try:
            article = NewsArticle.objects.get(id=article_id)
        except NewsArticle.DoesNotExist:
            return Response(
                {"error": "Article not found"}, status=status.HTTP_404_NOT_FOUND
            )

        action = request.data.get("action")
        if action == "approve":
            article.needs_moderation = False
            article.is_significant = request.data.get("is_significant", article.is_significant)
            article.save()
            logger.info(
                f"Admin {request.user.email} approved article {article_id}",
                extra={
                    "admin_user": request.user.email,
                    "action": "article_approved",
                    "target_object": f"NewsArticle(id={article_id})",
                },
            )
            return Response({"detail": "Статья одобрена"})

        elif action == "reject":
            article.is_significant = False
            article.significance_level = "LOW"
            article.needs_moderation = False
            article.save()
            logger.info(
                f"Admin {request.user.email} rejected article {article_id}",
                extra={
                    "admin_user": request.user.email,
                    "action": "article_rejected",
                    "target_object": f"NewsArticle(id={article_id})",
                },
            )
            return Response({"detail": "Статья отклонена"})

        return Response(
            {"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST
        )
