import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def pace_analyzer(df):
    st.markdown("### Training Pace Analyzer")
    if df.empty:
        st.write("Log flights to analyze training pace.")
        return

    timestamp_col = "created_at" if "created_at" in df.columns else "date" if "date" in df.columns else None
    if not timestamp_col:
        st.write("No timestamp data available yet.")
        return

    df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors="coerce")
    df = df.dropna(subset=[timestamp_col])
    if df.empty:
        st.write("No valid flight timestamps available yet.")
        return

    last30 = df[df[timestamp_col] > datetime.utcnow() - timedelta(days=30)]
    hours_30 = last30["total_time"].sum()

    total_days = (df[timestamp_col].max() - df[timestamp_col].min()).days
    weeks = max(total_days / 7, 1)
    weekly_avg = df["total_time"].sum() / weeks

    if weekly_avg >= 3:
        pace = "🔥 Fast"
    elif weekly_avg >= 1.5:
        pace = "👍 Good"
    else:
        pace = "⚠️ Slow"

    c1,c2,c3 = st.columns(3)
    c1.metric("Last 30 Days", f"{hours_30:.1f} hrs")
    c2.metric("Weekly Average", f"{weekly_avg:.1f} hrs/week")
    c3.metric("Training Pace", pace)