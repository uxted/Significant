"""
Management command to seed the database with initial data.

Usage:
    python manage.py seed_data
    python manage.py seed_data --demo-news=50
"""

import hashlib
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.news.models import NewsSource, NewsCategory, NewsArticle

User = get_user_model()


class Command(BaseCommand):
    help = "Seed database with categories, sources, demo news, and superuser."

    def add_arguments(self, parser):
        parser.add_argument(
            "--demo-news",
            type=int,
            default=0,
            help="Number of demo news articles to create (default: 0)",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing data before seeding",
        )

    def handle(self, *args, **options):
        reset = options["reset"]
        demo_count = options["demo_news"]

        if reset:
            self.stdout.write(self.style.WARNING("Deleting existing data..."))
            NewsArticle.objects.all().delete()
            NewsSource.objects.all().delete()
            NewsCategory.objects.all().delete()
            User.objects.filter(is_superuser=True).delete()

        self.seed_categories()
        self.seed_sources()
        self.seed_superuser()

        if demo_count > 0:
            self.seed_demo_news(demo_count)

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))

    def seed_categories(self):
        self.stdout.write("Creating categories...")
        categories = [
            (NewsCategory.MACRO, "Макроэкономика"),
            (NewsCategory.CORPORATE, "Корпоративные события"),
            (NewsCategory.REGULATORY, "Регуляторные решения"),
            (NewsCategory.MARKET, "Рыночные события"),
            (NewsCategory.GEOPOLITICS, "Геополитика"),
        ]

        for code, name in categories:
            _, created = NewsCategory.objects.get_or_create(
                code=code, defaults={"name": name}
            )
            if created:
                self.stdout.write(f"  ✓ Created category: {name}")
            else:
                self.stdout.write(f"  - Category exists: {name}")

    def seed_sources(self):
        self.stdout.write("Creating news sources...")
        sources = [
            # Tier 1 — Официальные регуляторы
            (
                "ЦБ РФ",
                "https://cbr.ru",
                1,
                "https://cbr.ru/press/pr rss/",
            ),
            (
                "Government.ru",
                "https://government.ru",
                1,
                "https://government.ru/rss/",
            ),
            (
                "e-disclosure.ru",
                "https://e-disclosure.ru",
                1,
                "",
            ),
            # Tier 2 — Информагентства
            (
                "ТАСС",
                "https://tass.ru",
                2,
                "https://tass.ru/rss/v2.xml",
            ),
            (
                "РИА Новости",
                "https://ria.ru",
                2,
                "https://ria.ru/export/rss2/index.xml",
            ),
            (
                "Интерфакс",
                "https://interfax.ru",
                2,
                "https://interfax.ru/rss.asp",
            ),
            # Tier 3 — Деловые СМИ
            (
                "РБК",
                "https://rbc.ru",
                3,
                "https://rbc.ru/vnews_feed.xml",
            ),
            (
                "Коммерсантъ",
                "https://kommersant.ru",
                3,
                "https://kommersant.ru/rss-all.xml",
            ),
            (
                "Ведомости",
                "https://vedomosti.ru",
                3,
                "https://vedomosti.ru/rss",
            ),
            (
                "Smart-Lab",
                "https://smart-lab.ru",
                3,
                "",
            ),
        ]

        for name, url, tier, feed_url in sources:
            _, created = NewsSource.objects.get_or_create(
                name=name,
                defaults={
                    "url": url,
                    "tier": tier,
                    "feed_url": feed_url,
                    "is_active": True,
                },
            )
            if created:
                tier_names = {1: "Регулятор", 2: "Агентство", 3: "Деловое СМИ", 4: "Корп."}
                self.stdout.write(
                    f"  ✓ Created source: {name} (Tier {tier} — {tier_names.get(tier, '?')})"
                )
            else:
                self.stdout.write(f"  - Source exists: {name}")

    def seed_superuser(self):
        self.stdout.write("Creating superuser...")
        if not User.objects.filter(email="admin@test.com").exists():
            User.objects.create_superuser(
                email="admin@test.com",
                password="adminpassword123",
            )
            self.stdout.write("  ✓ Created superuser: admin@test.com / adminpassword123")
        else:
            self.stdout.write("  - Superuser exists: admin@test.com")

        if not User.objects.filter(email="user@test.com").exists():
            User.objects.create_user(
                email="user@test.com",
                password="userpassword123",
                agreed_to_pd=True,
            )
            self.stdout.write("  ✓ Created user: user@test.com / userpassword123")
        else:
            self.stdout.write("  - User exists: user@test.com")

    def seed_demo_news(self, count):
        self.stdout.write(f"Creating {count} demo news articles...")

        sources = list(NewsSource.objects.all())
        categories = list(NewsCategory.objects.all())

        if not sources or not categories:
            self.stdout.write(self.style.ERROR("No sources or categories found. Run without --demo-news first."))
            return

        demo_news = [
            {
                "title": "ЦБ повысил ключевую ставку до 16%",
                "summary": "Совет директоров Банка России принял решение повысить ключевую ставку на 100 б.п., до 16,00% годовых. Решение связано с устойчивым отклонением инфляции вверх.",
                "significance": "HIGH",
                "category": NewsCategory.MACRO,
                "tier": 1,
                "assets": ["RUBUSD", "MOEX"],
                "is_significant": True,
                "confidence": 0.95,
            },
            {
                "title": "Газпром отчитался о росте чистой прибыли на 15%",
                "summary": "Чистая прибыль Газпрома по МСФО за 2025 год выросла на 15% и составила 1,8 трлн рублей. Выручка превысила 12 трлн рублей.",
                "significance": "HIGH",
                "category": NewsCategory.CORPORATE,
                "tier": 2,
                "assets": ["GAZP"],
                "is_significant": True,
                "confidence": 0.91,
            },
            {
                "title": "Введены новые санкции против технологического сектора",
                "summary": "США расширили список ограничений на экспорт полупроводниковых технологий в Россию. Под ограничения попали 12 компаний.",
                "significance": "HIGH",
                "category": NewsCategory.GEOPOLITICS,
                "tier": 2,
                "assets": ["MOEX", "RUBUSD"],
                "is_significant": True,
                "confidence": 0.93,
            },
            {
                "title": "Сбербанк объявил дивиденды за 2025 год",
                "summary": "Наблюдательный совет Сбербанка рекомендовал выплатить дивиденды в размере 33,3 рубля на акцию.",
                "significance": "MEDIUM",
                "category": NewsCategory.CORPORATE,
                "tier": 2,
                "assets": ["SBER"],
                "is_significant": True,
                "confidence": 0.87,
            },
            {
                "title": "Минфин разместил ОФЗ на 70 млрд рублей",
                "summary": "Министерство финансов провело аукцион по размещению облигаций федерального займа серии 26243 на сумму 70 млрд рублей.",
                "significance": "MEDIUM",
                "category": NewsCategory.MARKET,
                "tier": 1,
                "assets": ["RUBUSD"],
                "is_significant": True,
                "confidence": 0.82,
            },
            {
                "title": "Яндекс провёл IPO дочерней компании",
                "summary": "Яндекс разместил акции своего подразделения беспилотного транспорта на Московской бирже. Объём размещения — 15 млрд рублей.",
                "significance": "HIGH",
                "category": NewsCategory.MARKET,
                "tier": 3,
                "assets": ["YNDX"],
                "is_significant": True,
                "confidence": 0.90,
            },
            {
                "title": "Инфляция в России ускорилась до 7,5% в годовом выражении",
                "summary": "Росстат сообщил об ускорении годовой инфляции с 7,2% до 7,5%. Основной вклад оказали продовольственные товары и услуги ЖКХ.",
                "significance": "HIGH",
                "category": NewsCategory.MACRO,
                "tier": 2,
                "assets": ["RUBUSD", "MOEX"],
                "is_significant": True,
                "confidence": 0.94,
            },
            {
                "title": "ВТБ снизил ставки по ипотеке для зарплатных клиентов",
                "summary": "ВТБ объявил о снижении процентных ставок по ипотечным кредитам на 0,5 п.п. для клиентов, получающих зарплату на карту банка.",
                "significance": "LOW",
                "category": NewsCategory.CORPORATE,
                "tier": 3,
                "assets": ["VTBR"],
                "is_significant": False,
                "confidence": 0.45,
            },
            {
                "title": "Новые правила маркировки рекламы вступили в силу",
                "summary": "С 1 апреля 2026 года все рекламные объявления в интернете должны проходить обязательную маркировку через систему ОРД.",
                "significance": "MEDIUM",
                "category": NewsCategory.REGULATORY,
                "tier": 2,
                "assets": [],
                "is_significant": True,
                "confidence": 0.78,
            },
            {
                "title": "Московская биржа остановила торги акциями М.видео",
                "summary": "Торги обыкновенными акциями М.видео приостановлены до раскрытия существенного факта.",
                "significance": "HIGH",
                "category": NewsCategory.MARKET,
                "tier": 1,
                "assets": ["MVID"],
                "is_significant": True,
                "confidence": 0.88,
            },
            {
                "title": "Росстат: ВВП России вырос на 1,2% в IV квартале",
                "summary": "Предварительная оценка Росстата показала рост ВВП на 1,2% в годовом выражении в IV квартале 2025 года.",
                "significance": "MEDIUM",
                "category": NewsCategory.MACRO,
                "tier": 2,
                "assets": ["MOEX"],
                "is_significant": True,
                "confidence": 0.81,
            },
            {
                "title": "Лукойл завершил программу обратного выкупа акций",
                "summary": "Лукойл объявил о завершении программы обратного выкупа акций на сумму 5 млрд долларов. Всего было выкуплено 8% акций.",
                "significance": "MEDIUM",
                "category": NewsCategory.CORPORATE,
                "tier": 2,
                "assets": ["LKOH"],
                "is_significant": True,
                "confidence": 0.85,
            },
            {
                "title": "Ограничения на экспорт удобрений продлены до конца года",
                "summary": "Правительство продлило квоты на экспорт минеральных удобрений до 31 декабря 2026 года.",
                "significance": "MEDIUM",
                "category": NewsCategory.REGULATORY,
                "tier": 1,
                "assets": ["URKA", "PHOR"],
                "is_significant": True,
                "confidence": 0.76,
            },
            {
                "title": "Ростех анонсировал серийное производство нового процессора",
                "summary": "Ростех заявил о начале серийного производства микропроцессора «Байкал-М2» для серверного оборудования.",
                "significance": "MEDIUM",
                "category": NewsCategory.GEOPOLITICS,
                "tier": 3,
                "assets": [],
                "is_significant": True,
                "confidence": 0.72,
            },
            {
                "title": "Средняя зарплата в России выросла на 13% за год",
                "summary": "По данным Росстата, средняя начисленная зарплата в России составила 78 000 рублей, что на 13% выше прошлогоднего уровня.",
                "significance": "MEDIUM",
                "category": NewsCategory.MACRO,
                "tier": 3,
                "assets": [],
                "is_significant": True,
                "confidence": 0.70,
            },
            {
                "title": "РБК: Топ-10 лучших ресторанов Москвы по версии гидов",
                "summary": "РБК опубликовал рейтинг лучших ресторанов Москвы по итогам 2025 года. Лидером стал ресторан White Rabbit.",
                "significance": "LOW",
                "category": NewsCategory.MACRO,
                "tier": 3,
                "assets": [],
                "is_significant": False,
                "confidence": 0.25,
            },
            {
                "title": "Погода в Москве на выходные: потепление до +10",
                "summary": "Синоптики обещают потепление до +10 градусов в Москве в предстоящие выходные.",
                "significance": "LOW",
                "category": NewsCategory.MACRO,
                "tier": 3,
                "assets": [],
                "is_significant": False,
                "confidence": 0.10,
            },
            {
                "title": "Сборная России по хоккею выиграла турнир",
                "summary": "Сборная России одержала победу в финальном матче турнира.",
                "significance": "LOW",
                "category": NewsCategory.MACRO,
                "tier": 3,
                "assets": [],
                "is_significant": False,
                "confidence": 0.08,
            },
            {
                "title": "Новак: Россия готова увеличить добычу нефти",
                "summary": "Вице-премьер Александр Новак заявил о готовности России нарастить добычу нефти в рамках договорённостей ОПЕК+.",
                "significance": "HIGH",
                "category": NewsCategory.GEOPOLITICS,
                "tier": 2,
                "assets": ["GAZP", "LKOH", "ROSN"],
                "is_significant": True,
                "confidence": 0.92,
            },
            {
                "title": "Московская биржа ввела новый механизм расчётов",
                "summary": "Московская биржа внедрила систему мгновенных расчётов T+0 для операций с акциями первого эшелона.",
                "significance": "MEDIUM",
                "category": NewsCategory.MARKET,
                "tier": 1,
                "assets": ["MOEX"],
                "is_significant": True,
                "confidence": 0.79,
            },
        ]

        now = timezone.now()
        created = 0

        for i in range(count):
            if i < len(demo_news):
                item = demo_news[i]
            else:
                # Generate random news
                cat = random.choice(categories)
                src = random.choice(sources)
                item = {
                    "title": f"Демо-новость #{i + 1} от {now.strftime('%d.%m.%Y')}",
                    "summary": f"Автоматически сгенерированная демо-новость категории {cat.name}",
                    "significance": random.choice(["HIGH", "MEDIUM", "LOW"]),
                    "category": cat.code,
                    "tier": src.tier,
                    "assets": random.sample(["GAZP", "SBER", "YNDX", "LKOH", "VTBR", "MOEX"], k=random.randint(0, 3)),
                    "is_significant": random.choice([True, False]),
                    "confidence": round(random.uniform(0.1, 0.99), 2),
                }

            # Select source by tier preference
            tier_sources = [s for s in sources if s.tier <= item.get("tier", 3)]
            source = random.choice(tier_sources) if tier_sources else random.choice(sources)

            # Select category
            try:
                category = NewsCategory.objects.get(code=item["category"])
            except NewsCategory.DoesNotExist:
                category = random.choice(categories)

            title = item["title"]
            title_hash = hashlib.sha256(title.encode("utf-8")).hexdigest()

            # Time offset for variety
            time_offset = timedelta(hours=random.randint(0, 72), minutes=random.randint(0, 59))
            published_at = now - time_offset

            article = NewsArticle.objects.create(
                title=title,
                summary=item["summary"],
                full_text=item["summary"] + "\n\n[Полный текст новости — здесь будет развёрнутый материал с деталями события, комментариями экспертов и аналитикой.]",
                source=source,
                category=category,
                is_significant=item["is_significant"],
                significance_level=item["significance"],
                confidence_score=item["confidence"],
                original_url=f"{source.url}/news/{random.randint(10000, 99999)}",
                published_at=published_at,
                title_hash=title_hash,
                assets=item.get("assets", []),
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f"  ✓ Created {created} demo news articles"))

        # Print summary
        high = NewsArticle.objects.filter(significance_level="HIGH").count()
        medium = NewsArticle.objects.filter(significance_level="MEDIUM").count()
        low = NewsArticle.objects.filter(significance_level="LOW").count()
        self.stdout.write(f"  📊 Summary: 🔴 HIGH={high}, 🟡 MEDIUM={medium}, 🟢 LOW={low}")
