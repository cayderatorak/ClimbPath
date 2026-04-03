import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

from database import supabase


NON_EDITABLE_COLUMNS = {"id", "student_id", "created_at"}


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


def _build_update_payload(original_row, updated_row):
    payload = {}
    for column, new_value in updated_row.items():
        if column in NON_EDITABLE_COLUMNS:
            continue

        old_value = original_row.get(column)

        # Normalize NaN comparisons.
        if pd.isna(old_value) and pd.isna(new_value):
            continue

        if old_value != new_value:
            payload[column] = None if pd.isna(new_value) else new_value

    return payload



def logbook_section(df):
    st.markdown("### Flight Logbook")

    display_df = df.drop(columns=["student_id"], errors="ignore").copy()

    gb = GridOptionsBuilder.from_dataframe(display_df)
    for column in display_df.columns:
        gb.configure_column(column, editable=column not in NON_EDITABLE_COLUMNS)
    gb.configure_selection("single")

    grid = AgGrid(
        display_df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.MODEL_CHANGED,
        height=400,
    )
    updated = pd.DataFrame(grid["data"])


    if st.button("Save Edits", type="primary"):
        if "id" not in display_df.columns or "id" not in updated.columns:
            st.error("Unable to save edits because flight IDs are missing.")
        else:
            original_rows = display_df.set_index("id").to_dict("index")
            updates_applied = 0

            for _, row in updated.iterrows():
                flight_id = row.get("id")
                if not flight_id or flight_id not in original_rows:
                    continue

                payload = _build_update_payload(original_rows[flight_id], row.to_dict())
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
        flight_id = selected_records[0].get("id")
        if flight_id and st.button("Delete Flight"):
            supabase.table("flights").delete().eq("id", flight_id).execute()
            st.success("Flight deleted")
            st.rerun()


    csv = updated.to_csv(index=False).encode()
    st.download_button("Download CSV", csv, "climbpath_logbook.csv")