"""DuraCapital-branded PDF export (cover, TOC, per-page logo header)."""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)
from reportlab.platypus.tableofcontents import TableOfContents

BRAND_DIR = Path(__file__).resolve().parent.parent / "assets" / "branding"
LOGO_PATH = BRAND_DIR / "duracapital_logo.png"
HERO_PATH = BRAND_DIR / "cover_hero.png"

NAVY = HexColor("#0F375A")
CYAN = HexColor("#40B4D2")
GRAY = HexColor("#4A5568")
LIGHT_GRAY = HexColor("#718096")


def _plain(value: Any, max_len: int = 8000) -> str:
    if isinstance(value, str):
        text = value
    else:
        text = json.dumps(value, default=str)
    return text[:max_len]


def _section_narrative(section: dict[str, Any]) -> str:
    content = section.get("content", {})
    if isinstance(content, dict):
        return str(content.get("content") or "")
    if content:
        return str(content)
    return ""


def _section_key_points(section: dict[str, Any]) -> list[str]:
    content = section.get("content", {})
    if isinstance(content, dict):
        points = content.get("key_points") or []
        return [str(p) for p in points if str(p).strip()]
    return []


def _section_recommendations(section: dict[str, Any]) -> list[str]:
    content = section.get("content", {})
    if not isinstance(content, dict):
        return []
    recs = content.get("recommendations") or []
    out: list[str] = []
    for rec in recs:
        if isinstance(rec, dict):
            out.append(str(rec.get("action") or rec.get("area") or rec))
        else:
            out.append(str(rec))
    return [r for r in out if r.strip()]


def _roman(n: int) -> str:
    numerals = (
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    )
    result = []
    for value, glyph in numerals:
        while n >= value:
            result.append(glyph)
            n -= value
    return "".join(result) or "I"


def _is_prompt_like(text: str) -> bool:
    """Reject LLM prompt / instruction blobs from being used as cover titles."""
    value = (text or "").strip().lower()
    if not value:
        return True
    bad_starts = (
        "you are a",
        "you are an",
        "analyze the provided",
        "generate a comprehensive",
        "# ",
        "## ",
        "[section:",
    )
    if any(value.startswith(prefix) for prefix in bad_starts):
        return True
    if "senior financial analyst" in value or "report writer" in value:
        return True
    if len(value) > 180:
        return True
    return False


def _looks_like_company_name(text: str) -> bool:
    value = (text or "").strip()
    if not value or _is_prompt_like(value):
        return False
    if value.lower() in {"financial dataset", "unknown", "n/a", "none", "null"}:
        return False
    # Avoid picking up random metric labels
    if len(value) < 2 or len(value) > 120:
        return False
    return True


def _extract_company_from_json(json_data: Any) -> str | None:
    """Find a company / institution name inside the analyzed JSON payload."""
    preferred_keys = {
        "company_name",
        "companyname",
        "company",
        "client_name",
        "clientname",
        "client",
        "bank_name",
        "bankname",
        "institution",
        "institution_name",
        "organization",
        "organisation",
        "entity",
        "entity_name",
        "issuer",
        "counterparty",
        "legal_name",
        "customer_name",
        "name",
    }

    found: list[tuple[int, str]] = []

    def scan(obj: Any, depth: int = 0) -> None:
        if depth > 8 or len(found) >= 5:
            return
        if isinstance(obj, dict):
            for key, value in obj.items():
                key_l = str(key).lower().replace(" ", "_")
                if key_l in preferred_keys:
                    if isinstance(value, str) and _looks_like_company_name(value):
                        priority = 0 if key_l in {
                            "company_name",
                            "companyname",
                            "bank_name",
                            "bankname",
                            "institution",
                            "client_name",
                            "clientname",
                            "company",
                            "client",
                        } else 1
                        found.append((priority, value.strip()))
                    elif isinstance(value, dict):
                        nested = value.get("Name") or value.get("name") or value.get("title")
                        if isinstance(nested, str) and _looks_like_company_name(nested):
                            found.append((0, nested.strip()))
                if isinstance(value, (dict, list)):
                    scan(value, depth + 1)
        elif isinstance(obj, list):
            for item in obj[:30]:
                scan(item, depth + 1)

    scan(json_data)
    if not found:
        return None
    found.sort(key=lambda item: item[0])
    return found[0][1]


def _dataset_label(report_data: dict[str, Any], metadata: dict[str, Any]) -> str:
    raw = str(report_data.get("dataset_type") or metadata.get("dataset_type") or "").strip()
    labels = {
        "wacc": "WACC Analysis",
        "money_market": "Money Market Analysis",
        "financial_instruments": "Financial Instruments Analysis",
        "credit_risk": "Credit Risk Analysis",
        "financial_statements": "Financial Statements & Ratios Analysis",
        "investment_portfolio": "Investment Portfolio Analysis",
        "market_macro": "Market & Macroeconomic Data Analysis",
        "valuation": "Valuation Analysis",
        "annual_financial": "Annual Financial Analysis",
    }
    if raw in labels:
        return labels[raw]
    title = str(metadata.get("title") or "").strip()
    if title and not _is_prompt_like(title):
        return title
    if raw:
        return raw.replace("_", " ").title() + " Analysis"
    return "Financial Analysis Report"


def _meta(report_data: dict[str, Any]) -> dict[str, Any]:
    metadata = report_data.get("metadata") or {}
    original_json = metadata.get("original_json") or report_data.get("original_json")

    company = None
    for candidate in (
        report_data.get("bank_name"),
        metadata.get("bank_name"),
        metadata.get("company_name"),
        report_data.get("company_name"),
    ):
        if isinstance(candidate, str) and _looks_like_company_name(candidate):
            company = candidate.strip()
            break

    if not company and original_json is not None:
        company = _extract_company_from_json(original_json)

    period = str(
        report_data.get("data_period")
        or metadata.get("period")
        or metadata.get("data_period")
        or ""
    ).strip()
    if period.lower() in {"unknown period", "unknown", "n/a"}:
        period = ""

    report_title = _dataset_label(report_data, metadata)
    # Never allow prompt / instruction text onto the cover.
    if _is_prompt_like(report_title):
        report_title = "Financial Analysis Report"

    cover_company = (company or "").strip()
    cover_lines: list[str] = []
    if cover_company:
        cover_lines.append(cover_company.upper())
    cover_lines.append(report_title.upper())
    if period:
        cover_lines.append(period.upper())

    return {
        "bank": cover_company or "Financial Dataset",
        "company": cover_company,
        "period": period,
        "title": report_title,
        "dataset": report_title,
        "cover_title": cover_company.upper() if cover_company else report_title.upper(),
        "cover_lines": cover_lines,
        "subtitle": report_title,
        "has_company": bool(cover_company),
    }


def _build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    styles = {
        "CoverTitle": ParagraphStyle(
            "CoverTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=22,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceBefore=12,
            spaceAfter=0,
        ),
        "ContentsHeading": ParagraphStyle(
            "ContentsHeading",
            parent=base["Heading1"],
            fontName="Helvetica",
            fontSize=18,
            leading=22,
            textColor=CYAN,
            spaceBefore=12,
            spaceAfter=14,
            alignment=TA_LEFT,
        ),
        "ReportH1": ParagraphStyle(
            "ReportH1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=NAVY,
            spaceBefore=18,
            spaceAfter=10,
        ),
        # Body subheadings — intentionally NOT registered in the TOC.
        "SectionSub": ParagraphStyle(
            "SectionSub",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=NAVY,
            spaceBefore=10,
            spaceAfter=6,
            leftIndent=8,
        ),
        "Body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=GRAY,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
        ),
        "Bullet": ParagraphStyle(
            "Bullet",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            textColor=GRAY,
            leftIndent=12,
            spaceAfter=3,
            alignment=TA_JUSTIFY,
        ),
        "TOCLevel0": ParagraphStyle(
            name="TOCLevel0",
            fontName="Helvetica",
            fontSize=11,
            leading=16,
            textColor=GRAY,
            leftIndent=0,
            firstLineIndent=0,
            spaceBefore=2,
            spaceAfter=2,
        ),
    }
    return styles


class BrandedReportDocTemplate(BaseDocTemplate):
    """Registers a brief TOC: main report sections only (keeps Contents ≤ 2 pages)."""

    def __init__(self, *args, meta: dict[str, Any] | None = None, **kwargs):
        self.meta = meta or {}
        self._logo_path = str(LOGO_PATH) if LOGO_PATH.exists() else None
        self._toc_entry_count = 0
        self._toc_entry_limit = 40
        super().__init__(*args, **kwargs)

    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return
        style_name = getattr(flowable.style, "name", "")
        # Brief TOC: top-level sections only — no key-point / subhead clutter.
        if style_name != "ReportH1":
            return
        if self._toc_entry_count >= self._toc_entry_limit:
            return
        text = flowable.getPlainText().strip()
        if not text:
            return
        self.notify("TOCEntry", (0, text, self.page))
        self._toc_entry_count += 1


def _draw_content_header(canvas, doc: BrandedReportDocTemplate):
    canvas.saveState()
    width, height = A4
    meta = doc.meta or {}

    # Left metadata block (matches sample TOC page)
    canvas.setFillColor(GRAY)
    canvas.setFont("Helvetica", 9)
    y = height - 14 * mm
    left_lines = [
        meta.get("bank") or "",
        meta.get("subtitle") or meta.get("dataset") or "",
        meta.get("period") or "",
    ]
    for line in left_lines:
        if line:
            canvas.drawString(18 * mm, y, line[:70])
            y -= 4.2 * mm

    # Logo upper-right on every content/TOC page
    if doc._logo_path:
        logo_w = 42 * mm
        logo_h = 12 * mm
        canvas.drawImage(
            doc._logo_path,
            width - 18 * mm - logo_w,
            height - 18 * mm,
            width=logo_w,
            height=logo_h,
            preserveAspectRatio=True,
            mask="auto",
        )

    # Subtle separator under header
    canvas.setStrokeColor(HexColor("#E2E8F0"))
    canvas.setLineWidth(0.4)
    canvas.line(18 * mm, height - 22 * mm, width - 18 * mm, height - 22 * mm)

    # Page number bottom-center
    canvas.setFillColor(LIGHT_GRAY)
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(width / 2, 12 * mm, str(doc.page))
    canvas.restoreState()


def _wrap_centered_lines(text: str, max_chars: int = 36) -> list[str]:
    words = str(text or "").split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if len(trial) <= max_chars:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [str(text or "")]


def _draw_cover_page(canvas, doc: BrandedReportDocTemplate):
    """Dynamic cover: logo, decorative graphic, company name + report title from JSON."""
    canvas.saveState()
    width, height = A4
    meta = doc.meta or {}

    # Clean white cover (never use sample cover art — it contains hardcoded names).
    canvas.setFillColor(white)
    canvas.rect(0, 0, width, height, fill=1, stroke=0)

    # DuraCapital logo — top left
    if doc._logo_path:
        canvas.drawImage(
            doc._logo_path,
            18 * mm,
            height - 28 * mm,
            width=52 * mm,
            height=15 * mm,
            preserveAspectRatio=True,
            mask="auto",
        )

    # Decorative data graphic — top right / upper band (no baked-in text)
    if HERO_PATH.exists():
        canvas.drawImage(
            str(HERO_PATH),
            width * 0.28,
            height * 0.42,
            width=width * 0.68,
            height=height * 0.38,
            preserveAspectRatio=True,
            mask="auto",
        )

    # Dynamic text block centered on the lower half
    cover_lines = meta.get("cover_lines") or []
    if isinstance(cover_lines, str):
        cover_lines = [cover_lines]
    if not cover_lines:
        cover_lines = [meta.get("cover_title") or meta.get("title") or "FINANCIAL ANALYSIS REPORT"]

    canvas.setFillColor(NAVY)
    y = height * 0.36
    for index, raw_line in enumerate(cover_lines):
        line = str(raw_line or "").strip()
        if not line or _is_prompt_like(line):
            continue
        font_size = 16 if index == 0 else 12
        canvas.setFont("Helvetica-Bold", font_size)
        for wrapped in _wrap_centered_lines(line, max_chars=40 if index == 0 else 48):
            canvas.drawCentredString(width / 2, y, wrapped)
            y -= (7.2 if index == 0 else 5.5) * mm
        y -= 3 * mm

    canvas.restoreState()


def _cover_flowables(meta: dict[str, Any], styles: dict[str, ParagraphStyle], page_width: float) -> list:
    """Cover artwork is drawn on the canvas; keep a spacer so the cover page exists."""
    return [Spacer(1, 10 * mm)]


def _toc_flowable(styles: dict[str, ParagraphStyle]) -> TableOfContents:
    """Compact single-level table of contents (main sections only)."""
    toc = TableOfContents()
    toc.levelStyles = [styles["TOCLevel0"]]
    return toc


def generate_branded_pdf_report(report_data: dict[str, Any]) -> bytes:
    """Build a DuraCapital-branded PDF with cover, TOC, and section body."""
    meta = _meta(report_data)
    styles = _build_styles()
    sections = list(report_data.get("comprehensive_analysis") or [])

    buffer = io.BytesIO()
    doc = BrandedReportDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=28 * mm,
        bottomMargin=18 * mm,
        title=meta["title"],
        author="DuraCapital",
        meta=meta,
    )

    page_width, page_height = A4
    cover_frame = Frame(
        18 * mm,
        18 * mm,
        page_width - 36 * mm,
        page_height - 36 * mm,
        id="cover",
    )
    content_frame = Frame(
        18 * mm,
        18 * mm,
        page_width - 36 * mm,
        page_height - 46 * mm,
        id="normal",
    )

    doc.addPageTemplates(
        [
            PageTemplate(id="Cover", frames=cover_frame, onPage=_draw_cover_page),
            PageTemplate(id="Content", frames=content_frame, onPage=_draw_content_header),
        ]
    )

    story: list = []
    story.extend(_cover_flowables(meta, styles, page_width))
    story.append(NextPageTemplate("Content"))
    story.append(PageBreak())

    # Table of contents (entries filled during multiBuild)
    story.append(Paragraph("Contents", styles["ContentsHeading"]))
    toc = _toc_flowable(styles)
    story.append(toc)
    story.append(PageBreak())

    if not sections:
        story.append(Paragraph("AI Analysis", styles["ReportH1"]))
        ai_analysis = report_data.get("ai_analysis") or {}
        if isinstance(ai_analysis, dict):
            for key, value in ai_analysis.items():
                story.append(Paragraph(escape(str(key).replace("_", " ").title()), styles["SectionSub"]))
                story.append(Paragraph(escape(_plain(value, 4000)), styles["Body"]))
        else:
            story.append(Paragraph(escape(_plain(ai_analysis, 4000)), styles["Body"]))
    else:
        for index, section in enumerate(sections, start=1):
            title = str(section.get("title") or f"Section {index}")
            story.append(Paragraph(f"{index}. {escape(title)}", styles["ReportH1"]))

            narrative = _section_narrative(section)
            if narrative:
                story.append(Paragraph(escape(_plain(narrative, 12000)), styles["Body"]))

            # Key points stay in the body only — they are not listed in Contents.
            key_points = _section_key_points(section)
            for sub_index, point in enumerate(key_points[:8], start=1):
                story.append(
                    Paragraph(
                        f"{_roman(sub_index)}. {escape(_plain(point, 500))}",
                        styles["SectionSub"],
                    )
                )

            recommendations = _section_recommendations(section)
            if recommendations:
                story.append(Paragraph("Recommendations", styles["SectionSub"]))
                bullets = [
                    ListItem(Paragraph(escape(_plain(rec, 800)), styles["Bullet"]), leftIndent=10)
                    for rec in recommendations[:10]
                ]
                story.append(ListFlowable(bullets, bulletType="bullet", start="•"))

            story.append(Spacer(1, 6 * mm))

    doc.multiBuild(story)
    buffer.seek(0)
    return buffer.getvalue()
