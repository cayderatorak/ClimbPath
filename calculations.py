import pandas as pd

def _boolean_mask(df, column_name, default=False):
    if column_name not in df.columns:
        return pd.Series(default, index=df.index, dtype=bool)
    return df[column_name].fillna(default).astype(bool)


def calculate_totals(df):
    if df.empty:
        return {"Dual": 0, "Solo": 0, "XC": 0, "Night": 0, "Total": 0}, df

    total_time = pd.to_numeric(df.get("total_time", 0), errors="coerce").fillna(0)
    solo_mask = _boolean_mask(df, "solo")
    xc_mask = _boolean_mask(df, "cross_country")
    night_mask = _boolean_mask(df, "night")

    totals = {
        "Dual": total_time[~solo_mask].sum(),
        "Solo": total_time[solo_mask].sum(),
        "XC": total_time[xc_mask].sum(),
        "Night": total_time[night_mask].sum(),
    }

    totals["Total"] = total_time.sum()
    return totals, df


def calculate_flight_cost(duration, aircraft_rate, instructor_rate):
    return duration * (aircraft_rate + instructor_rate)


def checkride_readiness(totals, requirements):

    scores = []

    for category in ["Dual", "Solo", "XC", "Night"]:
        progress = min(totals.get(category, 0) / requirements.get(category, 1), 1)
        scores.append(progress)

    total_progress = min(totals.get("Total", 0) / requirements.get("Total", 1), 1)
    scores.append(total_progress)

    readiness_score = sum(scores) / len(scores)

    return round(readiness_score * 100, 1)


def hours_remaining(totals, requirements):

    remaining = {}

    for key in requirements:
        remaining[key] = max(0, requirements[key] - totals.get(key, 0))

    return remaining


def calculate_training_pace(df):

    if df.empty:
        return 0

    df["date"] = pd.to_datetime(df["date"])

    first_flight = df["date"].min()
    last_flight = df["date"].max()

    weeks_training = max((last_flight - first_flight).days / 7, 1)

    total_hours = df["total_time"].sum()


    hours_per_week = total_hours / weeks_training

    return round(hours_per_week, 2)

def estimate_remaining_cost(
    totals,
    requirements,
    hours_per_week,
    cost_per_hour=180,
    proficiency_score=50,
    consistency_score=50,
    ):
    """
    Smarter training cost estimator based on pace, consistency, and proficiency.
    """

    current_hours = totals.get("Total", 0)
    required_total = requirements.get("Total", 0) if requirements else 0
    # Use a realistic training completion floor while respecting track targets.
    base_required_hours = max(required_total, 65)

    # --- Adjust based on training pace ---
    if hours_per_week >= 4:
        pace_factor = 0.9   # very efficient training
    elif hours_per_week >= 2:
        pace_factor = 1.0   # normal pace
    elif hours_per_week >= 1:
        pace_factor = 1.15  # slower → more review flights
    else:
        pace_factor = 1.3   # very slow → lots of repetition

    # Better proficiency lowers likely repeat/review hours.
    bounded_proficiency = min(max(float(proficiency_score or 0), 0.0), 100.0)
    proficiency_factor = 1.2 - (bounded_proficiency / 100.0) * 0.35  # 1.20 -> 0.85

    # Better consistency lowers likely relearning overhead.
    bounded_consistency = min(max(float(consistency_score or 0), 0.0), 100.0)
    consistency_factor = 1.2 - (bounded_consistency / 100.0) * 0.35  # 1.20 -> 0.85

    adjusted_required_hours = (
        base_required_hours
        * pace_factor
        * proficiency_factor
        * consistency_factor
    )

    # --- Remaining hours ---
    remaining_hours = max(0, adjusted_required_hours - current_hours)

    # --- Cost estimate ---
    estimated_cost = remaining_hours * cost_per_hour

    return {
        "adjusted_required_hours": round(adjusted_required_hours, 1),
        "remaining_hours": round(remaining_hours, 1),
        "estimated_cost": round(estimated_cost, 0),
        "pace_factor": pace_factor,
        "proficiency_factor": round(proficiency_factor, 3),
        "consistency_factor": round(consistency_factor, 3),
    }