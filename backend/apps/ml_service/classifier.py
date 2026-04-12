"""ML classifier service."""

import time
import logging
from django.conf import settings
from pathlib import Path

logger = logging.getLogger("ml.classifier")

# Global model instance (loaded once at startup)
_model = None
_fallback_model = None


def _load_model():
    """Load RuBERT model."""
    global _model
    if _model is not None:
        return _model

    try:
        import tensorflow as tf
        model_path = Path(settings.ML_MODEL_PATH)
        if model_path.exists():
            _model = tf.saved_model.load(str(model_path))
            logger.info(f"RuBERT model loaded from {model_path}")
        else:
            logger.warning(f"Model not found at {model_path}, using fallback")
            _load_fallback()
    except Exception as e:
        logger.error(f"Failed to load RuBERT model: {e}")
        _load_fallback()

    return _model


def _load_fallback():
    """Load fallback TF-IDF + Logistic Regression model."""
    global _fallback_model
    try:
        import joblib
        fallback_path = Path(settings.ML_MODEL_PATH).parent / "fallback_model.pkl"
        if fallback_path.exists():
            _fallback_model = joblib.load(str(fallback_path))
            logger.info("Fallback model (TF-IDF + LR) loaded")
    except Exception as e:
        logger.error(f"Failed to load fallback model: {e}")


def classify_article(title: str, summary: str = "") -> tuple:
    """
    Classify a news article.

    Returns:
        (is_significant: bool, confidence: float)
    """
    global _model
    text = f"{title} {summary}".strip()

    start_time = time.time()

    try:
        model = _load_model()
        if model is not None and hasattr(model, "signatures"):
            # TensorFlow SavedModel
            result = model.signatures["serving_default"](
                tf.constant([text])
            )
            confidence = float(result["output_0"][0][1])  # probability of class 1
            is_significant = confidence >= 0.5
        elif _fallback_model is not None:
            # Fallback: TF-IDF + LR
            import joblib
            vectorizer_path = Path(settings.ML_MODEL_PATH).parent / "vectorizer.pkl"
            vectorizer = joblib.load(str(vectorizer_path))
            text_vec = vectorizer.transform([text])
            confidence = float(_fallback_model.predict_proba(text_vec)[0][1])
            is_significant = confidence >= 0.5
        else:
            # No model available — default to non-significant
            logger.warning("No ML model available, defaulting to non-significant")
            is_significant = False
            confidence = 0.0

    except Exception as e:
        logger.error(f"Classification error: {e}")
        is_significant = False
        confidence = 0.0

    duration = time.time() - start_time
    logger.info(
        f"Classification completed in {duration:.3f}s, "
        f"significant={is_significant}, confidence={confidence:.3f}"
    )

    return is_significant, confidence


def assign_significance_level(
    confidence: float, source_tier: int, title: str, summary: str
) -> str:
    """
    Assign H/M/L level based on confidence, source tier, and content rules.

    Rules:
    - HIGH: ЦБ решения, санкции против системообразующих, отчётность >150 млрд
    - MEDIUM: отчётность средних, кадровые назначения
    - LOW: локальные события, малые компании
    """
    text = f"{title} {summary}".lower()

    # High significance keywords
    high_keywords = [
        "ключевая ставка", "цб росс", "повысил ставку", "понизил ставку",
        "санкции против", "дефолт", "остановк торгов",
    ]
    for kw in high_keywords:
        if kw in text:
            return "HIGH"

    # Source tier influence
    if source_tier == 1:
        # Regulator sources — auto-high for significant news
        if confidence >= 0.7:
            return "HIGH"

    # Medium significance
    medium_keywords = [
        "отчёт", "выручк", "прибыл", "дивиденд", "назнач", "ceo",
    ]
    for kw in medium_keywords:
        if kw in text:
            return "MEDIUM"

    # Default based on confidence
    if confidence >= 0.8:
        return "HIGH"
    elif confidence >= 0.6:
        return "MEDIUM"
    else:
        return "LOW"


# Import tensorflow lazily
import tensorflow as tf
