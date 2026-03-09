import streamlit as st
import pandas as pd
import altair as alt

def training_velocity(df):
    st.markdown("### Training Velocity")
    if df.empty:
        st.write("Log flights to see training velocity.")
        return

    df_copy = df.copy()
    df_copy["week"] = pd.to_datetime(df_copy["created_at"]).dt.to_period("W")
    weekly = df_copy.groupby("week").total_time.sum().reset_index()
    
    chart = alt.Chart(weekly).mark_bar().encode(
        x="week",
        y="total_time"
    )

    st.altair_chart(chart,use_container_width=True)