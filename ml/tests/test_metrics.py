"""ML model metrics tests."""

import pytest
import json
import os

METRICS_FILE = os.path.join(os.path.dirname(__file__), "..", "metrics", "report.json")


@pytest.mark.skipif(not os.path.exists(METRICS_FILE), reason="Metrics report not found")
def test_precision_threshold():
    """Precision must be >= 80%."""
    with open(METRICS_FILE) as f:
        metrics = json.load(f)
    assert metrics["precision"] >= 0.80, f"Precision {metrics['precision']:.3f} < 0.80"


@pytest.mark.skipif(not os.path.exists(METRICS_FILE), reason="Metrics report not found")
def test_recall_threshold():
    """Recall must be >= 75%."""
    with open(METRICS_FILE) as f:
        metrics = json.load(f)
    assert metrics["recall"] >= 0.75, f"Recall {metrics['recall']:.3f} < 0.75"


@pytest.mark.skipif(not os.path.exists(METRICS_FILE), reason="Metrics report not found")
def test_f1_score():
    """F1-score must be >= 0.77."""
    with open(METRICS_FILE) as f:
        metrics = json.load(f)
    assert metrics["f1"] >= 0.77, f"F1 {metrics['f1']:.3f} < 0.77"
