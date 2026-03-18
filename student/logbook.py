import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from database import supabase

def logbook_section(df):
    st.markdown("### Flight Logbook")
    display_df = df.drop(columns=["student_id"],errors="ignore")
    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_columns(display_df.columns,editable=True)
    gb.configure_selection("single")
    grid = AgGrid(display_df, gridOptions=gb.build(), update_mode=GridUpdateMode.MODEL_CHANGED, height=400)
    updated = pd.DataFrame(grid["data"])

    selected = grid["selected_rows"]
    if selected:
        flight_id = selected[0]["id"]
        if st.button("Delete Flight"):
            supabase.table("flights").delete().eq("id",flight_id).execute()
            st.success("Flight deleted")
            st.rerun()

    csv = updated.to_csv(index=False).encode()
    st.download_button("Download CSV", csv, "climbpath_logbook.csv")