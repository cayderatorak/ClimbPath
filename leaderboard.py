import streamlit as st
import pandas as pd
from database import supabase

def leaderboard_section():
    st.markdown("### 🏆 Top Students")
    leaderboard = supabase.table("flights").select("student_id,total_time").execute()
    if leaderboard.data:
        lb = pd.DataFrame(leaderboard.data)
        top = lb.groupby("student_id").total_time.sum().sort_values(ascending=False).head(5)
        for i,(student,hours) in enumerate(top.items(),1):
            st.write(f"{i}. {student[:6]} — {hours:.1f} hrs")