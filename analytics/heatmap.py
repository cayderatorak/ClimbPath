import streamlit as st
import pandas as pd
import altair as alt

def training_heatmap(df):
    st.markdown("### 🔥 Training Activity")
    if df.empty:
        st.write("Log flights to see training activity.")
        return

    df["date"] = pd.to_datetime(df["created_at"]).dt.date
    heatmap = df.groupby("date")["total_time"].sum().reset_index()
    heatmap["date"] = pd.to_datetime(heatmap["date"])
    heatmap["week"] = heatmap["date"].dt.isocalendar().week
    heatmap["weekday"] = heatmap["date"].dt.weekday

    chart = alt.Chart(heatmap).mark_rect().encode(
        x="week:O",
        y="weekday:O",
        color=alt.Color("total_time:Q", scale=alt.Scale(scheme="blues")),
        tooltip=["date", "total_time"]
    ).properties(height=200)

    st.altair_chart(chart, use_container_width=True)