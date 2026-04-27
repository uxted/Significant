from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Загружаем конфигурацию из settings.py с префиксом CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически обнаруживаем задачи во всех установленных приложениях
app.autodiscover_tasks()


# Настройка расписания задач (Celery Beat)
app.conf.beat_schedule = {
    # Парсинг RSS-лент каждые 5 минут
    "parse-rss-sources-every-5-minutes": {
        "task": "apps.parsers.tasks.parse_rss_sources",
        "schedule": 300.0,  # 300 секунд = 5 минут
        "options": {"queue": "celery"}
    },
    
    # Очистка старых данных ежедневно в 03:00 UTC
    "cleanup-old-data-daily": {
        "task": "apps.news.tasks.cleanup_old_data",
        "schedule": crontab(hour=3, minute=0),
        "options": {"queue": "celery"}
    },
}

# Используем UTC для расписания
app.conf.timezone = "UTC"
app.conf.enable_utc = True

# Хранение состояния расписания (чтобы задачи не запускались дважды при рестарте бит-сервиса)
app.conf.beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")