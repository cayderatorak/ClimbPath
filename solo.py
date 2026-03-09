import pandas as pd
# Calculate solo readiness as percentage of required solo hours
def calculate_solo_readiness(df, required_solo_hours=5):
    solo_hours = df[df["solo"]==True]["total_time"].sum() if not df.empty else 0
    readiness = min(int((solo_hours / required_solo_hours) * 100), 100)
    return readiness

# Predict when student will reach solo readiness
def predict_solo(df, hours_per_week, targets):
    solo_hours = df[df["solo"]==True]["total_time"].sum() if not df.empty else 0
    remaining = max(targets["Solo"] - solo_hours, 0)
    weeks_needed = remaining / max(hours_per_week,1)
    predicted_date = pd.Timestamp.now() + pd.to_timedelta(int(weeks_needed*7), unit='d')
    return predicted_date.date()