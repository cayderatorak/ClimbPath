import pandas as pd

# ------------------ SOLO READINESS ------------------
def calculate_solo_readiness(df, required_solo_hours=5):

    if df.empty:
        return 0

    solo_hours = df[df["solo"] == True]["total_time"].sum()

    readiness = min(int((solo_hours / required_solo_hours) * 100), 100)

    return readiness


# ------------------ SOLO PREDICTION + CONFIDENCE ------------------
def predict_solo(df, hours_per_week, targets):

    if df.empty:
        return "Not enough data", 0

    df = df.copy()
    df["date"] = pd.to_datetime(df["created_at"])

    total_hours = df["total_time"].sum()
    solo_target = targets.get("Solo", 15)

    remaining = max(solo_target - total_hours, 0)

    training_days = (df["date"].max() - df["date"].min()).days
    training_weeks = max(training_days / 7, 1)

    actual_rate = total_hours / training_weeks
    effective_rate = max(hours_per_week, actual_rate, 0.5)

    weeks_needed = remaining / effective_rate

    predicted_date = pd.Timestamp.now() + pd.to_timedelta(int(weeks_needed * 7), unit="d")

    # -------- CONFIDENCE SCORE --------
    flights = len(df)

    consistency = min(actual_rate / hours_per_week, 1) if hours_per_week else 0

    confidence = min(int((flights / 20) * 50 + consistency * 50), 95)

    return predicted_date.strftime("%b %d, %Y"), confidence