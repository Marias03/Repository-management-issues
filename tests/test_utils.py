from datetime import datetime, timedelta, timezone
from src.utils import days_since, get_config_path


def test_days_since_today():
    now = datetime.now(timezone.utc)
    assert days_since(now) == 0


def test_days_since_five_days_ago():
    dt = datetime.now(timezone.utc) - timedelta(days=5)
    assert days_since(dt) == 5


def test_get_config_path_returns_correct_suffix():
    path = get_config_path("config/labels.json")
    assert path.endswith("config/labels.json")
