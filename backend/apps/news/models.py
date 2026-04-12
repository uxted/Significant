"""Models for news module."""

from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField


class NewsSource(models.Model):
    """News source with trust level."""

    class Tier(models.IntegerChoices):
        REGULATOR = 1, "Официальный регулятор"
        AGENCY = 2, "Информагентство"
        BUSINESS_MEDIA = 3, "Деловые СМИ"
        CORPORATE = 4, "Корпоративные раскрытия"

    name = models.CharField("Название", max_length=200)
    url = models.URLField("URL")
    tier = models.IntegerField("Уровень доверия", choices=Tier.choices)
    feed_url = models.URLField("URL RSS-фида", blank=True, default="")
    is_active = models.BooleanField("Активен", default=True)
    last_parsed = models.DateTimeField("Последний парсинг", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Источник"
        verbose_name_plural = "Источники"

    def __str__(self):
        return f"{self.name} (Tier {self.tier})"


class NewsCategory(models.Model):
    """News category."""

    MACRO = "macro"
    CORPORATE = "corporate"
    REGULATORY = "regulatory"
    MARKET = "market"
    GEOPOLITICS = "geopolitics"

    CODES = [
        (MACRO, "Макроэкономика"),
        (CORPORATE, "Корпоративные события"),
        (REGULATORY, "Регуляторные решения"),
        (MARKET, "Рыночные события"),
        (GEOPOLITICS, "Геополитика"),
    ]

    code = models.CharField(max_length=20, unique=True, choices=CODES)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class NewsArticle(models.Model):
    """Individual news article."""

    class SignificanceLevel(models.TextChoices):
        HIGH = "HIGH", "Высокий"
        MEDIUM = "MEDIUM", "Средний"
        LOW = "LOW", "Низкий"

    # Content
    title = models.CharField("Заголовок", max_length=500)
    summary = models.TextField("Краткое описание", blank=True, default="")
    full_text = models.TextField("Полный текст", blank=True, default="")

    # Source & category
    source = models.ForeignKey(
        NewsSource,
        on_delete=models.PROTECT,
        related_name="articles",
        verbose_name="Источник",
    )
    category = models.ForeignKey(
        NewsCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
        verbose_name="Категория",
    )

    # Classification
    is_significant = models.BooleanField("Значимая (ML)", default=False)
    significance_level = models.CharField(
        "Уровень значимости",
        max_length=10,
        choices=SignificanceLevel.choices,
        default=SignificanceLevel.LOW,
    )
    confidence_score = models.FloatField("Confidence score ML", default=0.0)
    needs_moderation = models.BooleanField("Требует модерации", default=False)
    is_unconfirmed = models.BooleanField("Неподтверждённый слух", default=False)

    # Metadata
    original_url = models.URLField("Ссылка на оригинал", max_length=1000)
    published_at = models.DateTimeField("Дата публикации")
    processed_at = models.DateTimeField("Дата обработки", auto_now_add=True)
    title_hash = models.CharField("Хеш заголовка", max_length=64, db_index=True)

    # Affected assets
    assets = models.JSONField("Затрагиваемые активы", default=list, blank=True)

    # Full-text search
    search_vector = SearchVectorField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ["-published_at"]
        indexes = [
            models.Index(fields=["-published_at"]),
            models.Index(fields=["significance_level"]),
            models.Index(fields=["source"]),
            models.Index(fields=["category"]),
            models.Index(fields=["title_hash"]),
            GinIndex(fields=["search_vector"], name="idx_search_vector"),
        ]

    def __str__(self):
        return f"{self.title[:80]} [{self.significance_level}]"


class NewsCluster(models.Model):
    """Cluster of duplicate/similar news from different sources."""

    leader_article = models.ForeignKey(
        NewsArticle,
        on_delete=models.CASCADE,
        related_name="cluster_leader",
        verbose_name="Основная новость",
    )
    articles = models.ManyToManyField(
        NewsArticle,
        related_name="clusters",
        verbose_name="Дубликаты",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Кластер новостей"
        verbose_name_plural = "Кластеры новостей"

    def __str__(self):
        return f"Cluster: {self.leader_article.title[:60]}"
