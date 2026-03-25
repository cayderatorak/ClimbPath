from datetime import date, datetime
from uuid import UUID
from database import supabase
from milestones import check_and_unlock_milestones


def _serialize_date(value):
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return value


def _normalize_optional_id(value):
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            return None
        try:
            UUID(cleaned)
            return cleaned
        except ValueError:
            return None
    return value

def _best_effort_insert(table_name, payload):
    try:
        supabase.table(table_name).insert(payload).execute()
    except Exception:
        # Secondary records should not block the main flight log action.
        return


def add_flight(
    user_id,
    instructor_id,
    aircraft_id,
    rate_id,
    duration,
    flight_type,
    is_xc,
    is_night,
    feedback,
    flight_date=None,
):
    flight_date_str = _serialize_date(flight_date or datetime.utcnow())
    instructor_id = _normalize_optional_id(instructor_id)
    aircraft_id = _normalize_optional_id(aircraft_id)
    rate_id = _normalize_optional_id(rate_id)

    is_solo = flight_type == "Solo"
    is_dual = flight_type == "Dual"

    _best_effort_insert("training_events", {
        "student_id":   user_id,
        "instructor_id": instructor_id if not is_solo else None,
        "aircraft_id":  aircraft_id,
        "rate_id":      rate_id,
        "date":         flight_date_str,
        "total_time":   duration,
        "dual_time":    duration if is_dual else 0,
        "solo_time":    duration if is_solo else 0,
        "cross_country": duration if is_xc else 0,
        "night":        duration if is_night else 0,
        "solo":         is_solo,
        "remarks":      feedback,
    })

    flight_id = result.data[0]["id"] if result.data else None

    _best_effort_insert("activity_feed", {
        "student_id":        user_id,
        "instructor_id":     instructor_id,
        "related_flight_id": flight_id,
        "event_type":        flight_type.lower(),
        "event_value":       duration,
        "notes":             feedback,
    })

    supabase.table("activity_feed").insert({
        "user_id":           user_id,
        "activity_type":     "flight",
        "title":             f"Logged a {flight_type.lower()} flight",
        "description":       f"{duration} hrs",
        "related_flight_id": flight_id,
        "is_public":         True,
    }).execute()

    check_and_unlock_milestones(user_id)