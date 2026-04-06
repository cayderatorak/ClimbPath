import pandas as pd

from solo import calculate_solo_readiness, predict_solo


def test_calculate_solo_readiness_handles_missing_solo_column():
    df = pd.DataFrame([{"total_time": 1.5}, {"total_time": 2.0}])

    readiness = calculate_solo_readiness(df)

    assert readiness == 0


def test_predict_solo_handles_missing_solo_column():
    df = pd.DataFrame(
        [
            {"total_time": 10.0, "created_at": "2026-03-01T00:00:00Z"},
            {"total_time": 3.0, "created_at": "2026-03-08T00:00:00Z"},
        ]
    )

    result = predict_solo(df, hours_per_week=2, targets={"Solo": 10})

    assert result["status"] == "in_progress"
    assert result["solo_hours_remaining"] == 10