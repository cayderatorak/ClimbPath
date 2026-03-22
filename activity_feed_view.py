import streamlit as st
import pandas as pd
import humanize
from datetime import datetime, timezone
from database import supabase


def activity_feed(user_id):
    st.markdown("### ✈️ Flight Activity Feed")

    try:
        feed = (
            supabase.table("activity_feed")
            .select("activity_type,title,description,created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(30)
            .execute()
            .data
        )
    except Exception as e:
        st.warning("Activity feed unavailable.")
        st.caption(str(e))  # remove before going live
        return

    if not feed:
        st.write("No recent activity.")
        return

    for row in feed:
        try:
            ts = pd.to_datetime(row["created_at"], utc=True).to_pydatetime()
            now = datetime.now(timezone.utc)
            time_ago = humanize.naturaltime(now - ts)
        except Exception:
            time_ago = ""

        activity_type = row.get("activity_type", "")
        title = row.get("title") or ""
        description = row.get("description") or ""

        if activity_type == "flight":
            icon = "✈️"
            text = title or "Logged a flight"
        elif activity_type == "achievement":
            icon = "🏅"
            text = title or "Unlocked an achievement"
        elif activity_type == "milestone":
            icon = "🎯"
            text = title or "Reached a training milestone"
        else:
            icon = "📌"
            text = title or "Training update"

        if description:
            st.write(f"{icon} {text} — {description} • {time_ago}")
        else:
            st.write(f"{icon} {text} • {time_ago}")