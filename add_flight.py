from datetime import date, datetime
import logging
from uuid import UUID

from database import supabase
from milestones import check_and_unlock_milestones

logger = logging.getLogger(__name__)


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


def _normalize_required_id(value):
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


def _resolve_student_id(user_id):
    """
    Resolve the student identifier used for inserts.
    Prefer the authenticated Supabase user's UUID to satisfy RLS checks.
    """
    auth_user_id = None
    try:
        auth = getattr(supabase, "auth", None)
        if auth and hasattr(auth, "get_user"):
            current_user = auth.get_user()
            auth_user = getattr(current_user, "user", None)
            auth_user_id = getattr(auth_user, "id", None)
    except Exception:
        # Fall back to caller-provided user_id if auth context is unavailable.
        auth_user_id = None

    resolved = _normalize_required_id(auth_user_id) or _normalize_required_id(user_id)

    # Ensure subsequent inserts use the authenticated session whenever possible so
    # Postgres RLS checks relying on auth.uid() can evaluate correctly.
    if resolved and auth_user_id is None:
        try:
            auth = getattr(supabase, "auth", None)
            if auth and hasattr(auth, "set_auth"):
                auth.set_auth(resolved)
        except Exception:
            # Best effort only; caller-provided identifier remains the fallback.
            pass

    return resolved


def _best_effort_insert(table_name, payload):
    try:
        supabase.table(table_name).insert(payload).execute()
    except Exception as exc:
        # Secondary records should not block the main flight log action.
        logger.warning(
            "Secondary insert failed for table '%s': %s",
            table_name,
            exc,
        )
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
    student_id = _resolve_student_id(user_id)
    if not student_id:
        raise RuntimeError(
            "Unable to add flight to 'flights' table: missing authenticated student id."
        )

    instructor_id = _normalize_optional_id(instructor_id)
    aircraft_id = _normalize_optional_id(aircraft_id)
    rate_id = _normalize_optional_id(rate_id)

    is_solo = flight_type == "Solo"

    flight_payload = {
        "student_id": student_id,
        "instructor_id": instructor_id,
        "aircraft_id": aircraft_id,
        "rate_id": rate_id,
        "date": flight_date_str,
        "total_time": duration,
        "solo": is_solo,
        "cross_country": bool(is_xc),
        "night": bool(is_night),
    }

    try:
        result = (
            supabase.table("flights")
            .insert(flight_payload)
            .execute()
        )

    except Exception as exc:
        logger.exception(
            "Flight insert failed for user_id=%s with payload keys=%s",
            user_id,
            sorted(flight_payload.keys()),
        )
        raise RuntimeError(
            f"Unable to add flight to 'flights' table: {exc}"
        ) from exc

    flight_id = result.data[0]["id"] if result.data else None

    _best_effort_insert(
        "training_events",
        {
            "student_id": student_id,
            "instructor_id": instructor_id if not is_solo else None,
            "related_flight_id": flight_id,
            "event_type": flight_type.lower(),
            "event_value": duration,
            "notes": feedback,
        },
    )

    _best_effort_insert(
        "activity_feed",
        {
            "student_id": student_id,
            "instructor_id": instructor_id,
            "related_flight_id": flight_id,
            "event_type": flight_type.lower(),
            "event_value": duration,
            "notes": feedback,
        },
    )

    _best_effort_insert(
        "activity_feed",
        {
            "student_id": student_id,
            "activity_type": "flight",
            "title": f"Logged a {flight_type.lower()} flight",
            "description": f"{duration} hrs",
            "related_flight_id": flight_id,
            "is_public": True,
        },
    )

    check_and_unlock_milestones(student_id)