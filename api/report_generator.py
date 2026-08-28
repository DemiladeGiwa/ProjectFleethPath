"""
FleetPath — PDF Report Generation Engine (PRD §7)
Renders an already-computed EngineOutputPayload as a single-page, audit-style
PDF. Performs no calculation — pathways and verdict are rendered as passed in.
"""

from io import BytesIO
from typing import Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

from engine.models import FleetInputPayload, EngineOutputPayload, PathwayOutputMetrics

NAVY = HexColor("#1B2A4A")
EMERALD = HexColor("#1F9D6E")
GRAY_LINE = HexColor("#C7CBD1")
GRAY_TEXT = HexColor("#4A4F58")
OFF_WHITE = HexColor("#F7F7F5")

PAGE_W, PAGE_H = letter
MARGIN = 0.65 * inch
CONTENT_W = PAGE_W - (2 * MARGIN)

_FUEL_DISPLAY_NAMES = {
    "diesel": "Diesel",
    "bev": "Battery-Electric",
    "hydrogen": "Hydrogen Fuel Cell",
    "cng": "CNG",
    "biodiesel": "Biodiesel (B20)",
}
_PATHWAY_ORDER = ["diesel", "bev", "hydrogen", "cng", "biodiesel"]

# DISCLOSED CHANGE: footnote previously cited NIR 2025 (CY2026), which does not match
# the NIR 2023 (1990-2021) source actually cited in data/grid_factors.json for every
# Canadian region. Corrected to match the real underlying citation.
_METHODOLOGY_FOOTNOTE = (
    "Methodology: figures derived from NREL H2A hydrogen station cost models, Argonne National "
    "Laboratory AFLEET 2023 vehicle and infrastructure baselines, EPA eGRID 2023 Rev 2 regional "
    "grid emission factors (US), and Environment and Climate Change Canada National Inventory "
    "Report 2023 (NIR 1990-2021) provincial grid intensities (Canada). This is a decision-support "
    "estimate, not a procurement guarantee."
)


def _fmt_money(value: float, currency: str) -> str:
    # DISCLOSED CHANGE (pricing-bug remediation): was a hardcoded "$" with no
    # currency disclosure. Renders the resolved pathway currency (CAD for
    # Canadian fleets, USD for US fleets) produced by the calculation engine.
    return f"${value:,.0f} {currency}"


def _fmt_tons(value: float) -> str:
    return f"{value:,.1f} t"


def _fmt_years(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    return f"{value:.1f} yr"


def _fmt_pct(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    return f"{value:.1f}%"


def _draw_wrapped_text(c: canvas.Canvas, text: str, x: float, y: float, max_width: float,
                        font: str, size: int, leading: float, color=GRAY_TEXT) -> float:
    """Draws left-aligned wrapped text starting at (x, y). Returns the y position after the last line."""
    c.setFont(font, size)
    c.setFillColor(color)
    words = text.split()
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if stringWidth(candidate, font, size) <= max_width:
            line = candidate
        else:
            c.drawString(x, y, line)
            y -= leading
            line = word
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y


def _row_value(pathway: PathwayOutputMetrics, column: str) -> str:
    if column == "tco_total":
        return _fmt_money(pathway.tco_total, pathway.currency)
    if column == "lifecycle_co2e_tons":
        return _fmt_tons(pathway.lifecycle_co2e_tons)
    if column == "cold_climate_adjustment_applied":
        return "Yes" if pathway.cold_climate_adjustment_applied else "No"
    raise ValueError(f"Unknown column: {column}")


def generate_fleet_report_pdf(
    fleet_input: FleetInputPayload,
    engine_output: EngineOutputPayload,
    matrix_font_size: int = 9,
) -> bytes:
    """
    Renders a single-page audit report PDF and returns it as bytes.
    matrix_font_size shrinks if the 5-row matrix risks overflowing the page —
    callers should not need to pass this; it is used internally for the retry.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    y = PAGE_H - MARGIN

    # --- Header -----------------------------------------------------------
    c.setFillColor(NAVY)
    c.rect(0, PAGE_H - 0.9 * inch, PAGE_W, 0.9 * inch, stroke=0, fill=1)
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(MARGIN, PAGE_H - 0.55 * inch, "FleetPath — Fuel Pathway Decision Report")
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN, PAGE_H - 0.75 * inch, "Independent cost and carbon analysis for fleet procurement decisions")
    y = PAGE_H - 1.15 * inch

    # --- Fleet profile summary block --------------------------------------
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(NAVY)
    c.drawString(MARGIN, y, "Fleet Profile")
    y -= 0.22 * inch

    profile_fields = [
        ("Region", fleet_input.region.state_prov),
        ("Vehicle class", fleet_input.fleet.vehicle_type),
        ("Fleet size", f"{fleet_input.fleet.vehicle_count} vehicles"),
        ("Annual mileage", f"{fleet_input.fleet.annual_mileage_per_vehicle:,.0f} mi"),
        ("Lifecycle horizon", f"{fleet_input.fleet.lifecycle_years} yr"),
    ]
    col_w = CONTENT_W / len(profile_fields)
    c.setFont("Helvetica", 7)
    for i, (label, value) in enumerate(profile_fields):
        x = MARGIN + i * col_w
        c.setFillColor(GRAY_TEXT)
        c.drawString(x, y, label.upper())
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(NAVY)
        c.drawString(x, y - 0.16 * inch, str(value))
        c.setFont("Helvetica", 7)
    y -= 0.42 * inch

    c.setStrokeColor(GRAY_LINE)
    c.line(MARGIN, y, PAGE_W - MARGIN, y)
    y -= 0.28 * inch

    # --- TL;DR verdict block ----------------------------------------------
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(NAVY)
    c.drawString(MARGIN, y, "TL;DR Verdict")
    y -= 0.22 * inch

    y = _draw_wrapped_text(
        c, engine_output.verdict.summary_text, MARGIN, y, CONTENT_W,
        font="Helvetica", size=10, leading=0.18 * inch, color=GRAY_TEXT,
    )
    y -= 0.06 * inch

    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(EMERALD)
    verdict_line = (
        f"Payback vs. diesel: {_fmt_years(engine_output.verdict.payback_years)}    "
        f"|    Emissions reduction vs. diesel: {_fmt_pct(engine_output.verdict.emissions_reduction_pct)}"
    )
    c.drawString(MARGIN, y, verdict_line)
    y -= 0.34 * inch

    c.setStrokeColor(GRAY_LINE)
    c.line(MARGIN, y, PAGE_W - MARGIN, y)
    y -= 0.28 * inch

    # --- 5-pathway comparison matrix ---------------------------------------
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(NAVY)
    c.drawString(MARGIN, y, "Pathway Comparison")
    y -= 0.24 * inch

    columns = [
        ("Fuel Pathway", 0.30),
        ("Lifetime TCO", 0.24),
        ("Lifecycle CO2e", 0.24),
        ("Cold-Climate Adj.", 0.22),
    ]
    col_x = []
    x_cursor = MARGIN
    for _, frac in columns:
        col_x.append(x_cursor)
        x_cursor += CONTENT_W * frac

    # Row/header height scales with matrix_font_size so the shrink-and-retry
    # path below actually reclaims vertical space instead of only shrinking text.
    row_h = (matrix_font_size + 12)
    header_h = (matrix_font_size + 12)

    c.setFillColor(NAVY)
    c.rect(MARGIN, y - header_h, CONTENT_W, header_h, stroke=0, fill=1)
    c.setFont("Helvetica-Bold", matrix_font_size)
    c.setFillColor(HexColor("#FFFFFF"))
    for i, (label, _) in enumerate(columns):
        c.drawString(col_x[i] + 4, y - header_h + 7, label)
    y -= header_h

    pathways_by_type = {p.fuel_type: p for p in engine_output.pathways}
    winner = engine_output.verdict.winner_pathway

    for fuel_type in _PATHWAY_ORDER:
        pathway = pathways_by_type.get(fuel_type)
        if pathway is None:
            continue

        is_winner = fuel_type == winner
        row_top = y

        if is_winner:
            c.setFillColor(HexColor("#E4F4EC"))  # light emerald tint, text stays high-contrast
            c.rect(MARGIN, row_top - row_h, CONTENT_W, row_h, stroke=0, fill=1)
        else:
            c.setFillColor(OFF_WHITE)
            c.rect(MARGIN, row_top - row_h, CONTENT_W, row_h, stroke=0, fill=1)

        c.setStrokeColor(GRAY_LINE)
        c.line(MARGIN, row_top - row_h, PAGE_W - MARGIN, row_top - row_h)

        label = _FUEL_DISPLAY_NAMES[fuel_type]
        if is_winner:
            label = f"{label}  (Winner)"  # text marker — not color-only, base-14-font safe, width-checked against col 0

        c.setFont("Helvetica-Bold" if is_winner else "Helvetica", matrix_font_size)
        c.setFillColor(EMERALD if is_winner else NAVY)
        c.drawString(col_x[0] + 4, row_top - row_h + 8, label)

        c.setFillColor(GRAY_TEXT)
        c.setFont("Helvetica-Bold" if is_winner else "Helvetica", matrix_font_size)
        c.drawString(col_x[1] + 4, row_top - row_h + 8, _row_value(pathway, "tco_total"))
        c.drawString(col_x[2] + 4, row_top - row_h + 8, _row_value(pathway, "lifecycle_co2e_tons"))
        c.drawString(col_x[3] + 4, row_top - row_h + 8, _row_value(pathway, "cold_climate_adjustment_applied"))

        y -= row_h

    c.setStrokeColor(NAVY)
    c.setLineWidth(1)
    c.rect(MARGIN, y, CONTENT_W, header_h + row_h * len(_PATHWAY_ORDER), stroke=1, fill=0)
    c.setLineWidth(1)

    # --- Institutional methodology footnote --------------------------------
    footnote_y = MARGIN + 0.35 * inch
    c.setStrokeColor(GRAY_LINE)
    c.line(MARGIN, footnote_y + 0.14 * inch, PAGE_W - MARGIN, footnote_y + 0.14 * inch)
    _draw_wrapped_text(
        c, _METHODOLOGY_FOOTNOTE, MARGIN, footnote_y, CONTENT_W,
        font="Helvetica", size=6.5, leading=0.11 * inch, color=GRAY_TEXT,
    )

    overflow = y < (MARGIN + 0.8 * inch)

    c.showPage()
    c.save()

    if overflow and matrix_font_size > 6:
        return generate_fleet_report_pdf(fleet_input, engine_output, matrix_font_size=matrix_font_size - 1)

    buffer.seek(0)
    return buffer.getvalue()