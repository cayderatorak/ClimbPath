import os
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-key")

from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock

import add_flight

STUDENT_ID = "00000000-0000-0000-0000-000000000001"


class _TableInsertExecute:
    def __init__(self, response):
        self.response = response
        self.payloads = []

    def insert(self, payload):
        self.payloads.append(payload)
        return self

    def execute(self):
        return self.response


class _TableInsertRaises(_TableInsertExecute):
    def execute(self):
        raise RuntimeError("insert failed")


class _SupabaseStub:
    def __init__(self):
        self.tables = {
            'flights': _TableInsertExecute(SimpleNamespace(data=[{'id': 42}])),
            'training_events': _TableInsertExecute(SimpleNamespace(data=[])),
            'activity_feed': _TableInsertExecute(SimpleNamespace(data=[])),
        }
        self.auth = SimpleNamespace(
            get_user=lambda: SimpleNamespace(
                user=SimpleNamespace(id=None)
            )
        )

    def table(self, name):
        return self.tables[name]


def test_add_flight_serializes_selected_date_and_links_records(monkeypatch):
    supabase_stub = _SupabaseStub()
    milestone_mock = MagicMock()

    monkeypatch.setattr(add_flight, 'supabase', supabase_stub)
    monkeypatch.setattr(add_flight, 'check_and_unlock_milestones', milestone_mock)

    add_flight.add_flight(
        user_id=STUDENT_ID,
        instructor_id='instructor-1',
        aircraft_id='aircraft-1',
        rate_id='rate-1',
        duration=1.5,
        flight_type='Solo',
        is_xc=True,
        is_night=False,
        feedback='Great landing.',
        flight_date=date(2026, 3, 17),
    )

    flights_payload = supabase_stub.tables['flights'].payloads[0]
    assert flights_payload['date'] == '2026-03-17'
    assert flights_payload['solo'] is True
    assert flights_payload['student_id'] == STUDENT_ID
    assert 'user_id' not in flights_payload

    events_payload = supabase_stub.tables['training_events'].payloads[0]
    assert events_payload['related_flight_id'] == 42
    assert events_payload['notes'] == 'Great landing.'

    feed_payload = supabase_stub.tables['activity_feed'].payloads[0]
    assert feed_payload['related_flight_id'] == 42

    milestone_mock.assert_called_once_with(STUDENT_ID)

def test_add_flight_converts_blank_foreign_keys_to_null(monkeypatch):
    supabase_stub = _SupabaseStub()
    milestone_mock = MagicMock()

    monkeypatch.setattr(add_flight, 'supabase', supabase_stub)
    monkeypatch.setattr(add_flight, 'check_and_unlock_milestones', milestone_mock)

    add_flight.add_flight(
        user_id=STUDENT_ID,
        instructor_id='   ',
        aircraft_id='',
        rate_id='',
        duration=1.0,
        flight_type='Dual',
        is_xc=False,
        is_night=False,
        feedback='',
        flight_date=date(2026, 3, 24),
    )

    flights_payload = supabase_stub.tables['flights'].payloads[0]
    assert flights_payload['instructor_id'] is None
    assert flights_payload['aircraft_id'] is None
    assert flights_payload['rate_id'] is None


def test_add_flight_converts_invalid_foreign_keys_to_null(monkeypatch):
    supabase_stub = _SupabaseStub()
    milestone_mock = MagicMock()

    monkeypatch.setattr(add_flight, 'supabase', supabase_stub)
    monkeypatch.setattr(add_flight, 'check_and_unlock_milestones', milestone_mock)

    add_flight.add_flight(
        user_id=STUDENT_ID,
        instructor_id='not-a-uuid',
        aircraft_id='also-not-a-uuid',
        rate_id='rate-123',
        duration=1.0,
        flight_type='Dual',
        is_xc=False,
        is_night=False,
        feedback='',
        flight_date=date(2026, 3, 24),
    )

    flights_payload = supabase_stub.tables['flights'].payloads[0]
    assert flights_payload['instructor_id'] is None
    assert flights_payload['aircraft_id'] is None
    assert flights_payload['rate_id'] is None


def test_add_flight_succeeds_when_secondary_inserts_fail(monkeypatch):
    supabase_stub = _SupabaseStub()
    supabase_stub.tables['training_events'] = _TableInsertRaises(SimpleNamespace(data=[]))
    supabase_stub.tables['activity_feed'] = _TableInsertRaises(SimpleNamespace(data=[]))
    milestone_mock = MagicMock()

    monkeypatch.setattr(add_flight, 'supabase', supabase_stub)
    monkeypatch.setattr(add_flight, 'check_and_unlock_milestones', milestone_mock)

    add_flight.add_flight(
        user_id=STUDENT_ID,
        instructor_id=None,
        aircraft_id=None,
        rate_id=None,
        duration=1.2,
        flight_type='Dual',
        is_xc=False,
        is_night=False,
        feedback='ok',
        flight_date=date(2026, 3, 24),
    )

    flights_payload = supabase_stub.tables['flights'].payloads[0]
    assert flights_payload['student_id'] == STUDENT_ID
    milestone_mock.assert_called_once_with(STUDENT_ID)


def test_add_flight_prefers_authenticated_user_id_for_rls(monkeypatch):
    supabase_stub = _SupabaseStub()
    supabase_stub.auth = SimpleNamespace(
        get_user=lambda: SimpleNamespace(
            user=SimpleNamespace(id="00000000-0000-0000-0000-000000000099")
        )
    )
    milestone_mock = MagicMock()

    monkeypatch.setattr(add_flight, 'supabase', supabase_stub)
    monkeypatch.setattr(add_flight, 'check_and_unlock_milestones', milestone_mock)

    add_flight.add_flight(
        user_id=STUDENT_ID,
        instructor_id=None,
        aircraft_id=None,
        rate_id=None,
        duration=1.2,
        flight_type='Dual',
        is_xc=False,
        is_night=False,
        feedback='ok',
        flight_date=date(2026, 3, 24),
    )

    flights_payload = supabase_stub.tables['flights'].payloads[0]
    assert flights_payload['student_id'] == "00000000-0000-0000-0000-000000000099"
    milestone_mock.assert_called_once_with("00000000-0000-0000-0000-000000000099")