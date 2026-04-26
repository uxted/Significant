"""
Rule-based фильтрация новостей.

Реализует 5 типов правил для отсеивания 60-70% новостей:
1. Проверка источника (Tier 1-4)
2. Ключевые слова значимых событий
3. Отсечение незначимых тем
4. Проверка типа контента
5. Количественные пороги
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# === КОНФИГУРАЦИЯ ПРАВИЛ ===

# 1. Ключевые слова значимых событий (позитивный фильтр)
SIGNIFICANT_KEYWORDS = [
    "ключевая ставка", "санкции", "инфляция", "ВВП", "безработица",
    "курс рубля", "дефолт", "кризис", "рецессия", "прогноз",
    "бюджет", "налоги", "НДС", "НДФЛ", "пошлины", "тарифы",
    "ЦБ РФ", "Банк России", "Минфин", "Правительство", "Федеральная резервная система",
    "IPO", "слияние", "поглощение", "банкротство", "реструктуризация",
    "дивиденды", "эмиссия", "облигации", "ОФЗ", "еврооблигации",
    "золотовалютные резервы", "фонд национального благосостояния", "ФНБ",
    "торговый баланс", "платежный баланс", "валютные интервенции",
    "ипотека", "рефинансирование", "кредитная ставка", "депозит",
    "акцизы", "субсидии", "дотации", "госзаказ", "тендер",
    "экспорт", "импорт", "таможенные пошлины", "квоты",
    "нефть", "газ", "энергоносители", "урожай", "продовольствие",
    "фондовый рынок", "биржа", "индекс Мосбиржи", "RTS",
    "корпоративные действия", "сплит", "консолидация", "байбэк"
]

# 2. Стоп-слова незначимых тем (негативный фильтр)
STOP_TOPICS = [
    "спорт", "футбол", "хоккей", "олимпиада", "чемпионат",
    "шоу-бизнес", "кино", "музыка", "актер", "певица", "концерт",
    "погода", "прогноз погоды", "температура", "осадки", "шторм",
    "гороскоп", "астролог", "знак зодиака",
    "рецепт", "кулинария", "еда", "ресторан", "кафе",
    "мода", "стиль", "дизайнер", "показ мод",
    "путешествия", "туризм", "отпуск", "курорт", "отель",
    "здоровье", "медицина", "болезнь", "лекарство", "врач", # Оставляем только если связано с экономикой
    "происшествия", "ДТП", "пожар", "криминал", "убийство",
    "скандал", "сплетни", "светская хроника",
    "конкурс", "фестиваль", "выставка", "премьера",
    "некролог", "смерть", "похороны"
]

# 3. Маркеры типов контента
PRESS_RELEASE_MARKERS = [
    "пресс-релиз", "официальное сообщение", "заявление",
    "сообщает пресс-служба", "по данным компании", "представитель заявил",
    "отчет", "финансовый отчет", "квартальный отчет", "годовой отчет",
    "раскрытие информации", "существенный факт", "инсайдерская информация"
]

RUMOR_MARKERS = [
    "слухи", "по неподтвержденным данным", "источник сообщил",
    "как сообщают", "возможно", "вероятно", "может быть",
    "по некоторым данным", "ходят слухи", "инсайд",
    "неофициально", "анонимный источник", "источник близкий к"
]

# 4. Пороговые значения для количественных фильтров
THRESHOLDS = {
    "revenue_min": 75_000_000_000,  # 75 млрд руб
    "assets_min": 150_000_000_000,   # 150 млрд руб
    "market_cap_min": 50_000_000_000, # 50 млрд руб
    "employees_min": 1000            # 1000 сотрудников
}

# Паттерны для извлечения чисел из текста
NUMBER_PATTERNS = [
    r'(\d+[.,]?\d*)\s*(млрд|млн|тыс\.?|billion|million)',
    r'(\d+[.,]?\d*)\s*(рублей?|руб\.?|долларов?|\$|euro|€)',
    r'выручка\s*[:\-]?\s*(\d+[.,]?\d*)',
    r'прибыль\s*[:\-]?\s*(\d+[.,]?\d*)',
    r'активы\s*[:\-]?\s*(\d+[.,]?\d*)',
    r'капитализация\s*[:\-]?\s*(\d+[.,]?\d*)'
]


def check_source_tier(source_tier: int) -> bool:
    """
    Правило 1: Проверка уровня доверия источника.
    Tier 1 (официальные) - всегда проходят.
    Tier 2 (агентства) - проходят.
    Tier 3 (деловые СМИ) - проходят.
    Tier 4 (прочие) - требуют дополнительной проверки.

    Возвращает True, если источник допустим.
    """
    if source_tier in [1, 2, 3]:
        return True
    elif source_tier == 4:
        # Источники Tier 4 требуют более строгой фильтрации по другим правилам
        return True  # Но не отфильтровываем полностью, просто помечаем
    else:
        logger.warning(f"Неизвестный уровень источника: {source_tier}")
        return False


def check_significant_keywords(text: str) -> Tuple[bool, List[str]]:
    """
    Правило 2: Проверка наличия ключевых слов значимых событий.

    Возвращает кортеж (проходит ли фильтр, список найденных ключевых слов).
    """
    if not text:
        return False, []

    text_lower = text.lower()
    found_keywords = []

    for keyword in SIGNIFICANT_KEYWORDS:
        if keyword in text_lower:
            found_keywords.append(keyword)

    has_significant = len(found_keywords) > 0
    return has_significant, found_keywords


def check_stop_topics(text: str) -> Tuple[bool, List[str]]:
    """
    Правило 3: Проверка на наличие незначимых тем.

    Возвращает кортеж (проходит ли фильтр, список найденных стоп-тем).
    Если найдена стоп-тема, новость отфильтровывается.
    """
    if not text:
        return True, []  # Если текста нет, не фильтруем по этому правилу

    text_lower = text.lower()
    found_topics = []

    for topic in STOP_TOPICS:
        # Используем границы слов для более точного поиска
        pattern = r'\b' + re.escape(topic) + r'\b'
        if re.search(pattern, text_lower):
            found_topics.append(topic)

    # Если найдены стоп-темы, но также есть значимые экономические термины,
    # можно пропустить новость (например, "экономический форум по спорту")
    if found_topics:
        has_economic_context, _ = check_significant_keywords(text)
        if has_economic_context:
            # Контекст экономический, пропускаем несмотря на стоп-слова
            return True, []
        return False, found_topics

    return True, []


def check_content_type(text: str) -> Tuple[str, float]:
    """
    Правило 4: Определение типа контента.

    Возвращает кортеж (тип контента, уверенность):
    - "press_release" (пресс-релиз) - высокая достоверность
    - "rumor" (слухи) - низкая достоверность
    - "news" (новость) - средняя достоверность
    - "unknown" (неизвестно)

    Уверенность от 0.0 до 1.0.
    """
    if not text:
        return "unknown", 0.0

    text_lower = text.lower()

    press_release_score = sum(1 for marker in PRESS_RELEASE_MARKERS if marker in text_lower)
    rumor_score = sum(1 for marker in RUMOR_MARKERS if marker in text_lower)

    if press_release_score >= 2:
        return "press_release", min(1.0, 0.5 + press_release_score * 0.1)
    elif rumor_score >= 2:
        return "rumor", min(1.0, 0.5 + rumor_score * 0.1)
    elif press_release_score == 1 and rumor_score == 0:
        return "press_release", 0.6
    elif rumor_score == 1 and press_release_score == 0:
        return "rumor", 0.6
    else:
        return "news", 0.5


def extract_numbers_from_text(text: str) -> Dict[str, float]:
    """
    Извлекает числовые значения из текста.

    Возвращает словарь с найденными величинами:
    {
        'revenue': значение в рублях,
        'profit': значение в рублях,
        'assets': значение в рублях,
        'market_cap': значение в рублях,
        'employees': количество сотрудников
    }
    """
    result = {
        'revenue': 0.0,
        'profit': 0.0,
        'assets': 0.0,
        'market_cap': 0.0,
        'employees': 0
    }

    if not text:
        return result

    text_lower = text.lower()

    # Простая эвристика для извлечения чисел
    # В реальном проекте лучше использовать NER модели

    for pattern in NUMBER_PATTERNS:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            try:
                if isinstance(match, tuple):
                    number_str, unit = match
                else:
                    number_str = match
                    unit = ""

                # Нормализация числа
                number_str = number_str.replace(',', '.')
                number = float(number_str)

                # Определение множителя
                multiplier = 1.0
                if 'млрд' in unit or 'billion' in unit:
                    multiplier = 1_000_000_000
                elif 'млн' in unit or 'million' in unit:
                    multiplier = 1_000_000
                elif 'тыс' in unit:
                    multiplier = 1_000

                value = number * multiplier

                # Попытка определить категорию по контексту
                if 'выручк' in text_lower[max(0, text_lower.find(number_str)-20):text_lower.find(number_str)+20]:
                    result['revenue'] = max(result['revenue'], value)
                elif 'прибыл' in text_lower[max(0, text_lower.find(number_str)-20):text_lower.find(number_str)+20]:
                    result['profit'] = max(result['profit'], value)
                elif 'актив' in text_lower[max(0, text_lower.find(number_str)-20):text_lower.find(number_str)+20]:
                    result['assets'] = max(result['assets'], value)
                elif 'капитализаци' in text_lower[max(0, text_lower.find(number_str)-20):text_lower.find(number_str)+20]:
                    result['market_cap'] = max(result['market_cap'], value)

            except (ValueError, IndexError):
                continue

    # Поиск количества сотрудников
    emp_pattern = r'(\d+)\s*(сотрудников?|человек|штат)'
    emp_matches = re.findall(emp_pattern, text_lower)
    if emp_matches:
        try:
            result['employees'] = int(emp_matches[0][0])
        except (ValueError, IndexError):
            pass

    return result


def check_quantitative_thresholds(numbers: Dict[str, float]) -> Tuple[bool, Dict[str, bool]]:
    """
    Правило 5: Проверка количественных порогов.

    Возвращает кортеж (проходит ли фильтр, детали по каждому порогу).
    """
    details = {
        'revenue_check': numbers.get('revenue', 0) >= THRESHOLDS['revenue_min'],
        'assets_check': numbers.get('assets', 0) >= THRESHOLDS['assets_min'],
        'market_cap_check': numbers.get('market_cap', 0) >= THRESHOLDS['market_cap_min'],
        'employees_check': numbers.get('employees', 0) >= THRESHOLDS['employees_min']
    }

    # Новость проходит, если хотя бы один порог превышен
    passed = any(details.values())

    return passed, details


def filter_news(
    title: str,
    description: str,
    content: str = "",
    source_tier: int = 3
) -> Dict[str, Any]:
    """
    Основная функция фильтрации новости.

    Применяет все 5 правил и возвращает результат фильтрации.

    Args:
        title: Заголовок новости
        description: Описание/анонс
        content: Полный текст новости (если доступен)
        source_tier: Уровень доверия источника (1-4)

    Returns:
        Словарь с результатами фильтрации:
        {
            'passed': bool,  # Прошла ли новость фильтр
            'reason': str,   # Причина отклонения (если отклонена)
            'score': float,  # Общий скор релевантности (0.0-1.0)
            'details': {     # Детали по каждому правилу
                'source_ok': bool,
                'keywords': list,
                'stop_topics': list,
                'content_type': str,
                'content_confidence': float,
                'numbers': dict,
                'thresholds': dict
            }
        }
    """
    full_text = f"{title} {description} {content}".strip()

    result = {
        'passed': True,
        'reason': '',
        'score': 0.0,
        'details': {}
    }

    # Правило 1: Проверка источника
    source_ok = check_source_tier(source_tier)
    result['details']['source_ok'] = source_ok
    if not source_ok:
        result['passed'] = False
        result['reason'] = 'Недоверенный источник'
        return result

    # Правило 2: Ключевые слова
    has_keywords, keywords = check_significant_keywords(full_text)
    result['details']['keywords'] = keywords

    # Правило 3: Стоп-темы
    topics_ok, stop_topics = check_stop_topics(full_text)
    result['details']['stop_topics'] = stop_topics
    if not topics_ok:
        result['passed'] = False
        result['reason'] = f'Незначимая тема: {", ".join(stop_topics)}'
        return result

    # Если нет значимых ключевых слов, снижаем приоритет
    if not has_keywords:
        # Для источников Tier 4 отсутствие ключевых слов критично
        if source_tier == 4:
            result['passed'] = False
            result['reason'] = 'Отсутствие значимых ключевых слов для источника Tier 4'
            return result

    # Правило 4: Тип контента
    content_type, confidence = check_content_type(full_text)
    result['details']['content_type'] = content_type
    result['details']['content_confidence'] = confidence

    # Слухи с низкой уверенностью от источников Tier 4 отфильтровываем
    if content_type == 'rumor' and confidence > 0.7 and source_tier == 4:
        result['passed'] = False
        result['reason'] = 'Неподтвержденные слухи от ненадежного источника'
        return result

    # Правило 5: Количественные пороги
    numbers = extract_numbers_from_text(full_text)
    thresholds_passed, threshold_details = check_quantitative_thresholds(numbers)
    result['details']['numbers'] = numbers
    result['details']['thresholds'] = threshold_details

    # Расчет общего скоринга
    score = 0.5  # Базовый скор

    if has_keywords:
        score += min(0.3, len(keywords) * 0.05)  # До +0.3 за ключевые слова

    if content_type == 'press_release':
        score += 0.1  # Пресс-релизы чуть важнее
    elif content_type == 'rumor':
        score -= 0.2  # Слухи менее важны

    if thresholds_passed:
        score += 0.1  # Крупные цифры добавляют важности

    # Источники Tier 1 и 2 получают небольшой буст
    if source_tier in [1, 2]:
        score += 0.05

    result['score'] = min(1.0, max(0.0, score))

    # Финальное решение
    if result['score'] < 0.4:
        result['passed'] = False
        result['reason'] = f'Низкий скор релевантности: {result["score"]:.2f}'

    return result