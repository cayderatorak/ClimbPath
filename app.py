import streamlit as st
import os

from auth import login
from instructor import instructor_dashboard
from sidebar import sidebar_controls
from solo import calculate_solo_readiness, predict_solo
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
from gamification_view import gamification_section
from config import TRACKS
from pdf_reports import generate_training_report
from faa_requirements import PRIVATE_PILOT_REQS, INSTRUMENT_REQS
from calculations import (
    calculate_totals,
    calculate_flight_cost,
    checkride_readiness,
    hours_remaining,
    calculate_training_pace
)

st.set_page_config(page_title="ClimbPath", page_icon="✈️", layout="wide")

st.info("Used by student pilots to track hours, costs, and checkride readiness ✈️")

st.markdown("""
<style>
button {
    height: 3em;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

user = login()

if not user:
    st.stop()

user_role = user["role"]
    
if "role" not in st.session_state:
    st.session_state.role = "student"

# Instructor view
if user_role == "instructor":
    instructor_dashboard.show(user)
    st.stop()

if "role" not in st.session_state:
    st.session_state.role = "student"

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
gamification = sidebar_data["gamification"]
hours_per_week = calculate_training_pace(df)  # df = your flight log dataframe

# Render all sections
dashboard_metrics(totals, milestone, solo_score, predicted_solo, solo_confidence, total_spent, remaining_cost, hours_per_week)
training_timeline(totals, TRACKS[track])
training_velocity(df)
training_heatmap(df)
pace_analyzer(df)
gamification_section(gamification)
risk_section(risk_alerts)
achievements_section(achievements_list)
school_comparison(totals, school_avg)
ranking_section(rank, percentile, track)
leaderboard_section()
feedback_section(feedback_insights)
logbook_section(df)
activity_feed(user["id"])


st.title("✈️ Free Student Pilot Checklist")

st.write(
"""
Download the **ClimbPath Student Pilot Checklist** used by pilots to track
their progress from first lesson to Private Pilot checkride.
"""
)

pdf_path = "resources/climbpath_student_pilot_checklist.pdf"

if os.path.exists(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        st.download_button(
            label="📥 Download the Free Checklist",
            data=pdf_file,
            file_name="ClimbPath_Student_Pilot_Checklist.pdf",
            mime="application/pdf",
        )

st.markdown("---")

st.subheader("🚀 Want automatic progress tracking?")

st.write(
"""
ClimbPath automatically tracks:

• Flight hours  
• PPL requirements  
• Training cost  
• Checkride readiness
"""
)

st.link_button("Start Tracking Flights", "https://climbpath.app/login")


score = checkride_readiness(totals, PRIVATE_PILOT_REQS)

st.subheader("🧑‍✈️ Checkride Readiness")
st.metric("Readiness", f"{score}%")
st.progress(score / 100)

remaining = hours_remaining(totals, PRIVATE_PILOT_REQS)

st.info(f"Estimated hours remaining: {remaining['Total']:.1f}")


solo_prediction = predict_solo(df, hours_per_week, PRIVATE_PILOT_REQS)

st.subheader("✈️ First Solo Prediction")

st.write(f"Estimated Date: {solo_prediction['predicted_date']}")
st.write(f"Hours Remaining: {solo_prediction['hours_remaining']}")

st.progress(solo_prediction["confidence"] / 100)


hours_per_week = calculate_training_pace(df)

solo_prediction = predict_solo(df, hours_per_week, PRIVATE_PILOT_REQS)