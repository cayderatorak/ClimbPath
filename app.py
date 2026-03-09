import streamlit as st

from auth import login
from sidebar import sidebar_controls
from metrics_dashboard import dashboard_metrics
from timeline import training_timeline
from velocity_chart import training_velocity
from heatmap import training_heatmap
from pace_analyzer import pace_analyzer
from risk_alerts import risk_section
from faa_progress import faa_progress
from achievements_view import achievements_section
from school_comparison import school_comparison
from ranking import ranking_section
from leaderboard import leaderboard_section
from feedback_insights import feedback_section
from logbook import logbook_section
from activity_feed_view import activity_feed

st.set_page_config(page_title="ClimbPath", page_icon="✈️", layout="wide")

user = login()

# Sidebar + data aggregation
sidebar_data = sidebar_controls(user)

# Unpack
df = sidebar_data["df"]
totals = sidebar_data["totals"]
track = sidebar_data["track"]
predicted_solo = sidebar_data["predicted_solo"]
solo_confidence = sidebar_data["solo_confidence"]
milestone = sidebar_data["milestone"]
solo_score = sidebar_data["solo_score"]
total_spent = sidebar_data["total_spent"]
remaining_cost = sidebar_data["remaining_cost"]
achievements_list = sidebar_data["achievements"]
school_avg = sidebar_data["school_avg"]
rank = sidebar_data["rank"]
percentile = sidebar_data["percentile"]
risk_alerts = sidebar_data["risk_alerts"]
feedback_insights = sidebar_data["feedback"]

# Render all sections
dashboard_metrics(totals, milestone, solo_score, predicted_solo, solo_confidence, total_spent, remaining_cost)
training_timeline(totals, TRACKS[track])
training_velocity(df)
training_heatmap(df)
pace_analyzer(df)
risk_section(risk_alerts)
faa_progress(totals, track)
achievements_section(achievements_list)
school_comparison(totals, school_avg)
ranking_section(rank, percentile, track)
leaderboard_section()
feedback_section(feedback_insights)
logbook_section(df)
activity_feed()