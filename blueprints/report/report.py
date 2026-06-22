from extensions import Blueprint, role_required
from flask import send_file
from models import Booking, Resource, EquipmentRequest
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
)

reportBp = Blueprint("report", __name__, url_prefix="/api/report")

# Reporting is a manager/admin capability (Export Report button).
REPORTERS = ("manager", "admin")


@reportBp.get("/export")
@role_required(*REPORTERS)
def export_pdf():
    """Generate the system summary report as a downloadable PDF."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=20 * mm, bottomMargin=20 * mm,
        leftMargin=18 * mm, rightMargin=18 * mm,
        title="CRBS System Report",
    )
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Campus Resource Booking System", styles["Title"]))
    story.append(Paragraph(
        "System Summary Report &mdash; generated "
        + datetime.now().strftime("%d %b %Y, %H:%M"),
        styles["Normal"],
    ))
    story.append(Spacer(1, 8 * mm))

    # --- Overview counts -------------------------------------------------
    total_resources = Resource.query.count()
    available = Resource.query.filter_by(status="available").count()
    total_bookings = Booking.query.count()
    pending_eq = EquipmentRequest.query.filter_by(status="pending").count()

    story.append(Paragraph("Overview", styles["Heading2"]))
    story.append(_table([
        ["Metric", "Value"],
        ["Total resources", str(total_resources)],
        ["Available resources", str(available)],
        ["Total bookings", str(total_bookings)],
        ["Pending equipment requests", str(pending_eq)],
    ], col_widths=[110 * mm, 50 * mm]))
    story.append(Spacer(1, 8 * mm))

    # --- Bookings by status ---------------------------------------------
    story.append(Paragraph("Bookings by Status", styles["Heading2"]))
    status_rows = [["Status", "Count"]]
    for status in ("confirmed", "pending", "checked_in", "cancelled", "no_show"):
        status_rows.append(
            [status, str(Booking.query.filter_by(status=status).count())]
        )
    story.append(_table(status_rows, col_widths=[110 * mm, 50 * mm]))
    story.append(Spacer(1, 8 * mm))

    # --- Resource status detail -----------------------------------------
    story.append(Paragraph("Resource Status", styles["Heading2"]))
    res_rows = [["Resource", "Type", "Capacity", "Status"]]
    for r in Resource.query.order_by(Resource.name).all():
        res_rows.append([r.name, r.type, str(r.capacity), r.status])
    story.append(_table(res_rows, col_widths=[70 * mm, 45 * mm, 25 * mm, 30 * mm]))

    doc.build(story)
    buffer.seek(0)

    filename = f"crbs-report-{datetime.now():%Y%m%d-%H%M}.pdf"
    return send_file(
        buffer, mimetype="application/pdf",
        as_attachment=True, download_name=filename,
    )


def _table(rows, col_widths):
    """Build a styled table with a coloured header row."""
    table = Table(rows, colWidths=col_widths, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0c4a6e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table
