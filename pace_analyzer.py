import streamlit as st
from datetime import datetime, timedelta

def pace_analyzer(df):
    st.markdown("### Training Pace Analyzer")
    if df.empty:
        st.write("Log flights to analyze training pace.")
        return

    df["created_at"] = pd.to_datetime(df["created_at"])
    last30 = df[df["created_at"] > datetime.utcnow() - timedelta(days=30)]
    hours_30 = last30["total_time"].sum()

    total_days = (df["created_at"].max() - df["created_at"].min()).days
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