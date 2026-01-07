from datetime import datetime

def calculate_sleep_minutes(start: datetime, end: datetime) -> int:
    """
    Handles cross-midnight sleep automatically
    """
    diff = end - start
    minutes = int(diff.total_seconds() // 60)

    if minutes <= 0:
        raise ValueError("End time must be after start time")

    return minutes
