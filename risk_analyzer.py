# risk_analyzer.py
import pandas as pd
from datetime import datetime

def analyze_training_risks(df, targets):
    risks = []

    if df.empty:
        return ["No flights logged yet"]

    df = df.copy()
    df["created_at"] = pd.to_datetime(df["created_at"])

    # ------------------ TRAINING GAP ------------------
    last_flight = df["created_at"].max()
    gap_days = (datetime.utcnow() - last_flight).days
    if gap_days > 14:
        risks.append(f"Long training gap detected ({gap_days} days)")

    # ------------------ TRAINING PACE ------------------
    total_hours = df["total_time"].sum()
    days = (df["created_at"].max() - df["created_at"].min()).days
    weeks = max(days / 7, 1)
    weekly_avg = total_hours / weeks
    if weekly_avg < 1.5:
        risks.append("Training pace below recommended level")

    # ------------------ CROSS COUNTRY ------------------
    if "XC" in targets:
        xc_hours = df[df["cross_country"] == True]["total_time"].sum()
        if total_hours > 20 and xc_hours < 1:
            risks.append("Cross-country training overdue")

    # ------------------ NIGHT TRAINING ------------------
    night_hours = df[df["night"] == True]["total_time"].sum()
    if total_hours > 30 and night_hours < 1:
        risks.append("Night training not started")

    return risks