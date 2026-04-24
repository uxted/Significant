-- =============================================
-- Инициализация БД: расширения и базовые данные
-- =============================================

-- Full-text search для русского языка
CREATE EXTENSION IF NOT EXISTS unaccent;

-- Индекс для full-text search (создаётся после миграций Django)
-- CREATE INDEX idx_news_article_search ON news_article USING gin(to_tsvector('russian', title || ' ' || summary));
