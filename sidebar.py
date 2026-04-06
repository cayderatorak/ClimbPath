import streamlit as st
from datetime import datetime
from load_data import load_student_flights, load_student_feedback_notes, _safe_execute, _empty_frame
from add_flight import add_flight as add_flight_func
from calculations import calculate_totals, calculate_flight_cost
import calculations as calculations_module
from milestones import next_milestone
from solo import calculate_solo_readiness, predict_solo
from achievements import calculate_achievements
from progress import school_averages, student_rankings
from risk_analyzer import analyze_training_risks
from feedback_ai import analyze_feedback
from config import TRACKS
from gamification import summarize_gamification
from database import supabase


DEFAULT_DUAL_COST = 180.0
DEFAULT_SOLO_COST = 120.0
SETTINGS_TABLE = "student_settings"

def _estimate_remaining_cost(*, totals, requirements, hours_per_week, cost_per_hour, proficiency_score, consistency_score):
    estimator = getattr(calculations_module, "estimate_remaining_cost", None)
    if callable(estimator):
        return estimator(
            totals=totals,
            requirements=requirements,
            hours_per_week=hours_per_week,
            cost_per_hour=cost_per_hour,
            proficiency_score=proficiency_score,
            consistency_score=consistency_score,
        )

    required_total = requirements.get("Total", 0) if requirements else 0
    remaining_hours = max(0, required_total - totals.get("Total", 0))
    return {
        "adjusted_required_hours": round(required_total, 1),
        "remaining_hours": round(remaining_hours, 1),
        "estimated_cost": round(remaining_hours * cost_per_hour, 0),
        "pace_factor": 1.0,
        "proficiency_factor": 1.0,
        "consistency_factor": 1.0,
    }

def _user_value(user, key):
    if isinstance(user, dict):
        return user.get(key)
    return getattr(user, key, None)


def _load_student_cost_settings(user_id):
    if not user_id:
        return DEFAULT_DUAL_COST, DEFAULT_SOLO_COST

    try:
        response = (
            supabase.table(SETTINGS_TABLE)
            .select("dual_cost,solo_cost")
            .eq("student_id", user_id)
            .limit(1)
            .execute()
        )
        if response.data:
            settings = response.data[0]
            dual_cost = float(settings.get("dual_cost") or DEFAULT_DUAL_COST)
            solo_cost = float(settings.get("solo_cost") or DEFAULT_SOLO_COST)
            return dual_cost, solo_cost
    except Exception:
        pass

    return DEFAULT_DUAL_COST, DEFAULT_SOLO_COST


def _save_student_cost_settings(user_id, dual_cost, solo_cost):
    if not user_id:
        return

    try:
        (
            supabase.table(SETTINGS_TABLE)
            .upsert(
                {
                    "student_id": user_id,
                    "dual_cost": float(dual_cost),
                    "solo_cost": float(solo_cost),
                },
                on_conflict="student_id",
            )
            .execute()
        )
    except Exception:
        pass


def sidebar_controls(user):
    user_email = _user_value(user, "email") or "Unknown user"
    user_id = _user_value(user, "id")

    st.sidebar.title("ClimbPath")
    st.sidebar.caption(f"Logged in as {user_email}")

    if st.sidebar.button("Logout"):
        from database import supabase
        supabase.auth.sign_out()
        st.session_state.user = None
        st.session_state.pop("supabase_access_token", None)
        st.session_state.pop("supabase_refresh_token", None)
        st.rerun()

    loaded_for_user = st.session_state.get("cost_settings_loaded_for")
    if loaded_for_user != user_id:
        loaded_dual_cost, loaded_solo_cost = _load_student_cost_settings(user_id)
        st.session_state.dual_cost = loaded_dual_cost
        st.session_state.solo_cost = loaded_solo_cost
        st.session_state.saved_dual_cost = loaded_dual_cost
        st.session_state.saved_solo_cost = loaded_solo_cost
        st.session_state.cost_settings_loaded_for = user_id

    st.sidebar.divider()
    st.sidebar.markdown("#### Training Setup")
    track = st.sidebar.selectbox("Training Track", list(TRACKS.keys()))
    hours_week = st.sidebar.number_input("Hours / Week", 0.0, 20.0, 3.0, step=0.1)

    with st.sidebar.expander("Hourly Cost Settings"):
        dual_cost = st.number_input(
            "Dual Cost",
            min_value=0.0,
            step=5.0,
            key="dual_cost",
        )
        solo_cost = st.number_input(
            "Solo Cost",
            min_value=0.0,
            step=5.0,
            key="solo_cost",
        )

    if (
        user_id
        and (
            dual_cost != st.session_state.get("saved_dual_cost")
            or solo_cost != st.session_state.get("saved_solo_cost")
        )
    ):
        _save_student_cost_settings(user_id, dual_cost, solo_cost)
        st.session_state.saved_dual_cost = dual_cost
        st.session_state.saved_solo_cost = solo_cost


    st.sidebar.divider()
    with st.sidebar.expander("Log a Flight", expanded=True):
        date = st.date_input("Date", datetime.today())
        flight_type = st.selectbox("Flight Type", ["Dual", "Solo"])
        duration = st.number_input("Duration (hrs)", 0.0, 10.0, 1.0, step=0.1)
        aircraft_tail_number = st.text_input("Aircraft Tail Number")
        instructor_name = st.text_input("Instructor Name")
        is_xc = st.checkbox("Cross Country")
        is_night = st.checkbox("Night")
        feedback = st.text_area("Instructor Feedback")

        if st.button("Add Flight", use_container_width=True):
            try:
                metadata_lines = []
                if instructor_name.strip():
                    metadata_lines.append(f"Instructor: {instructor_name.strip()}")
                if aircraft_tail_number.strip():
                    metadata_lines.append(f"Aircraft: {aircraft_tail_number.strip()}")
                metadata = "\n".join(metadata_lines)
                combined_feedback = feedback.strip()
                if metadata:
                    combined_feedback = (
                        f"{combined_feedback}\n\n{metadata}" if combined_feedback else metadata
                    )

                add_flight_func(
                    user_id=user_id,
                    instructor_id=None,
                    aircraft_id=None,
                    rate_id=None,
                    duration=duration,
                    flight_type=flight_type,
                    is_xc=is_xc,
                    is_night=is_night,
                    feedback=combined_feedback,
                    flight_date=date
                )

                st.success("Flight added!")
                st.rerun()
            except Exception as exc:
                st.error(
                    "Unable to add flight. Open diagnostics below for details."
                )
                with st.expander("Add flight diagnostics"):
                    st.code(str(exc))
                    st.write(
                        {
                            "user_id": user_id,
                            "flight_type": flight_type,
                            "duration": duration,
                            "is_xc": is_xc,
                            "is_night": is_night,
                            "date": str(date),
                        }
                    )




    # Load flights
    df = load_student_flights(user_id)
    if "flight_cost" not in df.columns:
        df["flight_cost"] = 0.0

    # Cost calculation
    for idx, flight in df.iterrows():
        from database import get_flight_rate
        rate = get_flight_rate(flight["id"])
        if rate:
            df.loc[idx, "flight_cost"] = calculate_flight_cost(
                flight["total_time"],
                rate["aircraft_hourly_rate"],
                rate["instructor_hourly_rate"]
            )

    total_spent = df["flight_cost"].sum()

    # Training calculations
    totals, _ = calculate_totals(df)
    milestone = next_milestone(totals)
    solo_score = calculate_solo_readiness(df)
    solo_prediction = predict_solo(df, hours_week, TRACKS[track])

    predicted_solo = solo_prediction["predicted_date"]
    solo_confidence = solo_prediction["confidence"]

    achievements_list = calculate_achievements(totals)
    school_avg = school_averages(track)
    rank, percentile = student_rankings(user_id, track)
    risk_alerts = analyze_training_risks(df, TRACKS[track])
    feedback_df = load_student_feedback_notes(user_id)
    feedback_insights = analyze_feedback(feedback_df)

    gamification_summary = summarize_gamification(df)

    avg_cost_per_hour = total_spent / totals["Total"] if totals["Total"] else 0
    blended_hourly_cost = avg_cost_per_hour if avg_cost_per_hour > 0 else ((dual_cost + solo_cost) / 2)

    cost_projection = _estimate_remaining_cost(
        totals=totals,
        requirements=TRACKS[track],
        hours_per_week=hours_week,
        cost_per_hour=blended_hourly_cost,
        proficiency_score=solo_score,
        consistency_score=solo_confidence,
    )
    remaining_cost = cost_projection["estimated_cost"]

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