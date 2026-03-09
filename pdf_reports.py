from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from io import BytesIO

def generate_training_report(student_name, total_hours, solo_hours, xc_hours):

    buffer = BytesIO()

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("ClimbPath Training Report", styles["Title"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph(f"Student: {student_name}", styles["Normal"]))
    story.append(Paragraph(f"Total Flight Hours: {total_hours}", styles["Normal"]))
    story.append(Paragraph(f"Solo Hours: {solo_hours}", styles["Normal"]))
    story.append(Paragraph(f"Cross Country Hours: {xc_hours}", styles["Normal"]))

    story.append(Spacer(1, 20))

    data = [
        ["Category", "Hours"],
        ["Total Time", total_hours],
        ["Solo Time", solo_hours],
        ["Cross Country", xc_hours]
    ]

    table = Table(data)
    story.append(table)

    doc = SimpleDocTemplate(buffer, pagesize=letter)
    doc.build(story)

    buffer.seek(0)
    return buffer
