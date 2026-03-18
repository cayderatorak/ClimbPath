import os
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-key")

import unittest
from unittest.mock import patch

from postgrest.exceptions import APIError

import load_data
import sidebar


class LoadDataTests(unittest.TestCase):
    def test_load_student_flights_returns_empty_frame_on_api_error(self):
        with patch.object(load_data.supabase, "table") as table_mock:
            table_mock.return_value.select.return_value.eq.return_value.execute.side_effect = APIError({"message": "boom"})

            df = load_data.load_student_flights("student-123")

        self.assertTrue(df.empty)
        self.assertEqual(list(df.columns), load_data.FLIGHT_COLUMNS)

    def test_load_student_flights_returns_empty_frame_when_student_id_missing(self):
        df = load_data.load_student_flights(None)

        self.assertTrue(df.empty)
        self.assertEqual(list(df.columns), load_data.FLIGHT_COLUMNS)

    def test_load_student_feedback_notes_filters_blank_notes(self):
        payload = [
            {"notes": "Needs more right rudder", "created_at": "2026-03-18", "event_type": "lesson"},
            {"notes": "   ", "created_at": "2026-03-18", "event_type": "lesson"},
            {"notes": None, "created_at": "2026-03-18", "event_type": "lesson"},
        ]

        with patch.object(load_data.supabase, "table") as table_mock:
            table_mock.return_value.select.return_value.eq.return_value.execute.return_value.data = payload

            df = load_data.load_student_feedback_notes("student-123")

        self.assertEqual(df["notes"].tolist(), ["Needs more right rudder"])

    def test_load_student_feedback_notes_returns_empty_frame_on_unexpected_error(self):
        with patch.object(load_data.supabase, "table") as table_mock:
            table_mock.return_value.select.return_value.eq.return_value.execute.side_effect = RuntimeError("boom")

            df = load_data.load_student_feedback_notes("student-123")

        self.assertTrue(df.empty)
        self.assertEqual(list(df.columns), load_data.FEEDBACK_COLUMNS)
        

class SidebarUserValueTests(unittest.TestCase):
    def test_user_value_supports_dicts_and_objects(self):
        user_dict = {"id": "dict-id", "email": "dict@example.com"}
        user_obj = type("User", (), {"id": "obj-id", "email": "obj@example.com"})()

        self.assertEqual(sidebar._user_value(user_dict, "id"), "dict-id")
        self.assertEqual(sidebar._user_value(user_obj, "email"), "obj@example.com")


if __name__ == "__main__":
    unittest.main()
