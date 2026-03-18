import os
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-key")

from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock

import add_flight


class _TableInsertExecute:
    def __init__(self, response):
        self.response = response
        self.payloads = []

    def insert(self, payload):
        self.payloads.append(payload)
        return self

    def execute(self):
        return self.response


class _SupabaseStub:
    def __init__(self):
        self.tables = {
            'flights': _TableInsertExecute(SimpleNamespace(data=[{'id': 42}])),
            'training_events': _TableInsertExecute(SimpleNamespace(data=[])),
            'activity_feed': _TableInsertExecute(SimpleNamespace(data=[])),
        }

    def table(self, name):
        return self.tables[name]


def test_add_flight_serializes_selected_date_and_links_records(monkeypatch):
    supabase_stub = _SupabaseStub()
    milestone_mock = MagicMock()

    monkeypatch.setattr(add_flight, 'supabase', supabase_stub)
    monkeypatch.setattr(add_flight, 'check_and_unlock_milestones', milestone_mock)

    add_flight.add_flight(
        user_id='student-1',
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
    assert flights_payload['created_at'] == '2026-03-17T00:00:00'
    assert flights_payload['solo'] is True

    events_payload = supabase_stub.tables['training_events'].payloads[0]
    assert events_payload['related_flight_id'] == 42
    assert events_payload['notes'] == 'Great landing.'

    feed_payload = supabase_stub.tables['activity_feed'].payloads[0]
    assert feed_payload['related_id'] == 42

    milestone_mock.assert_called_once_with('student-1')
