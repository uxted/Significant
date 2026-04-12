# 📊 News Aggregator — Система агрегирования экономически значимых новостей

> **Тема ВКР:** Разработка программного комплекса агрегирования и визуализации экономически значимых новостей на основе методов машинного обучения
>
> **Стек:** Python, Django, React, PostgreSQL, Redis, Celery, RuBERT, Docker

---

## Быстрый запуск

```bash
# 1. Клонировать репозиторий
git clone <repo-url>
cd news-aggregator

# 2. Создать .env файл
cp .env.example .env
# Отредактируйте .env, задав SECRET_KEY и DB_PASSWORD

# 3. Запустить всё одной командой
docker-compose up --build

# 4. Открыть браузер
# Фронтенд:  http://localhost:3000
# API:        http://localhost:8000/api/
# Admin:      http://localhost:8000/admin/
```

---

## Структура проекта

```
news-aggregator/
├── backend/                    # Django + DRF
│   ├── config/                 # Настройки Django (settings, urls, celery)
│   ├── apps/
│   │   ├── users/              # Модель пользователя + аутентификация
│   │   ├── news/               # Модели новостей, категорий, источников
│   │   ├── parsers/            # Celery-задачи парсинга (RSS + BeautifulSoup)
│   │   ├── ml_service/         # ML-классификатор (RuBERT + fallback)
│   │   └── api/                # REST API endpoints (DRF)
│   ├── tests/
│   │   ├── unit/               # Unit-тесты (pytest)
│   │   ├── integration/        # Integration-тесты (полный цикл парсинга)
│   │   └── load/               # Нагрузочные тесты (Locust)
│   └── requirements.txt
├── frontend/                   # React
│   ├── src/
│   │   ├── components/         # UI-компоненты
│   │   │   ├── Header/         # Шапка с навигацией
│   │   │   ├── Dashboard/      # Главная страница (лента + сводка)
│   │   │   ├── NewsCard/       # Карточка новости с цветовой маркировкой
│   │   │   ├── NewsFeed/       # Лента новостей
│   │   │   ├── NewsDetail/     # Детальный просмотр
│   │   │   ├── Filters/        # Панель фильтров
│   │   │   ├── LoginForm/      # Форма входа
│   │   │   ├── Bookmarks/      # Закладки
│   │   │   ├── Subscriptions/  # Подписки на категории/тикеры
│   │   │   └── Privacy/        # Политика конфиденциальности
│   │   ├── hooks/              # React hooks (useAuth, useNewsFeed)
│   │   ├── services/           # API клиент (axios + JWT)
│   │   ├── context/            # Auth context
│   │   ├── styles/             # Глобальные CSS
│   │   └── __tests__/          # Unit-тесты (Jest)
│   └── package.json
├── ml/                         # ML-модуль
│   ├── models/                 # Сохранённые модели (RuBERT)
│   ├── data/datasets/          # Обучающие выборки (CSV)
│   ├── scripts/train.py        # Скрипт обучения RuBERT
│   ├── tests/test_metrics.py   # Проверка метрик (Precision/Recall/F1)
│   └── requirements.txt
├── tests/
│   ├── playwright/             # E2E-тесты (Playwright)
│   └── load/                   # Нагрузочные тесты
├── nginx/                      # Nginx конфигурация
├── config/                     # Конфигурация (init.sql)
├── .github/workflows/ci.yml    # GitHub Actions CI pipeline
├── docker-compose.yml          # Оркестрация (7 контейнеров)
├── Dockerfile.web              # Backend Docker
├── Dockerfile.frontend         # Frontend Docker
├── .env.example                # Шаблон переменных окружения
├── .gitignore
├── spec.md                     # Спецификация требований
└── README.md
```

---

## Архитектура

```
  Источники (RSS/Web) ──▶ Celery Worker ──▶ PostgreSQL
                              │
                              ▼
                         RuBERT (ML)
                              │
                              ▼
  Пользователь (React) ◀── Django REST API ◀── Redis (кэш)
         │
         └── Polling (30 сек)
```

### Контейнеры Docker

| Контейнер | Назначение |
|-----------|-----------|
| `db` | PostgreSQL 14 — основная БД |
| `cache` | Redis 7 — кэш + broker Celery |
| `web` | Django + Gunicorn — REST API |
| `worker` | Celery Worker — парсинг + ML |
| `beat` | Celery Beat — расписание задач |
| `frontend` | React — веб-интерфейс |
| `nginx` | Reverse proxy + статика |

---

## API Endpoints

| Endpoint | Метод | Описание | Доступ |
|----------|-------|----------|--------|
| `POST /api/auth/login/` | POST | Вход (JWT) | Публичный |
| `POST /api/auth/refresh/` | POST | Обновление токена | Публичный |
| `GET /api/news/` | GET | Лента новостей (фильтры, поиск) | Публичный |
| `GET /api/news/{id}/` | GET | Детальная новость | Публичный |
| `GET /api/sources/` | GET | Список источников | Публичный |
| `GET /api/categories/` | GET | Список категорий | Публичный |
| `GET/PUT /api/user/subscriptions/` | GET/PUT | Подписки | Auth |
| `GET/POST /api/user/bookmarks/` | GET/POST | Закладки | Auth |
| `GET /api/admin/sources/` | GET | Управление источниками | Admin |
| `GET /api/admin/moderation/` | GET | Модерация новостей | Admin |

---

## ML-модель

| Параметр | Значение |
|----------|----------|
| **Архитектура** | RuBERT fine-tuned (binary classification) |
| **Fallback** | TF-IDF + Logistic Regression |
| **Датасет** | 5000 новостей (2500 значимых / 2500 не значимых) |
| **Метрики** | Precision ≥80%, Recall ≥75%, F1 ≥0.77 |
| **Время инференса** | ≤0.5 сек на новость |
| **Полный цикл** | ≤1 секунды |

### Обучение модели

```bash
# Внутри контейнера web/worker
python ml/scripts/train.py --dataset ml/data/datasets/news_dataset.csv --epochs 3
```

---

## Тестирование

```bash
# Backend (pytest)
cd backend
pytest --cov=. --cov-report=term-missing

# Frontend (Jest)
cd frontend
npm test -- --coverage

# E2E (Playwright)
npx playwright test

# Нагрузочное (Locust)
cd backend/tests/load
locust -f locustfile.py --host=http://localhost:8000
```

---

## Пользователи по умолчанию

| Роль | Email | Пароль |
|------|-------|--------|
| Admin | admin@test.com | adminpassword123 |
| User | test@test.com | testpassword123 |

---

## Переменные окружения (.env)

```bash
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=news_aggregator
DB_PASSWORD=your-db-password
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=10080
```

---

## Чек-лист безопасности

- ✅ Пароли: PBKDF2 (SHA256, 600 000 итераций)
- ✅ JWT: access 15 мин + refresh 7 дней
- ✅ Rate limiting: 100 запросов/мин (пользователь)
- ✅ Audit log действий администратора
- ✅ `.env` не коммитится в Git
- ✅ Django ORM — защита от SQL-инъекций
- ✅ React экранирует вывод — защита от XSS

---

## Лицензия

Учебный проект для ВКР.
