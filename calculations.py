import pandas as pd

def calculate_totals(df):
    totals = {
        "Dual": df[df["solo"]==False]["total_time"].sum() if not df.empty else 0,
        "Solo": df[df["solo"]==True]["total_time"].sum() if not df.empty else 0,
        "XC": df[df.get("cross_country", False)]["total_time"].sum() if not df.empty else 0,
        "Night": df[df.get("night", False)]["total_time"].sum() if not df.empty else 0,
    }

    totals["Total"] = sum([totals[k] for k in ["Dual","Solo","XC","Night"]])
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

    hours_per_week = calculate_training_pace(df)  # df = your flight log dataframe

    hours_per_week = total_hours / weeks_training

    return round(hours_per_week, 2)

def estimate_remaining_cost(
    totals,
    requirements,
    hours_per_week,
    cost_per_hour=180
    ):
    """
    Smarter training cost estimator based on pace + realistic completion hours.
    """

    current_hours = totals.get("Total", 0)

    # --- Realistic baseline instead of FAA minimum ---
    base_required_hours = 65  # average real-world PPL completion

    # --- Adjust based on training pace ---
    if hours_per_week >= 4:
        pace_factor = 0.9   # very efficient training
    elif hours_per_week >= 2:
        pace_factor = 1.0   # normal pace
    elif hours_per_week >= 1:
        pace_factor = 1.15  # slower → more review flights
    else:
        pace_factor = 1.3   # very slow → lots of repetition

    adjusted_required_hours = base_required_hours * pace_factor

    # --- Remaining hours ---
    remaining_hours = max(0, adjusted_required_hours - current_hours)

    # --- Cost estimate ---
    estimated_cost = remaining_hours * cost_per_hour

    return {
        "adjusted_required_hours": round(adjusted_required_hours, 1),
        "remaining_hours": round(remaining_hours, 1),
        "estimated_cost": round(estimated_cost, 0),
        "pace_factor": pace_factor
    }