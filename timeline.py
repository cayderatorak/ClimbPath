# ------------------ TRAINING TIMELINE ------------------
st.markdown("### Training Timeline")

total_hours = totals["Total"]

solo_progress = min(total_hours / TRACKS[track]["Solo"],1)
xc_progress = min(total_hours / TRACKS[track]["XC"],1)
checkride_progress = min(total_hours / TRACKS[track]["Total"],1)

timeline = [
("Start Training",1),
("Solo",solo_progress),
("Cross Country",xc_progress),
("Checkride",checkride_progress)
]

cols = st.columns(len(timeline))

for col,(label,progress) in zip(cols,timeline):

    if progress >= 1:
        status="✔"
    elif progress > 0:
        status="●"
    else:
        status="○"

    col.metric(label,status)