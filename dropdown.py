import streamlit as st

aircraft = get_aircraft()
instructors = get_instructors()

# Aircraft dropdown
aircraft_options = {f"{a['tail_number']} ({a['type']})": a['id'] for a in aircraft}
selected_aircraft_label = st.selectbox("Select Aircraft", list(aircraft_options.keys()))
selected_aircraft_id = aircraft_options[selected_aircraft_label]

# Instructor dropdown
instructor_options = {i['name']: i['id'] for i in instructors}
selected_instructor_label = st.selectbox("Select Instructor", list(instructor_options.keys()))
selected_instructor_id = instructor_options[selected_instructor_label]