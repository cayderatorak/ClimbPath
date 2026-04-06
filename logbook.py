import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

from database import supabase


NON_EDITABLE_COLUMNS = {"id", "student_id", "created_at"}
TABLE_COLUMNS = [
    "tail number",
    "instructor name",
    "date of flight",
    "total time",
    "dual time",
    "solo time",
    "cross country",
    "night",
    "flight cost",
]

def _selected_rows_to_records(selected_rows):
    if selected_rows is None:
        return []
    if isinstance(selected_rows, pd.DataFrame):
        return selected_rows.to_dict("records")
    if isinstance(selected_rows, dict):
        return [selected_rows]
    if isinstance(selected_rows, list):
        return selected_rows
    return []


EDITABLE_COLUMNS = {
    "tail number",
    "instructor name",
    "date of flight",
    "total time",
    "cross country",
    "night",
}


def _display_flight_table(df):
    table = pd.DataFrame(index=df.index)
    table["_row_id"] = df.get("id")

    table["tail number"] = (
        df.get("tail_number")
        .fillna(df.get("aircraft_tail_number", ""))
        if "tail_number" in df.columns or "aircraft_tail_number" in df.columns
        else ""
    )
    table["instructor name"] = (
        df.get("instructor_name")
        .fillna("")
        if "instructor_name" in df.columns
        else ""
    )

    date_series = (
        df.get("date")
        if "date" in df.columns
        else df.get("created_at", "")
    )
    table["date of flight"] = pd.to_datetime(date_series, errors="coerce").dt.date

    total_time = pd.to_numeric(df.get("total_time"), errors="coerce") if "total_time" in df.columns else pd.Series(0.0, index=df.index)
    total_time = total_time.fillna(0.0)

    solo_flag = df.get("solo") if "solo" in df.columns else pd.Series(False, index=df.index)
    solo_flag = solo_flag.fillna(False).astype(bool)

    cross_country = df.get("cross_country") if "cross_country" in df.columns else pd.Series(False, index=df.index)
    night = df.get("night") if "night" in df.columns else pd.Series(False, index=df.index)

    table["total time"] = total_time.round(1)
    table["dual time"] = total_time.where(~solo_flag, 0).round(1)
    table["solo time"] = total_time.where(solo_flag, 0).round(1)
    table["cross country"] = cross_country.fillna(False).astype(bool)
    table["night"] = night.fillna(False).astype(bool)
    table["flight cost"] = pd.to_numeric(df.get("flight_cost", 0), errors="coerce").fillna(0.0).round(2)

    return table[["_row_id", *TABLE_COLUMNS]]


def _normalize_date_for_db(value):
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date().isoformat()


def _build_flights_update_payload(df, original_row, updated_row):
    payload = {}

    if original_row.get("date of flight") != updated_row.get("date of flight"):
        payload["date"] = _normalize_date_for_db(updated_row.get("date of flight"))

    if original_row.get("total time") != updated_row.get("total time"):
        payload["total_time"] = float(updated_row.get("total time") or 0)

    if original_row.get("cross country") != updated_row.get("cross country"):
        payload["cross_country"] = bool(updated_row.get("cross country"))

    if original_row.get("night") != updated_row.get("night"):
        payload["night"] = bool(updated_row.get("night"))

    if (
        "instructor_name" in df.columns
        and original_row.get("instructor name") != updated_row.get("instructor name")
    ):
        payload["instructor_name"] = updated_row.get("instructor name") or None

    tail_value_changed = original_row.get("tail number") != updated_row.get("tail number")
    if tail_value_changed:
        if "tail_number" in df.columns:
            payload["tail_number"] = updated_row.get("tail number") or None
        elif "aircraft_tail_number" in df.columns:
            payload["aircraft_tail_number"] = updated_row.get("tail number") or None

    return payload



def logbook_section(df):
    st.markdown("### Flight Logbook")

    display_df = _display_flight_table(df)

    gb = GridOptionsBuilder.from_dataframe(display_df)
    for column in display_df.columns:
        if column == "_row_id":
            gb.configure_column(column, hide=True, editable=False)
        else:
            gb.configure_column(column, editable=column in EDITABLE_COLUMNS)
    gb.configure_selection("single")

    grid = AgGrid(
        display_df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.MODEL_CHANGED,
        height=400,
    )
    updated = pd.DataFrame(grid["data"])

    if st.button("Save Edits", type="primary"):
        if "_row_id" not in updated.columns:
            st.error("Unable to save edits because row IDs are missing.")
        else:
            original_rows = display_df.set_index("_row_id").to_dict("index")
            updates_applied = 0

            for _, row in updated.iterrows():
                flight_id = row.get("_row_id")
                if not flight_id or flight_id not in original_rows:
                    continue

                original_row = original_rows[flight_id]
                payload = _build_flights_update_payload(df, original_row, row.to_dict())
                if not payload:
                    continue

                supabase.table("flights").update(payload).eq("id", flight_id).execute()
                updates_applied += 1

            if updates_applied:
                st.success(f"Saved edits for {updates_applied} flight(s).")
                st.rerun()
            else:
                st.info("No changes detected.")

    selected_records = _selected_rows_to_records(grid.get("selected_rows"))
    if selected_records:
        flight_id = selected_records[0].get("_row_id")
        if flight_id and st.button("Delete Flight"):
            supabase.table("flights").delete().eq("id", flight_id).execute()
            st.success("Flight deleted")
            st.rerun()


    csv = updated[TABLE_COLUMNS].to_csv(index=False).encode()
    st.download_button("Download CSV", csv, "climbpath_logbook.csv")