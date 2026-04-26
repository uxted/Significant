import random
import hashlib
import logging
from datetime import timedelta
from typing import Optional, Dict, Any

import requests
from bs4 import BeautifulSoup, Comment
from django.utils import timezone

logger = logging.getLogger(__name__)

# Список User-Agent для ротации
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
]

def get_random_user_agent() -> str:
    """Возвращает случайный User-Agent."""
    return random.choice(USER_AGENTS)

def fetch_url(url: str, timeout: int = 10) -> Optional[str]:
    """
    Выполняет HTTP GET запрос с ротацией User-Agent и таймаутом.
    Возвращает содержимое ответа или None при ошибке.
    """
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        # Попытка определить кодировку
        if response.encoding is None or response.encoding == 'ISO-8859-1':
            # Часто серверы отдают неверную кодировку по умолчанию, пробуем угадать
            response.encoding = response.apparent_encoding

        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Неожиданная ошибка при запросе {url}: {e}")
        return None

def clean_html(html_content: str) -> str:
    """
    Очищает HTML от скриптов, стилей, комментариев и навигационных элементов.
    Возвращает текстовое содержимое.
    """
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, 'html.parser')

    # Удаляем скрипты, стили, комментарии
    for tag in soup(['script', 'style', 'comment', 'noscript']):
        tag.decompose()

    # Удаляем часто встречающиеся блоки рекламы и навигации (по классам/id)
    # Это упрощенная эвристика, можно расширять
    unwanted_tags = soup.find_all(attrs={"class": lambda x: x and any(word in x for word in ['ad', 'banner', 'sidebar', 'nav', 'footer', 'header'])})
    for tag in unwanted_tags:
        tag.decompose()

    # Получаем текст и очищаем от лишних пробелов
    text = soup.get_text(separator=' ', strip=True)

    # Нормализация пробелов
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)

    return text

def calculate_title_hash(title: str) -> str:
    """Вычисляет SHA256 хеш от заголовка новости."""
    if not title:
        return ""
    # Нормализуем заголовок перед хешированием (убираем лишние пробелы, приводим к нижнему регистру для устойчивости)
    normalized_title = " ".join(title.lower().split())
    return hashlib.sha256(normalized_title.encode('utf-8')).hexdigest()

def detect_encoding_fallback(content: bytes) -> str:
    """Пытается определить кодировку для байтового контента."""
    # Простая эвристика для常见 кириллических кодировок
    # В реальном проекте лучше использовать chardet
    try:
        content.decode('utf-8')
        return 'utf-8'
    except UnicodeDecodeError:
        pass

    try:
        content.decode('windows-1251')
        return 'windows-1251'
    except UnicodeDecodeError:
        pass

    return 'utf-8' # По умолчанию