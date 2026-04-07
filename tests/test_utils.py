from datetime import datetime, timezone, timedelta

from src.utils import days_since


def test_days_since_handles_aware_datetime():
    dt = datetime.now(timezone.utc) - timedelta(days=3, hours=1)
    assert days_since(dt) >= 3


def test_days_since_handles_naive_datetime():
    dt = (datetime.now(timezone.utc) - timedelta(days=2)).replace(tzinfo=None)
    assert days_since(dt) >= 2
