import pandas as pd
import numpy as np


SOLO_HOUR_BASE = 15        # average first solo total hours
SOLO_HOUR_MIN = 10         # realistic early solo
SOLO_HOUR_MAX = 30         # realistic late solo


def _days_since_last_flight(df):
    if df.empty:
        return None
    last = pd.to_datetime(df["created_at"], utc=True, errors="coerce").max()
    if pd.isna(last):
        return None
    return (pd.Timestamp.now(tz="UTC") - last).days


def _avg_flights_per_week(df):
    if df.empty or len(df) < 2:
        return 0
    df = df.copy()
    df["date"] = pd.to_datetime(df["created_at"])
    span_weeks = max((df["date"].max() - df["date"].min()).days / 7, 1)
    return len(df) / span_weeks


def _recency_factor(days_since_last):
    """
    Decay factor based on time off. Flying retains skill non-linearly:
    - 0-7 days off:  no penalty
    - 7-21 days off: slight penalty (need a refresher flight)
    - 21-60 days:    moderate penalty
    - 60+ days:      significant penalty, may need to repeat lessons
    """
    if days_since_last is None:
        return 0.5  # no data, be conservative
    if days_since_last <= 7:
        return 1.0
    if days_since_last <= 21:
        return 0.85
    if days_since_last <= 60:
        return 0.65
    return 0.4


def _frequency_factor(flights_per_week):
    """
    Students flying more frequently retain better and solo sooner.
    Adjusts the target solo hours up or down from the 15hr baseline.
    """
    if flights_per_week >= 3:
        return 0.85   # solo around 12-13 hrs
    if flights_per_week >= 2:
        return 0.93   # solo around 14 hrs
    if flights_per_week >= 1:
        return 1.0    # baseline 15 hrs
    if flights_per_week >= 0.5:
        return 1.15   # solo around 17 hrs
    return 1.3        # infrequent flying, solo around 19-20 hrs


def _confidence_score(df, total_hours, hours_per_week, days_since_last):
    """
    Confidence reflects data quality, not just pace.
    Grows with: number of flights logged, recency, training consistency.
    Shrinks with: very few flights, long gap since last flight, erratic pace.
    """
    if df.empty or len(df) < 2:
        return 15  # almost no data

    flight_count = len(df)
    data_confidence = min(flight_count / 10, 1.0)         # maxes out at 10 flights

    hours_confidence = min(total_hours / SOLO_HOUR_BASE, 1.0)

    recency_conf = _recency_factor(days_since_last)

    pace_confidence = min(hours_per_week / 3, 1.0)

    raw = (
        data_confidence  * 0.35 +
        hours_confidence * 0.30 +
        recency_conf     * 0.20 +
        pace_confidence  * 0.15
    )

    return min(int(raw * 100), 95)  # cap at 95 — never claim certainty


def calculate_solo_readiness(df, required_solo_hours=5):
    solo_hours = df[df["solo"] == True]["total_time"].sum() if not df.empty else 0
    readiness = min(int((solo_hours / required_solo_hours) * 100), 100)
    return readiness


def predict_solo(df, hours_per_week, targets):

    if df.empty:
        total_hours = 0.0
        solo_hours = 0.0
    else:
        total_hours = float(df["total_time"].sum())
        solo_hours = float(df[df["solo"] == True]["total_time"].sum())

    # Already soloed?
    if solo_hours > 0:
        return {
            "predicted_date": None,
            "confidence": 100,
            "hours_remaining": 0,
            "solo_hours_remaining": 0,
            "status": "soloed",
            "note": "First solo completed!"
        }

    days_since_last = _days_since_last_flight(df)
    flights_per_week = _avg_flights_per_week(df)

    # Adjust solo target based on how often they're flying
    freq_factor = _frequency_factor(flights_per_week)
    adjusted_solo_target = round(
        np.clip(SOLO_HOUR_BASE * freq_factor, SOLO_HOUR_MIN, SOLO_HOUR_MAX), 1
    )

    remaining_total = max(adjusted_solo_target - total_hours, 0)

    # Effective pace: discount hours/week by recency
    recency = _recency_factor(days_since_last)
    effective_pace = max(hours_per_week * recency, 0.1)

    weeks_needed = remaining_total / effective_pace
    predicted_date = pd.Timestamp.now() + pd.to_timedelta(int(weeks_needed * 7), unit="d")

    confidence = _confidence_score(df, total_hours, hours_per_week, days_since_last)

    # Human-readable note explaining the estimate
    if days_since_last is not None and days_since_last > 21:
        note = f"Gap of {days_since_last} days since last flight is slowing the estimate."
    elif flights_per_week >= 2:
        note = "Flying frequently — on track for an earlier solo."
    elif flights_per_week < 0.5:
        note = "Flying infrequently — more regular lessons will move this date sooner."
    else:
        note = "Steady pace — keep it up."

    return {
        "predicted_date": predicted_date.date(),
        "confidence": confidence,
        "hours_remaining": round(remaining_total, 1),
        "solo_hours_remaining": round(max(targets["Solo"] - solo_hours, 0), 1),
        "adjusted_solo_target": adjusted_solo_target,
        "effective_pace": round(effective_pace, 2),
        "status": "in_progress",
        "note": note
    }