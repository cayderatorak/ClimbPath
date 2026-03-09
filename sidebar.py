import streamlit as st
from datetime import datetime
from load_data import load_student_flights
from add_flight import add_flight as add_flight_func
from calculations import calculate_totals, calculate_flight_cost
from milestones import next_milestone
from solo import calculate_solo_readiness, predict_solo
from achievements import calculate_achievements
from progress import school_averages, student_rankings
from risk_analyzer import analyze_training_risks
from feedback_ai import analyze_feedback
from config import TRACKS
from gamification import summarize_gamification

def sidebar_controls(user):
    st.sidebar.markdown(f"**Logged in:** {user.email}")

    if st.sidebar.button("Logout"):
        from database import supabase
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

    # Inputs
    track = st.sidebar.selectbox("Training Track", list(TRACKS.keys()))
    hours_week = st.sidebar.number_input("Hours / Week", 0.0, 20.0, 3.0)
    dual_cost = st.sidebar.number_input("Dual Cost", value=st.session_state.get("dual_cost", 180.0))
    solo_cost = st.sidebar.number_input("Solo Cost", value=st.session_state.get("solo_cost", 120.0))

    # Add Flight inputs
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
        add_flight_func(
            user_id=user.id,
            instructor_id=instructor_id,
            aircraft_id=aircraft_id,
            rate_id=rate_id,
            duration=duration,
            flight_type=flight_type,
            is_xc=is_xc,
            is_night=is_night,
            feedback=feedback
        )
        st.success("Flight added!")
        st.rerun()

    # Load flights
    df = load_student_flights(user.id)

    # Cost calculation
    for idx, flight in df.iterrows():
        from database import get_flight_rate
        rate = get_flight_rate(flight["id"])
        if rate:
            df.loc[idx,"flight_cost"] = calculate_flight_cost(
                flight["total_time"],
                rate["aircraft_hourly_rate"],
                rate["instructor_hourly_rate"]
            )

    total_spent = df["flight_cost"].sum() if not df.empty else 0

    # Training calculations
    totals,_ = calculate_totals(df)
    milestone = next_milestone(totals)
    solo_score = calculate_solo_readiness(df)
    predicted_solo, solo_confidence = predict_solo(df, hours_week, TRACKS[track])
    achievements_list = calculate_achievements(totals)
    school_avg = school_averages(track)
    rank, percentile = student_rankings(user.id, track)
    risk_alerts = analyze_training_risks(df, TRACKS[track])
    feedback_insights = analyze_feedback(df)

    gamification_summary = summarize_gamification(df)

    remaining_hours = max(TRACKS[track]["Total"] - totals["Total"],0)
    avg_cost_per_hour = total_spent / totals["Total"] if totals["Total"] else 0
    remaining_cost = remaining_hours * avg_cost_per_hour

    return {
        "df": df,
        "totals": totals,
        "track": track,
        "predicted_solo": predicted_solo,
        "solo_confidence": solo_confidence,
        "milestone": milestone,
        "solo_score": solo_score,
        "total_spent": total_spent,
        "remaining_cost": remaining_cost,
        "achievements": achievements_list,
        "school_avg": school_avg,
        "rank": rank,
        "percentile": percentile,
        "risk_alerts": risk_alerts,
    
        "feedback": feedback_insights,
        "gamification": gamification_summary
    }