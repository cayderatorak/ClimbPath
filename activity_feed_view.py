import streamlit as st
import pandas as pd
import humanize
from datetime import datetime
from database import supabase

def activity_feed():
    st.markdown("### ✈️ Flight Activity Feed")
    feed = supabase.table("activity_feed").select("event_type,event_value,created_at").order("created_at", desc=True).limit(30).execute().data
    if feed:
        feed_df = pd.DataFrame(feed)
        for _,row in feed_df.iterrows():
            ts = pd.to_datetime(row["created_at"])
            time_ago = humanize.naturaltime(datetime.utcnow() - ts)
            if row["event_type"] == "flight":
                icon = "✈️"
                text = f"Logged {row['event_value']} hr flight"
            elif row["event_type"] == "achievement":
                icon = "🏅"
                text = "Unlocked an achievement"
            elif row["event_type"] == "milestone":
                icon = "🎯"
                text = "Reached a training milestone"
            else:
                icon = "📌"
                text = "Training update"
            st.write(f"{icon} {text} • {time_ago}")
    else:
        st.write("No recent activity.")