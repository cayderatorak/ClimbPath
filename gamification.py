from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

import pandas as pd


@dataclass
class GamificationSummary:
    total_xp: int
    current_streak_days: int
    longest_streak_days: int
    level: int
    next_level_xp: int


def _normalize_flight_dates(df: pd.DataFrame) -> list:
    if df.empty or "created_at" not in df.columns:
        return []

    # Convert once and keep only unique calendar dates.
    created = pd.to_datetime(df["created_at"], errors="coerce", utc=True).dropna()
    if created.empty:
        return []

    return sorted(created.dt.date.unique())


def calculate_streaks(dates: Iterable, today: datetime | None = None) -> tuple[int, int]:
    ordered = sorted(set(dates))
    if not ordered:
        return 0, 0

    # Longest streak across all historical training dates.
    longest = 1
    running = 1
    for idx in range(1, len(ordered)):
        if (ordered[idx] - ordered[idx - 1]).days == 1:
            running += 1
            longest = max(longest, running)
        else:
            running = 1

    # Current streak: allow a 1-day gap so users are not punished for rest days/weather.
    current = 1
    for idx in range(len(ordered) - 1, 0, -1):
        if (ordered[idx] - ordered[idx - 1]).days <= 2:
            current += 1
        else:
            break

    if today is not None:
        last_date = ordered[-1]
        if (today.date() - last_date).days > 2:
            current = 0

    return current, longest


def calculate_xp(df: pd.DataFrame) -> int:
    if df.empty:
        return 0

    total_xp = 0
    for _, flight in df.iterrows():
        duration = float(flight.get("total_time", 0) or 0)
        is_solo = bool(flight.get("solo", False))
        is_xc = bool(flight.get("cross_country", False))
        is_night = bool(flight.get("night", False))

        total_xp += int(duration * 10)  # Base XP: 10 per flight hour.
        if is_solo:
            total_xp += 15
        if is_xc:
            total_xp += 10
        if is_night:
            total_xp += 10

    return total_xp


def calculate_level(total_xp: int) -> tuple[int, int]:
    level = (total_xp // 100) + 1
    next_level_xp = level * 100
    return level, next_level_xp


def summarize_gamification(df: pd.DataFrame) -> GamificationSummary:
    total_xp = calculate_xp(df)
    current_streak, longest_streak = calculate_streaks(_normalize_flight_dates(df), today=datetime.utcnow())
    level, next_level_xp = calculate_level(total_xp)
    return GamificationSummary(
        total_xp=total_xp,
        current_streak_days=current_streak,
        longest_streak_days=longest_streak,
        level=level,
        next_level_xp=next_level_xp,
    )
