# solo.py
import pandas as pd


def calculate_solo_readiness(df, required_solo_hours=5):

    solo_hours = df[df["solo"] == True]["total_time"].sum() if not df.empty else 0

    readiness = min(int((solo_hours / required_solo_hours) * 100), 100)

    return readiness


def predict_solo(df, hours_per_week, targets):

    if df.empty:
        total_hours = 0
        solo_hours = 0
    else:
        total_hours = df["total_time"].sum()
        solo_hours = df[df["solo"] == True]["total_time"].sum()

    remaining_solo = max(targets["Solo"] - solo_hours, 0)

    # typical first solo happens around 15 hours
    SOLO_TARGET_TOTAL = 15
    remaining_total = max(SOLO_TARGET_TOTAL - total_hours, 0)

    weeks_needed = remaining_total / max(hours_per_week, 1)

    predicted_date = pd.Timestamp.now() + pd.to_timedelta(int(weeks_needed * 7), unit="d")

    confidence = min(int((hours_per_week / 3) * 100), 100)

    return {
        "predicted_date": predicted_date.date(),
        "confidence": confidence,
        "hours_remaining": round(remaining_total, 1),
        "solo_hours_remaining": round(remaining_solo, 1)
    }