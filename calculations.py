import pandas as pd
# calculations.py

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


# --- NEW FEATURE: Checkride Readiness ---
def checkride_readiness(totals, requirements):

    scores = []

    # category progress
    for category in ["Dual", "Solo", "XC", "Night"]:
        progress = min(totals.get(category, 0) / requirements.get(category, 1), 1)
        scores.append(progress)

    # total hours progress
    total_progress = min(totals.get("Total", 0) / requirements.get("Total", 1), 1)
    scores.append(total_progress)

    readiness_score = sum(scores) / len(scores)

    return round(readiness_score * 100, 1)


# --- OPTIONAL: Remaining Hours ---
def hours_remaining(totals, requirements):

    remaining = {}

    for key in requirements:
        remaining[key] = max(0, requirements[key] - totals.get(key, 0))

    return remaining


    # calculations.py

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