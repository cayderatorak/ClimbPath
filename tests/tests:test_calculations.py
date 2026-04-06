import pandas as pd

from calculations import calculate_totals


def test_calculate_totals_handles_missing_optional_columns():
    df = pd.DataFrame(
        [
            {"total_time": 1.5},
            {"total_time": 2.0},
        ]
    )

    totals, returned_df = calculate_totals(df)

    assert totals == {"Dual": 3.5, "Solo": 0.0, "XC": 0.0, "Night": 0.0, "Total": 3.5}
    assert returned_df is df


def test_calculate_totals_total_matches_logged_time_without_double_counting():
    df = pd.DataFrame(
        [
            {"total_time": 1.0, "solo": False, "cross_country": False, "night": False},
            {"total_time": 2.0, "solo": True, "cross_country": True, "night": False},
            {"total_time": 1.5, "solo": False, "cross_country": False, "night": True},
        ]
    )

    totals, _ = calculate_totals(df)

    assert totals["Dual"] == 2.5
    assert totals["Solo"] == 2.0
    assert totals["XC"] == 2.0
    assert totals["Night"] == 1.5
    assert totals["Total"] == 4.5