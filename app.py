import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# ------------------ CUSTOM MODULES ------------------
from database import supabase, get_student_flights, get_flight_rate
from calculations import calculate_totals, calculate_flight_cost
from milestones import next_milestone, check_and_unlock_milestones
from achievements import calculate_achievements, unlock_achievement
from solo import calculate_solo_readiness, predict_solo
from progress import school_averages, student_rankings
from config import TRACKS

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="ClimbPath", page_icon="✈️", layout="wide")

# ------------------ SESSION STATE ------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "dual_cost" not in st.session_state:
    st.session_state.dual_cost = 180.0
if "solo_cost" not in st.session_state:
    st.session_state.solo_cost = 120.0

# ------------------ LOGIN ------------------
def login():
    if st.session_state.user:
        return st.session_state.user

    st.title("✈️ ClimbPath Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):
            try:
                resp = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = resp.user
                st.rerun()
            except:
                st.error("Invalid login")

    with col2:
        if st.button("Signup"):
            try:
                supabase.auth.sign_up({"email": email, "password": password})
                st.success("Account created!")
            except:
                st.error("Signup failed")
    st.stop()

user = login()

# ------------------ SIDEBAR ------------------
st.sidebar.markdown(f"**Logged in:** {user.email}")
if st.sidebar.button("Logout"):
    supabase.auth.sign_out()
    st.session_state.user = None
    st.rerun()

track = st.sidebar.selectbox("Training Track", list(TRACKS.keys()))
hours_week = st.sidebar.number_input("Hours / Week", 0.0, 20.0, 3.0)
st.session_state.dual_cost = st.sidebar.number_input("Dual Cost", value=st.session_state.dual_cost)
st.session_state.solo_cost = st.sidebar.number_input("Solo Cost", value=st.session_state.solo_cost)

# ------------------ ADD FLIGHT ------------------
st.sidebar.markdown("### Add Flight")
date = st.sidebar.date_input("Date", datetime.today())
flight_type = st.sidebar.selectbox("Flight Type", ["Dual","Solo"])
duration = st.sidebar.number_input("Duration (hrs)", 0.0, 10.0, 1.0)
aircraft_id = st.sidebar.text_input("Aircraft ID")
instructor_id = st.sidebar.text_input("Instructor ID")
is_xc = st.sidebar.checkbox("XC")
is_night = st.sidebar.checkbox("Night")
rate_id = st.sidebar.text_input("Rate ID")  # link to rates table
feedback = st.sidebar.text_area("Instructor Feedback")

if st.sidebar.button("Add Flight"):
    # Add flight
    result = supabase.table("flights").insert({
        "student_id": user.id,
        "instructor_id": instructor_id,
        "aircraft_id": aircraft_id,
        "rate_id": rate_id,
        "total_time": duration,
        "solo": flight_type=="Solo",
        "cross_country": is_xc,
        "night": is_night,
        "created_at": datetime.utcnow()
    }).execute()

    flight_id = result.data[0]["id"] if result.data else None

    # Log training event
    event_type = flight_type.lower()
    supabase.table("training_events").insert({
        "student_id": user.id,
        "instructor_id": instructor_id,
        "related_flight_id": flight_id,
        "event_type": event_type,
        "event_value": duration,
        "notes": feedback
    }).execute()

    # Add activity feed entry
    supabase.table("activity_feed").insert({
        "student_id": user.id,
        "event_type": "flight",
        "event_value": duration,
        "related_id": flight_id
    }).execute()

    # Unlock achievements/milestones
    check_and_unlock_milestones(user.id)
    st.success("Flight added and milestones checked!")
    st.rerun()

# ------------------ LOAD DATA ------------------
flights_data = get_student_flights(user.id).data
df = pd.DataFrame(flights_data) if flights_data else pd.DataFrame(columns=[
    "id","student_id","instructor_id","aircraft_id","rate_id",
    "total_time","solo","cross_country","night","created_at"
])

# Calculate cost per flight dynamically
for idx, flight in df.iterrows():
    rate = get_flight_rate(flight["id"])
    if rate:
        df.loc[idx, "flight_cost"] = calculate_flight_cost(flight["total_time"], rate["aircraft_hourly_rate"], rate["instructor_hourly_rate"])
total_spent = df["flight_cost"].sum() if not df.empty else 0

# ------------------ CALCULATIONS ------------------
totals, _ = calculate_totals(df)
milestone = next_milestone(totals)
solo_score = calculate_solo_readiness(df)
predicted_solo = predict_solo(df, hours_week, TRACKS[track])
achievements_list = calculate_achievements(totals)
school_avg = school_averages(track)
rank, percentile = student_rankings(user.id, track)

# ------------------ METRICS ------------------
c1,c2,c3,c4,c5,c6 = st.columns(6)
c1.metric("Total Hours", round(totals["Total"],1))
c2.metric("Next Milestone", milestone)
c3.metric("Solo Readiness", f"{solo_score}%")
c4.metric("Predicted Solo", predicted_solo)
c5.metric("Total Spent", f"${total_spent:,.0f}")
c6.metric("Remaining Cost", f"${(TRACKS[track]['Total']-totals['Total'])*(total_spent/totals['Total'] if totals['Total'] else 1):,.0f}")

# ------------------ FAA PROGRESS ------------------
st.markdown("### FAA Progress")
for cat in ["Dual","Solo","XC","Night"]:
    percent = min(totals.get(cat,0)/TRACKS[track][cat]*100, 100)
    st.write(f"{cat}: {totals.get(cat,0):.1f}/{TRACKS[track][cat]}")
    st.progress(percent/100)

# ------------------ ACHIEVEMENTS ------------------
st.markdown("### Achievements")
for badge in achievements_list:
    st.write("🏅", badge)

# ------------------ PROGRESS VS SCHOOL ------------------
st.markdown("### Progress vs School Averages")
if school_avg:
    for key, val in school_avg.items():
        st.write(f"{key}: You: {totals.get(key,0)} hrs • School Avg: {val:.1f} hrs")

# ------------------ STUDENT RANKING ------------------
st.markdown("### Student Ranking")
st.write(f"You are ranked #{rank} ({percentile} percentile) in your school for {track} track")

# ------------------ TRAINING VELOCITY ------------------
st.markdown("### Training Velocity")
if not df.empty:
    df["week"] = pd.to_datetime(df["created_at"]).dt.to_period("W").astype(str)
    weekly = df.groupby("week").total_time.sum().reset_index()
    chart = alt.Chart(weekly).mark_bar().encode(x="week", y="total_time")
    st.altair_chart(chart, use_container_width=True)

# ------------------ FLIGHT LOGBOOK ------------------
st.markdown("### Flight Logbook")
display_df = df.drop(columns=["id","student_id"], errors="ignore")
gb = GridOptionsBuilder.from_dataframe(display_df)
gb.configure_columns(display_df.columns, editable=True)
gb.configure_selection("single")
grid = AgGrid(display_df, gridOptions=gb.build(), update_mode=GridUpdateMode.MODEL_CHANGED, height=400)
updated = pd.DataFrame(grid["data"])

# ------------------ DELETE / EDIT FLIGHTS ------------------
selected = grid["selected_rows"]
if selected:
    flight_id = selected[0]["id"]
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Delete Flight"):
            supabase.table("flights").delete().eq("id", flight_id).execute()
            st.success("Flight deleted!")
            st.rerun()

# ------------------ CSV EXPORT ------------------
csv = updated.to_csv(index=False).encode()
st.download_button("Download CSV", csv, "climbpath_logbook.csv")

# ------------------ REAL-TIME ACTIVITY FEED ------------------
st.markdown("### 📰 Activity Feed")

def render_feed_item(row):
    ts = pd.to_datetime(row["created_at"])
    time_ago = humanize.naturaltime(datetime.utcnow() - ts)
    
    if row["event_type"] == "flight":
        icon = "✈️"
        text = f"{row['student']['email']} logged {row['event_value']} hr flight"
        color = "#1f77b4"  # blue
    elif row["event_type"] == "achievement":
        icon = "🏅"
        text = f"{row['student']['email']} unlocked an achievement"
        color = "#ff7f0e"  # orange
    elif row["event_type"] == "milestone":
        icon = "🎯"
        text = f"{row['student']['email']} reached a milestone"
        color = "#2ca02c"  # green
    else:
        icon = "❓"
        text = f"{row['student']['email']} did something"
        color = "#7f7f7f"
    
    return f"""
    <div style="border-left:4px solid {color}; padding:8px 12px; margin-bottom:4px; border-radius:6px; background:#f8f9fa;">
        <span style="font-size:18px;">{icon}</span>
        <strong>{text}</strong><br>
        <small style="color:#6c757d">{time_ago}</small>
    </div>
    """

# Load feed
feed = supabase.table("activity_feed").select(
    "id,student_id,event_type,event_value,related_id,created_at,student:students(email)"
).order("created_at", desc=True).limit(30).execute().data

if feed:
    feed_df = pd.DataFrame(feed)
    feed_df["created_at"] = pd.to_datetime(feed_df["created_at"])
    
    # Display feed in a scrollable container
    feed_html = "".join(feed_df.apply(render_feed_item, axis=1).tolist())
    st.markdown(f'<div style="max-height:400px; overflow-y:auto;">{feed_html}</div>', unsafe_allow_html=True)
else:
    st.write("No activity yet.")

# ------------------ REAL-TIME SUBSCRIPTION ------------------
def subscribe_feed():
    def callback(payload):
        st.experimental_rerun()
    supabase.table("activity_feed").on("INSERT", callback).subscribe()

subscribe_feed()