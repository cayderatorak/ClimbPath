python
import streamlit as st
import pandas as pd
import altair as alt
import humanize
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# ------------------ CUSTOM MODULES ------------------
from database import supabase, get_student_flights, get_flight_rate
from calculations import calculate_totals, calculate_flight_cost
from milestones import next_milestone, check_and_unlock_milestones
from achievements import calculate_achievements
from solo import calculate_solo_readiness, predict_solo
from progress import school_averages, student_rankings
from config import TRACKS
from feedback_ai import analyze_feedback
from risk_analyzer import analyze_training_risks

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
rate_id = st.sidebar.text_input("Rate ID")

is_xc = st.sidebar.checkbox("XC")
is_night = st.sidebar.checkbox("Night")

feedback = st.sidebar.text_area("Instructor Feedback")

if st.sidebar.button("Add Flight"):

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

    supabase.table("training_events").insert({
        "student_id": user.id,
        "instructor_id": instructor_id,
        "related_flight_id": flight_id,
        "event_type": flight_type.lower(),
        "event_value": duration,
        "notes": feedback
    }).execute()

    supabase.table("activity_feed").insert({
        "student_id": user.id,
        "event_type": "flight",
        "event_value": duration,
        "related_id": flight_id
    }).execute()

    check_and_unlock_milestones(user.id)

    st.success("Flight added!")
    st.rerun()

# ------------------ LOAD DATA ------------------
flights_data = get_student_flights(user.id).data

df = pd.DataFrame(flights_data) if flights_data else pd.DataFrame(columns=[
    "id","student_id","instructor_id","aircraft_id","rate_id",
    "total_time","solo","cross_country","night","created_at"
])

# ------------------ COST CALCULATIONS ------------------
for idx, flight in df.iterrows():
    rate = get_flight_rate(flight["id"])
    if rate:
        df.loc[idx,"flight_cost"] = calculate_flight_cost(
            flight["total_time"],
            rate["aircraft_hourly_rate"],
            rate["instructor_hourly_rate"]
        )

total_spent = df["flight_cost"].sum() if not df.empty else 0

# ------------------ TRAINING CALCULATIONS ------------------
totals,_ = calculate_totals(df)

milestone = next_milestone(totals)

solo_score = calculate_solo_readiness(df)

predicted_solo, solo_confidence = predict_solo(df, hours_week, TRACKS[track])

achievements_list = calculate_achievements(totals)

school_avg = school_averages(track)

rank,percentile = student_rankings(user.id, track)

risk_alerts = analyze_training_risks(df, TRACKS[track])

# ------------------ METRICS ------------------
remaining_hours = max(TRACKS[track]["Total"] - totals["Total"],0)

avg_cost_per_hour = total_spent / totals["Total"] if totals["Total"] else 0

remaining_cost = remaining_hours * avg_cost_per_hour

c1,c2,c3,c4,c5,c6 = st.columns(6)

c1.metric("Total Hours", round(totals["Total"],1))
c2.metric("Next Milestone", milestone)
c3.metric("Solo Readiness", f"{solo_score}%")
c4.metric("Predicted Solo", predicted_solo, f"{solo_confidence}% confidence")
c5.metric("Total Spent", f"${total_spent:,.0f}")
c6.metric("Remaining Cost", f"${remaining_cost:,.0f}")

# ------------------ TRAINING TIMELINE ------------------
st.markdown("### Training Timeline")

total_hours = totals["Total"]

solo_progress = min(total_hours / TRACKS[track]["Solo"],1)
xc_progress = min(total_hours / TRACKS[track]["XC"],1)
checkride_progress = min(total_hours / TRACKS[track]["Total"],1)

timeline = [
("Start Training",1),
("Solo",solo_progress),
("Cross Country",xc_progress),
("Checkride",checkride_progress)
]

cols = st.columns(len(timeline))

for col,(label,progress) in zip(cols,timeline):

    if progress >= 1:
        status="✔"
    elif progress > 0:
        status="●"
    else:
        status="○"

    col.metric(label,status)

# ------------------ TRAINING PROGRESS ------------------
st.markdown("### Training Progress")

st.write("Solo")
st.progress(solo_progress)

st.write("Cross Country")
st.progress(xc_progress)

st.write("Checkride")
st.progress(checkride_progress)

# ------------------ TRAINING VELOCITY ------------------
st.markdown("### Training Velocity")

if not df.empty:

    df["week"] = pd.to_datetime(df["created_at"]).dt.to_period("W").astype(str)

    weekly = df.groupby("week").total_time.sum().reset_index()

    chart = alt.Chart(weekly).mark_bar().encode(
        x="week",
        y="total_time"
    )

    st.altair_chart(chart,use_container_width=True)

# ------------------ TRAINING HEATMAP ------------------
st.markdown("### 🔥 Training Activity")

if not df.empty:

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

else:
    st.write("Log flights to see training activity.")

# ------------------ TRAINING PACE ANALYZER ------------------
st.markdown("### Training Pace Analyzer")

if not df.empty:

    df["created_at"] = pd.to_datetime(df["created_at"])

    last30 = df[df["created_at"] > datetime.utcnow() - pd.Timedelta(days=30)]

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

else:

    st.write("Log flights to analyze training pace.")    

# ------------------ TRAINING RISK ALERTS ------------------
st.markdown("### ⚠️ Training Risk Alerts")

if risk_alerts:

    for risk in risk_alerts:
        st.warning(risk)

else:

    st.success("No training risks detected")

# ------------------ FAA PROGRESS ------------------
st.markdown("### FAA Progress")

for cat in ["Dual","Solo","XC","Night"]:
    percent = min(totals.get(cat,0)/TRACKS[track][cat]*100,100)
    st.write(f"{cat}: {totals.get(cat,0):.1f}/{TRACKS[track][cat]}")
    st.progress(percent/100)

# ------------------ ACHIEVEMENTS ------------------
st.markdown("### Achievements")

for badge in achievements_list:
    st.write("🏅",badge)

# ------------------ SCHOOL COMPARISON ------------------
st.markdown("### Progress vs School Averages")

if school_avg:
    for key,val in school_avg.items():
        st.write(f"{key}: You {totals.get(key,0)} hrs • School Avg {val:.1f} hrs")

# ------------------ STUDENT RANKING ------------------
st.markdown("### Student Ranking")

st.write(f"You are ranked #{rank} ({percentile} percentile) in {track}")

# ------------------ LEADERBOARD ------------------
st.markdown("### 🏆 Top Students")

leaderboard = supabase.table("flights") \
.select("student_id,total_time") \
.execute()

if leaderboard.data:

    lb = pd.DataFrame(leaderboard.data)

    top = lb.groupby("student_id").total_time.sum().sort_values(ascending=False).head(5)

    for i,(student,hours) in enumerate(top.items(),1):
        st.write(f"{i}. {student[:6]} — {hours:.1f} hrs")

# ------------------ INSTRUCTOR FEEDBACK ANALYZER ------------------
st.markdown("### 🧠 Instructor Feedback Insights")

if feedback_insights:

    sorted_items = sorted(feedback_insights.items(), key=lambda x: x[1], reverse=True)

    for category, count in sorted_items:

        if count >= 5:
            label = "Focus Area ⚠️"
        elif count >= 2:
            label = "Improving 👍"
        else:
            label = "Mentioned"

        st.write(f"**{category}** — {label} ({count} mentions)")

else:

    st.write("No instructor feedback available yet.")

# ------------------ LOGBOOK ------------------
st.markdown("### Flight Logbook")

display_df = df.drop(columns=["student_id"],errors="ignore")

gb = GridOptionsBuilder.from_dataframe(display_df)

gb.configure_columns(display_df.columns,editable=True)

gb.configure_selection("single")

grid = AgGrid(
display_df,
gridOptions=gb.build(),
update_mode=GridUpdateMode.MODEL_CHANGED,
height=400
)

updated = pd.DataFrame(grid["data"])

# ------------------ DELETE FLIGHT ------------------
selected = grid["selected_rows"]

if selected:

    flight_id = selected[0]["id"]

    if st.button("Delete Flight"):

        supabase.table("flights").delete().eq("id",flight_id).execute()

        st.success("Flight deleted")

        st.rerun()

# ------------------ EXPORT CSV ------------------
csv = updated.to_csv(index=False).encode()

st.download_button(
"Download CSV",
csv,
"climbpath_logbook.csv"
)

# ------------------ FLIGHT ACTIVITY FEED ------------------
st.markdown("### ✈️ Flight Activity Feed")

feed = supabase.table("activity_feed") \
.select("event_type,event_value,created_at") \
.order("created_at", desc=True) \
.limit(30) \
.execute().data

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
