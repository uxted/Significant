"""User API views — subscriptions, bookmarks."""

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import models

from apps.news.models import NewsArticle, NewsCategory
from apps.users.models import User


class UserSubscription(models.Model):
    """User subscription to categories/assets."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(NewsCategory, on_delete=models.CASCADE, null=True, blank=True)
    asset_ticker = models.CharField(max_length=20, blank=True, default="")

    class Meta:
        unique_together = ["user", "category", "asset_ticker"]

    def __str__(self):
        target = self.category or self.asset_ticker
        return f"{self.user.email} → {target}"


class UserBookmark(models.Model):
    """User bookmark of news article."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "article"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} bookmarked {self.article.title[:40]}"


class UserSubscriptionView(generics.GenericAPIView):
    """Get/update user subscriptions."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        subscriptions = UserSubscription.objects.filter(user=request.user)
        data = {
            "categories": list(
                subscriptions.exclude(category__isnull=True).values_list(
                    "category_id", flat=True
                )
            ),
            "assets": list(
                subscriptions.exclude(asset_ticker="").values_list(
                    "asset_ticker", flat=True
                )
            ),
        }
        return Response(data)

    def put(self, request):
        # Clear existing
        UserSubscription.objects.filter(user=request.user).delete()

        # Create new
        categories = request.data.get("categories", [])
        assets = request.data.get("assets", [])

        for cat_id in categories:
            UserSubscription.objects.create(
                user=request.user, category_id=cat_id
            )
        for ticker in assets:
            UserSubscription.objects.create(
                user=request.user, asset_ticker=ticker
            )

        return Response({"detail": "Подписки обновлены"})


class UserBookmarkView(generics.GenericAPIView):
    """Get/add bookmarks."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookmarks = UserBookmark.objects.filter(user=request.user).select_related(
            "article__source", "article__category"
        )
        from apps.news.serializers import NewsArticleListSerializer
        articles = [b.article for b in bookmarks]
        serializer = NewsArticleListSerializer(
            articles, many=True, context={"request": request}
        )
        return Response(serializer.data)

    def post(self, request):
        article_id = request.data.get("article_id")
        if not article_id:
            return Response(
                {"error": "article_id required"}, status=status.HTTP_400_BAD_REQUEST
            )

        bookmark, created = UserBookmark.objects.get_or_create(
            user=request.user, article_id=article_id
        )
        if created:
            return Response({"detail": "Добавлено в закладки"}, status=status.HTTP_201_CREATED)
        return Response({"detail": "Уже в закладках"}, status=status.HTTP_200_OK)


class BookmarkDetailView(generics.GenericAPIView):
    """Remove a bookmark."""

    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        UserBookmark.objects.filter(user=request.user, article_id=pk).delete()
        return Response({"detail": "Удалено из закладок"}, status=status.HTTP_200_OK)
