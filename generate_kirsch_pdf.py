"""
Adam Kirsch CTE Courses — College Now Eligibility Analysis
Generates a professional PDF for the 509j CTE Alignment Project
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus.flowables import Flowable
import os

OUTPUT = "/Users/andymcateer/Desktop/Claude Projects/01_TEACHING/CTE_Alignment_Project/Kirsch_CollegeNow_Analysis_FINAL.pdf"

# ── Brand Colors ─────────────────────────────────────────────────────────────
NAVY      = colors.HexColor("#1a2744")
BLUE      = colors.HexColor("#2563eb")
TEAL      = colors.HexColor("#0891b2")
GREEN     = colors.HexColor("#16a34a")
AMBER     = colors.HexColor("#d97706")
RED       = colors.HexColor("#dc2626")
LIGHT_BG  = colors.HexColor("#f0f4ff")
MID_GRAY  = colors.HexColor("#64748b")
RULE_GRAY = colors.HexColor("#e2e8f0")
WHITE     = colors.white

# Strength colors
STRONG   = colors.HexColor("#dcfce7")  # green tint
MODERATE = colors.HexColor("#fef9c3")  # yellow tint
WEAK     = colors.HexColor("#fee2e2")  # red tint
STRONG_T = colors.HexColor("#15803d")
MODERATE_T = colors.HexColor("#92400e")
WEAK_T   = colors.HexColor("#991b1b")

# ── Styles ────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def make_style(name, **kwargs):
    return ParagraphStyle(name, **kwargs)

S = {
    "cover_title": make_style("cover_title",
        fontName="Helvetica-Bold", fontSize=28, textColor=WHITE,
        leading=34, alignment=TA_CENTER),
    "cover_sub": make_style("cover_sub",
        fontName="Helvetica", fontSize=13, textColor=colors.HexColor("#c7d2fe"),
        leading=18, alignment=TA_CENTER),
    "cover_meta": make_style("cover_meta",
        fontName="Helvetica", fontSize=10, textColor=colors.HexColor("#94a3b8"),
        leading=14, alignment=TA_CENTER),
    "h1": make_style("h1",
        fontName="Helvetica-Bold", fontSize=16, textColor=NAVY,
        spaceBefore=18, spaceAfter=6, leading=20),
    "h2": make_style("h2",
        fontName="Helvetica-Bold", fontSize=13, textColor=BLUE,
        spaceBefore=14, spaceAfter=4, leading=16),
    "h3": make_style("h3",
        fontName="Helvetica-Bold", fontSize=11, textColor=MID_GRAY,
        spaceBefore=10, spaceAfter=3, leading=14),
    "body": make_style("body",
        fontName="Helvetica", fontSize=9.5, textColor=colors.HexColor("#1e293b"),
        leading=14, spaceBefore=3, spaceAfter=3),
    "body_small": make_style("body_small",
        fontName="Helvetica", fontSize=8.5, textColor=colors.HexColor("#334155"),
        leading=12, spaceBefore=2, spaceAfter=2),
    "bullet": make_style("bullet",
        fontName="Helvetica", fontSize=9, textColor=colors.HexColor("#1e293b"),
        leading=13, leftIndent=14, firstLineIndent=-10, spaceBefore=1),
    "label": make_style("label",
        fontName="Helvetica-Bold", fontSize=8, textColor=WHITE,
        leading=10, alignment=TA_CENTER),
    "table_hdr": make_style("table_hdr",
        fontName="Helvetica-Bold", fontSize=8.5, textColor=WHITE,
        leading=11, alignment=TA_CENTER),
    "table_cell": make_style("table_cell",
        fontName="Helvetica", fontSize=8.5, textColor=colors.HexColor("#1e293b"),
        leading=11),
    "table_cell_c": make_style("table_cell_c",
        fontName="Helvetica", fontSize=8.5, textColor=colors.HexColor("#1e293b"),
        leading=11, alignment=TA_CENTER),
    "caption": make_style("caption",
        fontName="Helvetica-Oblique", fontSize=8, textColor=MID_GRAY,
        leading=11, alignment=TA_CENTER, spaceBefore=2),
    "strong_label": make_style("strong_label",
        fontName="Helvetica-Bold", fontSize=8, textColor=STRONG_T,
        leading=10, alignment=TA_CENTER),
    "mod_label": make_style("mod_label",
        fontName="Helvetica-Bold", fontSize=8, textColor=MODERATE_T,
        leading=10, alignment=TA_CENTER),
    "weak_label": make_style("weak_label",
        fontName="Helvetica-Bold", fontSize=8, textColor=WEAK_T,
        leading=10, alignment=TA_CENTER),
}

# ── Helper Flowables ──────────────────────────────────────────────────────────
class ColorBar(Flowable):
    """A solid colored rectangle used as a section header bar."""
    def __init__(self, w, h, fill, radius=4):
        super().__init__()
        self.w, self.h, self.fill, self.radius = w, h, fill, radius
    def wrap(self, *args):
        return (self.w, self.h)
    def draw(self):
        self.canv.setFillColor(self.fill)
        self.canv.roundRect(0, 0, self.w, self.h, self.radius, fill=1, stroke=0)

def rule(color=RULE_GRAY, width=0.5):
    return HRFlowable(width="100%", thickness=width, color=color,
                      spaceAfter=4, spaceBefore=4)

def sp(pts=6):
    return Spacer(1, pts)

def p(text, style="body"):
    return Paragraph(text, S[style])

def bullets(items, style="bullet"):
    return [Paragraph(f"• {item}", S[style]) for item in items]

def badge(text, bg, fg_style):
    """Small colored badge for strength indicator."""
    data = [[Paragraph(text, S[fg_style])]]
    t = Table(data, colWidths=[1.1*inch], rowHeights=[0.22*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), bg),
        ("ROUNDEDCORNERS", [4]),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
    ]))
    return t

def section_header(title, subtitle=None, color=NAVY):
    """Returns a shaded section title block."""
    items = [sp(4), p(f"<b>{title}</b>", "h1"), rule(color, 1.5)]
    if subtitle:
        items.insert(2, p(subtitle, "body_small"))
    return items

def hex_str(c):
    """Get 6-char hex string from a ReportLab color, no prefix."""
    h = c.hexval()
    return h[2:] if h.startswith('0x') else h.lstrip('#')

def course_header(number, name, color=BLUE):
    """Returns a styled course title."""
    return [
        sp(8),
        p(f"<font color='#{hex_str(color)}' size='10'><b>COURSE {number}</b></font>  "
          f"<font size='14'><b>{name}</b></font>", "h1"),
        rule(color, 1),
    ]

def two_col_table(rows, col1_w=1.6*inch, col2_w=4.7*inch):
    """Simple two-column key-value table."""
    data = []
    for k, v in rows:
        data.append([
            Paragraph(f"<b>{k}</b>", S["body_small"]),
            Paragraph(v, S["body_small"])
        ])
    t = Table(data, colWidths=[col1_w, col2_w])
    t.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.white, LIGHT_BG]),
        ("LINEBELOW", (0,0), (-1,-1), 0.3, RULE_GRAY),
    ]))
    return t

def strength_row(strength, lbcc_course, notes):
    """Compact strength indicator row."""
    if strength == "STRONG":
        bg, fg = STRONG, "strong_label"
        text = "STRONG MATCH"
    elif strength == "MODERATE":
        bg, fg = MODERATE, "mod_label"
        text = "MODERATE MATCH"
    else:
        bg, fg = WEAK, "weak_label"
        text = "WEAK MATCH"

    data = [[
        Paragraph(text, S[fg]),
        Paragraph(f"<b>Recommended:</b> {lbcc_course}", S["body_small"]),
        Paragraph(notes, S["body_small"])
    ]]
    t = Table(data, colWidths=[1.1*inch, 2.3*inch, 2.9*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,0), bg),
        ("BACKGROUND", (1,0), (-1,0), LIGHT_BG),
        ("ALIGN", (0,0), (0,0), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("BOX", (0,0), (-1,-1), 0.5, RULE_GRAY),
        ("LINEAFTER", (0,0), (0,0), 0.5, RULE_GRAY),
        ("LINEAFTER", (1,0), (1,0), 0.5, RULE_GRAY),
    ]))
    return t

# ── Cover Page ────────────────────────────────────────────────────────────────
def build_cover():
    story = []
    # Dark navy background simulation via table
    cover_data = [[
        Paragraph("509j CTE ALIGNMENT PROJECT", S["cover_meta"]),
        Paragraph(" ", S["cover_meta"]),
        Paragraph("Adam Kirsch — CVHS Engineering & Applied Technology", S["cover_title"]),
        Paragraph(" ", S["cover_meta"]),
        Paragraph("College Now Eligibility Analysis", S["cover_sub"]),
        Paragraph(" ", S["cover_meta"]),
        Paragraph("Six Courses • LBCC Articulation Pathways • Action Recommendations", S["cover_sub"]),
        Paragraph(" ", S["cover_meta"]),
        Paragraph("509j CTE Alignment Project  |  Corvallis School District  |  March 2026", S["cover_meta"]),
    ]]
    # Use a table as a colored block
    cover_tbl = Table([[item] for item in [
        Paragraph("509j CTE ALIGNMENT PROJECT", S["cover_meta"]),
        sp(24),
        Paragraph("Adam Kirsch", S["cover_title"]),
        Paragraph("CVHS Engineering &amp; Applied Technology", S["cover_sub"]),
        sp(12),
        Paragraph("College Now Eligibility Analysis", S["cover_sub"]),
        sp(8),
        Paragraph("Six Courses  •  LBCC Articulation Pathways  •  Action Recommendations", S["cover_sub"]),
        sp(24),
        rule(colors.HexColor("#4f6baf"), 0.75),
        sp(8),
        Paragraph("509j CTE Alignment Project  |  Corvallis School District  |  March 2026", S["cover_meta"]),
    ]], colWidths=[6.5*inch])
    cover_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), NAVY),
        ("TOPPADDING", (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ("LEFTPADDING", (0,0), (-1,-1), 40),
        ("RIGHTPADDING", (0,0), (-1,-1), 40),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(sp(80))
    story.append(cover_tbl)
    story.append(sp(30))

    # Disclaimer box
    disc = Table([[Paragraph(
        "<b>About this document:</b> This analysis was prepared as part of the 509j CTE Alignment "
        "process. Course content sourced directly from Mr. Kirsch's 2025-2026 class websites. "
        "LBCC program data from linnbenton.edu current catalog. College Now eligibility requires "
        "formal review by LBCC faculty and satisfies ODE CTE articulation requirements.",
        S["body_small"]
    )]], colWidths=[6.5*inch])
    disc.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), LIGHT_BG),
        ("BOX", (0,0), (-1,-1), 0.75, BLUE),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING", (0,0), (-1,-1), 14),
        ("RIGHTPADDING", (0,0), (-1,-1), 14),
    ]))
    story.append(disc)
    story.append(PageBreak())
    return story

# ── Executive Summary ─────────────────────────────────────────────────────────
def build_exec_summary():
    story = []
    story += section_header("Executive Summary",
        "What we found, what it means, what to do next.")

    story.append(p(
        "Adam Kirsch teaches six distinct CTE-designated courses at Crescent Valley High School "
        "spanning applied engineering, woodworking, carpentry, and entrepreneurship. None currently "
        "carry College Now (dual credit) articulation with LBCC, despite significant content overlap "
        "with LBCC's Engineering Technology and CADD programs. This document evaluates each course "
        "against LBCC's current catalog and ranks articulation opportunity by strength of content match."
    ))
    story.append(sp(6))

    # Summary matrix
    hdr_style = TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("TEXTCOLOR", (0,0), (-1,0), WHITE),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 8.5),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("FONTNAME", (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,1), (-1,-1), 8.5),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ("LINEBELOW", (0,0), (-1,-1), 0.3, RULE_GRAY),
        ("BOX", (0,0), (-1,-1), 0.5, RULE_GRAY),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        # Color code strength column
        ("BACKGROUND", (3,1), (3,1), STRONG),   # IDEA
        ("BACKGROUND", (3,2), (3,2), MODERATE), # DREAM
        ("BACKGROUND", (3,3), (3,3), WEAK),     # Carpentry
        ("BACKGROUND", (3,4), (3,4), WEAK),     # Woods 1
        ("BACKGROUND", (3,5), (3,5), MODERATE), # Woods 2
        ("BACKGROUND", (3,6), (3,6), WEAK),     # Woods 3&4
    ])

    matrix_data = [
        [Paragraph("Course", S["table_hdr"]),
         Paragraph("Oregon Skill Set / Standards", S["table_hdr"]),
         Paragraph("Best LBCC Match", S["table_hdr"]),
         Paragraph("Match Strength", S["table_hdr"]),
         Paragraph("Priority", S["table_hdr"])],

        [Paragraph("IDEA", S["table_cell_c"]),
         Paragraph("NGSS HS-ETS; Oregon CTE Engineering & Applied Technology; CCSS Math", S["table_cell"]),
         Paragraph("ENGR 248 — Engineering Graphics: Mechanical\n(parametric CAD, orthographic, engineering graphics)", S["table_cell"]),
         Paragraph("STRONG", S["strong_label"]),
         Paragraph("#1 — Pursue First", S["table_cell_c"])],

        [Paragraph("DREAM", S["table_cell_c"]),
         Paragraph("NGSS HS-ETS; Oregon CTE Engineering & Applied Technology; CCSS Math", S["table_cell"]),
         Paragraph("ENGR 102 — Design Thinking & Problem Solving\n+ BA 260 Entrepreneurship (partial)", S["table_cell"]),
         Paragraph("MODERATE", S["mod_label"]),
         Paragraph("#2 — Pursue with ENGR dept", S["table_cell_c"])],

        [Paragraph("Carpentry 1–3", S["table_cell_c"]),
         Paragraph("Oregon Skill Set: Construction Cluster,\nCarpentry Focus (COPE10)", S["table_cell"]),
         Paragraph("No direct LBCC match.\nCTE Construction apprenticeship pathway possible.", S["table_cell"]),
         Paragraph("WEAK", S["weak_label"]),
         Paragraph("#5 — Apprenticeship route", S["table_cell_c"])],

        [Paragraph("Woodworking 1", S["table_cell_c"]),
         Paragraph("Oregon Skill Set: Manufacturing Cluster;\nOregon CTE Engineering & Applied Technology", S["table_cell"]),
         Paragraph("No dedicated LBCC woodworking program.\nMA3.396 Manufacturing Processes I (partial).", S["table_cell"]),
         Paragraph("WEAK", S["weak_label"]),
         Paragraph("#6 — Explore OSU Wood Sci.", S["table_cell_c"])],

        [Paragraph("Woodworking 2", S["table_cell_c"]),
         Paragraph("OR Skill Set: Manufacturing (MNPI10) +\nCarpentry (COPE10); NGSS HS-ETS", S["table_cell"]),
         Paragraph("EG4.412 — Inventor 3D Design (CAD component)\nMA3.420 CNC Operations (CNC component)", S["table_cell"]),
         Paragraph("MODERATE", S["mod_label"]),
         Paragraph("#3 — CAD component only", S["table_cell_c"])],

        [Paragraph("Woodworking 3 & 4", S["table_cell_c"]),
         Paragraph("Oregon Skill Set: Manufacturing Cluster;\nAdvanced CTE capstone", S["table_cell"]),
         Paragraph("MA3.412 — Mastercam CAD/CAM\nMA3.420 — CNC Vertical Machining Ops", S["table_cell"]),
         Paragraph("WEAK", S["weak_label"]),
         Paragraph("#4 — CNC component only", S["table_cell_c"])],
    ]
    matrix_tbl = Table(matrix_data,
        colWidths=[0.9*inch, 1.75*inch, 1.85*inch, 0.9*inch, 1.1*inch])
    matrix_tbl.setStyle(hdr_style)
    story.append(matrix_tbl)
    story.append(sp(4))
    story.append(p(
        "<i>LBCC does not currently offer a dedicated woodworking or carpentry certificate program. "
        "The strongest articulation opportunity is IDEA → ENGR 248. OSU's Wood Science and Engineering "
        "program is a longer-term pathway worth exploring for the woodworking sequence.</i>",
        "caption"
    ))
    story.append(sp(10))

    # Key findings
    story.append(p("<b>Key Findings</b>", "h2"))
    story += bullets([
        "<b>IDEA is the highest-priority course</b> for College Now pursuit — it already uses "
        "SolidWorks (ENGR 248 uses parametric CAD — platform-agnostic per catalog), covers NGSS engineering design standards, "
        "earns students 1.5 HS credits, and has documented standards alignment.",
        "<b>DREAM is the strongest entrepreneurship match</b> but splits between engineering and "
        "business content. A split articulation (ENGR 102 + BA 260) may be most accurate.",
        "<b>The woodworking sequence has no direct LBCC path</b> — LBCC's programs focus on "
        "metal machining (Machine Tool Technology), not fine woodworking or furniture. The CNC "
        "and CAD sub-components of each course do have partial matches.",
        "<b>Carpentry aligns with Oregon's Construction Cluster skill set</b> (COPE10) but LBCC "
        "does not offer a stand-alone carpentry certificate — only apprenticeship-adjacent programs.",
        "<b>Kirsch carries 6 distinct courses</b> with no current College Now articulations. "
        "Adding even one (IDEA) would be a measurable win for the CTE alignment goals.",
    ])
    story.append(PageBreak())
    return story

# ── Course Profiles ───────────────────────────────────────────────────────────
def course_block(num, name, color, description, credits, level, prereqs,
                  skills, software, standards, projects,
                  lbcc_course, lbcc_number, match, match_why, action_items):
    story = []
    story += course_header(num, name, color)

    # Quick facts row
    qf_data = [[
        Paragraph("<b>Credits</b>", S["body_small"]),
        Paragraph("<b>Level</b>", S["body_small"]),
        Paragraph("<b>Prerequisites</b>", S["body_small"]),
    ],[
        Paragraph(credits, S["body"]),
        Paragraph(level, S["body"]),
        Paragraph(prereqs, S["body"]),
    ]]
    qf_tbl = Table(qf_data, colWidths=[1.5*inch, 1.5*inch, 3.8*inch])
    qf_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("TEXTCOLOR", (0,0), (-1,0), WHITE),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 8.5),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("BOX", (0,0), (-1,-1), 0.5, RULE_GRAY),
        ("LINEBEFORE", (1,0), (1,-1), 0.3, RULE_GRAY),
        ("LINEBEFORE", (2,0), (2,-1), 0.3, RULE_GRAY),
    ]))
    story.append(qf_tbl)
    story.append(sp(6))

    story.append(p(description, "body"))
    story.append(sp(6))

    # Two-column detail table
    detail_rows = [
        ("Key Skills", skills),
        ("Software / Tools", software),
        ("Standards", standards),
        ("Major Projects", projects),
    ]
    story.append(two_col_table(detail_rows))
    story.append(sp(8))

    # LBCC match box
    match_color = STRONG if match == "STRONG" else (MODERATE if match == "MODERATE" else WEAK)
    match_label = f"<b>{'STRONG' if match=='STRONG' else 'MODERATE' if match=='MODERATE' else 'WEAK'} MATCH</b>"
    label_color = STRONG_T if match == "STRONG" else (MODERATE_T if match == "MODERATE" else WEAK_T)

    lbcc_content = [
        [Paragraph(f"<font color='#{hex_str(label_color)}'>{match_label}</font>  "
                   f"<font size='10'><b>{lbcc_course}</b></font>  "
                   f"<font color='#{hex_str(MID_GRAY)}' size='8'>{lbcc_number}</font>",
                   S["body"])],
        [Paragraph(match_why, S["body_small"])],
        [Paragraph("<b>To pursue articulation:</b>", S["body_small"])],
    ]
    for item in action_items:
        lbcc_content.append([Paragraph(f"  {chr(9655)}  {item}", S["body_small"])])

    lbcc_tbl = Table(lbcc_content, colWidths=[6.5*inch])
    lbcc_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), LIGHT_BG),
        ("BACKGROUND", (0,0), (0,0), match_color),
        ("BOX", (0,0), (-1,-1), 0.75, color),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("LINEBELOW", (0,0), (0,0), 0.5, color),
    ]))
    story.append(lbcc_tbl)
    story.append(sp(4))
    return story

# ── Individual Course Pages ───────────────────────────────────────────────────
def build_courses():
    story = []
    story += section_header("Course-by-Course Analysis",
        "Each course evaluated against LBCC's current catalog for College Now eligibility.")

    # ── IDEA ──────────────────────────────────────────────────────────────────
    story += course_block(
        num="1", name="IDEA — Introduction to Design using Engineering and Art",
        color=BLUE,
        description=(
            "IDEA is a foundational engineering course earning students 1.5 high school credits "
            "(1.0 Science + 0.5 Applied Technology) — unusual for a single HS class and a strong "
            "signal of college-level rigor. Students work with industry-standard CAD software "
            "(SolidWorks), fabrication equipment (3D printers, laser engravers, CNC routers, "
            "UV printer, waterjet cutters, vinyl cutters), and cover physics, chemistry, statistics, "
            "and trigonometry in an engineering design context. Students routinely pass the CSWA (Certified SolidWorks Associate) exam."
        ),
        credits="1.5 HS credits (1.0 Science + 0.5 Applied Tech)",
        level="9th–10th grade entry point to engineering sequence",
        prereqs="None listed — open enrollment gateway course",
        skills="Engineering design process, problem-solving, teamwork, technical communication, "
               "orthographic drawing, dimensioning, CAD, physics concepts (energy, waves, circuits), "
               "basic chemistry (stoichiometry), statistics, trigonometry, geometry",
        software="SolidWorks 2019 (students pass CSWA exam), Adobe Illustrator, Mastercam, Z-Suite, "
                 "Logger Pro (motion analysis), Inkscape",
        standards="NGSS: HS-ETS1-1 through 4, HS-PS1, HS-PS2, HS-PS3, HS-PS4, HS-ESS3-4; "
                  "CCSS Math: HSN.Q, HSA.SSE, HSA.CED, HSF.LE, HSS.ID, HSS.IC; "
                  "Oregon CTE Engineering & Applied Technology pathway standards (all); "
                  "CCSS Literacy in Science & Technical Subjects 9/10 (all)",
        projects="Turbine design and analysis report; prototype fabrication using 3D printer, "
                 "laser engraver, CNC router; physics motion analysis; multiple design challenges",
        lbcc_course="ENGR 248 — Engineering Graphics: Mechanical",
        lbcc_number="(3 credits, LBCC Engineering program)",
        match="STRONG",
        match_why=(
            "IDEA uses SolidWorks as its primary CAD tool; ENGR 248 specifies 'solid modelling/CAD "
            "software' — no brand requirement. SolidWorks and Inventor (LBCC's platform) are both "
            "parametric solid modelers; skills transfer directly. Both courses cover orthographic "
            "projection, dimensioning, and engineering graphics applied to real design problems. IDEA's "
            "documented NGSS HS-ETS standards directly parallel ENGR 248's engineering design content. "
            "The 1.5-credit HS structure demonstrates rigor above a typical elective. Kirsch holds a "
            "PE license (the national bar for engineering competency), fully satisfying LBCC instructor "
            "qualification requirements. Secondary option: ENGR 102 — Design Thinking & Problem "
            "Solving if ENGR 248 is too narrow."
        ),
        action_items=[
            "Contact LBCC High School Partnerships (highschool@linnbenton.edu) to request ENGR 248 "
            "faculty review of IDEA syllabus",
            "Prepare syllabus document mapping IDEA content to ENGR 248 course outcomes",
            "Confirm Kirsch's credentials package: PE license (Oregon), engineering degree and "
            "industry experience — Kirsch meets LBCC instructor qualification requirements",
            "Submit formal College Now application through ODE's CTE articulation process",
            "Consider requesting dual articulation: ENGR 248 (CAD/design) + ENGR 111 (orientation)",
        ]
    )

    # ── DREAM ─────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story += course_block(
        num="2", name="DREAM — Designing, Researching & Engineering Articles for Market",
        color=TEAL,
        description=(
            "DREAM is the capstone of Kirsch's engineering sequence — students who have completed "
            "IDEA and other engineering courses apply all skills to design, prototype, and market "
            "real products using the full suite of school fabrication equipment. The course integrates "
            "engineering design, project management, community partnerships, and entrepreneurship. "
            "Products created in class are sold to support further course projects. Students also "
            "serve as mentors for younger students during 8th-grade engineering events."
        ),
        credits="1.0 HS credit (Applied Technology / CTE)",
        level="11th–12th grade capstone; requires IDEA or equivalent",
        prereqs="IDEA (or equivalent engineering coursework)",
        skills="Product design and optimization, engineering stress analysis, project management, "
               "marketing and product development, technical drawings and dimensioning, "
               "teamwork and leadership, employability skills, soldering and basic electronics, "
               "community engagement, mentorship of younger students",
        software="SolidWorks 2019, Adobe Illustrator, Mastercam, Sheetcam, Inkscape; "
                 "Full equipment: 3D printers, laser engraver, vinyl cutter, CNC routers, "
                 "UV printer, Shaper Origin",
        standards="NGSS: HS-ETS1-1 through 4, HS-PS1, HS-PS2, HS-PS3, HS-PS4, HS-ESS3-4; "
                  "CCSS Math: full HSN, HSA, HSF, HSS series; "
                  "Oregon CTE Engineering & Applied Technology pathway standards (all); "
                  "CCSS Literacy in Science & Technical Subjects 9/10 (all, including WHST.3)",
        projects="Community-based engineering challenges; product prototyping and sale; "
                 "scavenger hunt activity design for 8th-grade visitors; project timelines "
                 "and management documentation; internships with community business partners",
        lbcc_course="ENGR 102 — Design Thinking & Problem Solving + BA 260 — Entrepreneurship",
        lbcc_number="(LBCC Engineering + Business programs — split articulation)",
        match="MODERATE",
        match_why=(
            "DREAM's engineering component (design process, CAD, fabrication) aligns with ENGR 102, "
            "while its product-to-market and project management content aligns with BA 260 "
            "(Entrepreneurship & Small Business). A single LBCC course that covers both the technical "
            "and entrepreneurial content does not currently exist, making a split articulation the "
            "most honest representation. ENGR 102 alone would undervalue the course; BA 260 alone "
            "would misrepresent it as business-only. Best strategy: pursue ENGR 102 first (as it "
            "builds on the IDEA → ENGR 248 relationship), then explore BA 260 as an additional "
            "articulation in a future cycle."
        ),
        action_items=[
            "Build on the IDEA → ENGR 248 relationship first; establish Kirsch as a College Now "
            "instructor before adding DREAM",
            "Request LBCC Engineering faculty review of DREAM for ENGR 102 equivalency",
            "Contact LBCC Business department about BA 260 review for the entrepreneurship component",
            "Document the product-to-market project cycle with photos and sales records — "
            "this is compelling evidence of college-level entrepreneurship rigor",
            "Consider pursuing ENGR 102 in year 2 after IDEA is established",
        ]
    )

    # ── WOODWORKING 2 ─────────────────────────────────────────────────────────
    story.append(PageBreak())
    story += course_block(
        num="3", name="Woodworking 2",
        color=AMBER,
        description=(
            "Woodworking 2 is an intermediate hands-on course explicitly aligned to Oregon's CTE "
            "Skill Sets in both the Manufacturing Cluster (Wood Products) and Construction Cluster "
            "(Carpentry). Students work with raw lumber, advanced joinery, CAD-designed projects, "
            "CNC machining (V-Carve Pro), and wood finishing. The course emphasizes project "
            "planning, material estimation, technical drawing, and professional presentation "
            "at the Mid Willamette Valley Woodworkers Guild show."
        ),
        credits="1.0 HS credit (CTE — Manufacturing/Construction)",
        level="Intermediate; requires Woodworking 1 or equivalent",
        prereqs="Woodworking 1 or demonstrated shop skills",
        skills="Wood identification and properties, material cost estimation, advanced joinery "
               "(mortise/tenon, dovetails, inlay), multi-view technical drawing, wood finishing, "
               "project planning (POP template), safe tool/machine operation, wood science basics",
        software="SolidWorks 2019, V-Carve Pro (CNC), Inkscape, Adobe Illustrator",
        standards="Oregon Skill Set: Manufacturing Cluster, Wood Products (MNPI10.01–10.03); "
                  "Oregon Skill Set: Construction Cluster, Carpentry (COPE10.01–10.02); "
                  "NGSS: HS-PS2-6, HS-ETS1-2, HS-ETS1-3; "
                  "Oregon CTE Engineering & Applied Technology pathway standards 1.0–6.0",
        projects="Complex inlay project (CNC + V-Carve); two personal projects (100+ pts each); "
                 "submission to Mid Willamette Valley Woodworkers Guild show (public library, April)",
        lbcc_course="EG4.412 — Inventor 3D Design  (CAD component only)",
        lbcc_number="(LBCC CADD program) + MA3.420 — CNC Operations (CNC component)",
        match="MODERATE",
        match_why=(
            "LBCC has no dedicated woodworking or wood technology program, which is the core challenge. "
            "However, two sub-components of Woodworking 2 have meaningful LBCC equivalents: "
            "(1) The CAD/technical drawing work aligns with EG4.412 (Inventor 3D Design) or ENGR 248 "
            "— both use parametric solid modeling and dimensioning standards. (2) The V-Carve/CNC "
            "machining work aligns with MA3.420 (CNC Vertical Machining Operations). A full-course "
            "articulation is not viable — the woodworking-specific content has no LBCC equivalent. "
            "A partial or component articulation is the realistic near-term goal."
        ),
        action_items=[
            "Identify which portion of Woodworking 2 hours are spent on CAD (SolidWorks/V-Carve) "
            "vs. hand/power tool work — this determines if a CAD-only articulation is defensible",
            "Explore whether OSU's Wood Science and Engineering (BS program) has community college "
            "pathways or articulation agreements that CVHS could connect to",
            "Contact Oregon Dept. of Education CTE office about the Wood Products skill set — "
            "they may know of other CC partners with woodworking programs",
            "In the near term, document Oregon Skill Set alignment (MNPI10/COPE10) formally — "
            "this is required for any future articulation and good CTE practice regardless",
        ]
    )

    # ── WOODWORKING 3 & 4 ─────────────────────────────────────────────────────
    story.append(PageBreak())
    story += course_block(
        num="4", name="Woodworking 3 & 4",
        color=AMBER,
        description=(
            "Woodworking 3 & 4 is the advanced/capstone level of the woodworking sequence. "
            "Students complete three 300-point projects demonstrating mastery of joinery, "
            "design, and professional-quality finishing. Students also complete the Forest "
            "Service Trail Signs project (real commissioned work for the National Forest) "
            "using V-Carve CNC routing, and submit work to the Mid Willamette Valley "
            "Woodworkers Guild public show. Safety certification is required before any "
            "equipment use."
        ),
        credits="1.0 HS credit (CTE — Advanced Manufacturing/Construction)",
        level="Advanced capstone; requires Woodworking 1 & 2",
        prereqs="Woodworking 1 and 2; safety certification",
        skills="Advanced joinery and hand tool mastery, professional finishing, CNC routing "
               "and toolpath generation (V-Carve Pro), G-code file preparation, project "
               "management (POP/timeline documentation), safety certification across all "
               "major equipment, professional presentation for guild show",
        software="V-Carve Pro, SolidWorks, Inkscape; Full shop: band saw, table saw, "
                 "router, drill press, CNC router, lathe",
        standards="Oregon Skill Set: Manufacturing Cluster (advanced); "
                  "CVHS Dimensioning Standards; POP/portfolio documentation standards; "
                  "Real-world commission work (Forest Service Trail Signs)",
        projects="Forest Service Trail Signs (commissioned real-world project); "
                 "three 300-point personal projects; Mid Willamette Valley Woodworkers "
                 "Guild show submission (2 pieces, public library, April 23-26)",
        lbcc_course="MA3.412 — Mastercam CAD/CAM Programming  (CNC component)",
        lbcc_number="(LBCC Machine Tool Technology program)",
        match="WEAK",
        match_why=(
            "The same LBCC gap applies here as with Woodworking 2: no woodworking program exists. "
            "The CNC routing work in this course uses V-Carve (wood-specific), not Mastercam "
            "(metal-focused) — so even the CNC match is imperfect. MA3.412/MA3.420 target metal "
            "CNC machining, not wood CNC routing. This course's strongest value proposition is "
            "the real-world commissioned work (Forest Service Trail Signs) and guild show "
            "participation — hallmarks of a high-quality CTE capstone — but without a LBCC "
            "woodworking program, formal articulation is not currently viable."
        ),
        action_items=[
            "Document the Forest Service Trail Signs as an industry partnership — this is "
            "significant evidence for any future articulation or grant application",
            "Long-term: explore Chemeketa Community College (Salem) or Lane Community College "
            "(Eugene) — both may have cabinet/woodworking programs that could articulate",
            "Consider Oregon apprenticeship pathway: Oregon Building Industry Association / "
            "Carpenters Union apprenticeship programs accept HS credit through ODE",
            "For now: ensure Oregon Skill Set documentation is current and complete — "
            "required for CTE designation regardless of College Now status",
        ]
    )

    # ── CARPENTRY 1-3 ─────────────────────────────────────────────────────────
    story.append(PageBreak())
    story += course_block(
        num="5", name="Carpentry 1–3",
        color=GREEN,
        description=(
            "The Carpentry sequence centers on real construction work — students build actual "
            "micro-shelters and tiny homes donated to the community (Unity Shelter). Carpentry 1 "
            "focuses on structural work: roofing (drip edge, underlayment, shingles), Hardi panel "
            "soffits, window and door installation. Carpentry 2 & 3 add CNC design work with "
            "V-Carve Pro and phone holder fabrication. Students maintain documentation portfolios "
            "via Google Slides and mentor younger students in pre-engineering activities. "
            "The program also connects to OSU's Wood Science and Forestry programs."
        ),
        credits="1.0 HS credit per level (CTE — Construction)",
        level="Levels 1, 2, and 3 — multi-year sequence",
        prereqs="None for Carpentry 1; subsequent levels build on prior",
        skills="Structural carpentry (roofing, siding, windows, doors, framing), tool safety "
               "and maintenance, shop cleanliness and workplace readiness, CNC/V-Carve design, "
               "technical drawing (SolidWorks), photography documentation, project portfolio, "
               "mentorship and teaching younger students",
        software="V-Carve Pro, SolidWorks 2019, Inkscape, Adobe Illustrator; "
                 "Physical: framing tools, roofing equipment, power saws, drill",
        standards="Oregon Skill Set: Construction Cluster, Carpentry Focus (COPE10.01–10.02); "
                  "Pre-Engineering Program Syllabus standards; "
                  "Real construction documentation requirements",
        projects="Micro-shelter/tiny home construction (Shelter #9 completion, Shelter #10 build); "
                 "Roofing installation; CNC phone holder design (Carpentry 2&3); "
                 "Pre-engineering mentorship for 8th-grade Open House",
        lbcc_course="No direct match — LBCC lacks a carpentry certificate program",
        lbcc_number="(Oregon Building Trades Apprenticeship pathway — alternative route)",
        match="WEAK",
        match_why=(
            "LBCC does not offer a carpentry or residential construction certificate. Their "
            "construction-adjacent offerings are within the Engineering program (Construction "
            "Engineering emphasis — ENGR 245 Engineering Graphics: Civil) and apprenticeship "
            "support programs. The Carpentry course's real construction work (tiny homes for "
            "Unity Shelter) is exceptional CTE practice and community partnership — but without "
            "a LBCC carpentry equivalent, College Now articulation is not currently possible. "
            "The most viable alternative is Oregon's registered apprenticeship pathway, where "
            "documented HS construction hours can count toward Carpenters Union apprenticeship."
        ),
        action_items=[
            "Contact Oregon BOLI (Bureau of Labor & Industries) Apprenticeship Division about "
            "pre-apprenticeship credit for documented carpentry hours",
            "Reach out to the Mid-Willamette Valley Carpenters Local Union about partnership",
            "Explore ENGR 245 (Engineering Graphics: Civil) articulation for any structural "
            "drawing/design component if Carpentry courses include civil drawing work",
            "Document Unity Shelter partnership formally — this is a powerful community "
            "partnership that strengthens any grant or program review",
            "Check whether Chemeketa CC's Construction program offers College Now agreements "
            "with other districts — if so, pursue a similar agreement for 509j",
        ]
    )

    # ── WOODWORKING 1 ─────────────────────────────────────────────────────────
    story.append(PageBreak())
    story += course_block(
        num="6", name="Woodworking 1",
        color=AMBER,
        description=(
            "Woodworking 1 is the entry-level course in Kirsch's woodworking sequence. Students "
            "learn foundational woodworking — hand tools, power tools, wood selection, and basic "
            "project construction — alongside introductory CNC skills using V-Carve Pro. The "
            "Forest Service Trail Signs project begins here, with students creating two signs "
            "using V-Carve software for CNC engraving and submitting work to the Mid Willamette "
            "Valley Woodworkers Guild show. Community connections include Oregon State University "
            "Wood Science and Engineering and local sawyer/supplier partnerships."
        ),
        credits="1.0 HS credit (CTE — Manufacturing/Construction)",
        level="Entry-level; no prerequisites",
        prereqs="None — open enrollment",
        skills="Hand tool operation and safety, power tool operation, wood selection and properties, "
               "project planning (POP template), V-Carve Pro for CNC design (toolpaths, G-code), "
               "basic Solidworks CAD, portfolio documentation",
        software="V-Carve Pro, SolidWorks 2019, Inkscape, Adobe Illustrator",
        standards="Oregon Skill Set: Manufacturing Cluster; Oregon CTE Engineering & Applied Technology (partial); "
                  "CVHS safety and dimensioning standards",
        projects="Forest Service Trail Signs (V-Carve CNC engraving, due for guild show); "
                 "foundational woodworking projects (100-point level); "
                 "Mid Willamette Valley Woodworkers Guild show submission",
        lbcc_course="No direct match — MA3.396 Manufacturing Processes I is closest (partial)",
        lbcc_number="(LBCC Machine Tool Technology — wood-specific content not covered)",
        match="WEAK",
        match_why=(
            "Woodworking 1 is foundational and introductory — even if LBCC had a woodworking "
            "program, a 100-level entry course typically does not qualify for college-level "
            "dual credit. The CNC and CAD elements are taught at a basic level in this course "
            "(covered more deeply in Woodworking 2 and 3&4). MA3.396 (Manufacturing Processes I) "
            "covers metalworking processes, not wood. This course is best understood as building "
            "toward the Woodworking 2/3&4 sequence rather than a standalone College Now target."
        ),
        action_items=[
            "Focus College Now energy on Woodworking 2 and 3&4 rather than Woodworking 1 — "
            "the content is more advanced and defensible",
            "Ensure Woodworking 1 is formally documented as a CTE course under Oregon Skill "
            "Sets so it counts toward pathway completion metrics",
            "Track student progression through the full sequence (1 → 2 → 3&4) — longitudinal "
            "data strengthens any future articulation case",
        ]
    )

    story.append(PageBreak())
    return story

# ── Action Plan ───────────────────────────────────────────────────────────────
def build_action_plan():
    story = []
    story += section_header("Action Plan & Next Steps",
        "Prioritized recommendations for pursuing College Now articulation.")

    story.append(p(
        "Based on content strength and LBCC program availability, here is a phased approach "
        "to building College Now articulations for Kirsch's courses over 2–3 years."
    ))
    story.append(sp(8))

    phases = [
        ("Year 1 — Immediate (2025-26)", BLUE, [
            "Submit IDEA → ENGR 248 articulation request to LBCC (highschool@linnbenton.edu). "
            "Prepare syllabus mapping to LBCC course outcomes.",
            "Compile Kirsch's credentials package: PE license (Oregon), engineering degree and "
            "industry experience, CSWA student outcomes — all included in Kirsch_Credentials.docx.",
            "Formally document Oregon Skill Set alignment for ALL six courses — required for "
            "CTE designation and a prerequisite for any articulation.",
            "Document the Unity Shelter tiny home partnership and Forest Service Trail Signs "
            "as industry/community partnerships (required for Perkins V reporting).",
        ]),
        ("Year 2 — Build (2026-27)", TEAL, [
            "After IDEA is established, pursue DREAM → ENGR 102 with LBCC Engineering faculty.",
            "Contact Oregon BOLI Apprenticeship Division about pre-apprenticeship credit for "
            "Carpentry hours (documented construction hours toward Carpenters Union apprenticeship).",
            "Research Chemeketa CC (Salem) and Lane CC (Eugene) for woodworking/cabinetry programs "
            "— if either has College Now agreements with other Oregon districts, 509j can follow.",
            "Explore OSU Wood Science articulation pathway for the Woodworking sequence capstone.",
        ]),
        ("Year 3 — Expand (2027-28)", GREEN, [
            "If LBCC adds a Construction or Wood Technology program, pursue Carpentry and "
            "Woodworking articulations formally.",
            "Pursue BA 260 (Entrepreneurship) articulation for the DREAM business component.",
            "Evaluate whether Woodworking 2's CAD/CNC content can articulate as a component "
            "credit alongside a full woodworking articulation from another CC.",
            "Review all articulations annually per ODE CTE program review requirements.",
        ]),
    ]

    for title, color, items in phases:
        phase_hdr = Table([[Paragraph(f"<b>{title}</b>", S["h2"])]],
            colWidths=[6.5*inch])
        phase_hdr.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), LIGHT_BG),
            ("LEFTPADDING", (0,0), (-1,-1), 12),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("LINELEFT", (0,0), (-1,-1), 4, color),
        ]))
        story.append(phase_hdr)
        story.append(sp(4))
        story += bullets(items)
        story.append(sp(8))

    # Contact info
    story.append(rule())
    story.append(p("<b>Key Contacts for Articulation Pursuit</b>", "h2"))
    contact_data = [
        [Paragraph("<b>Contact</b>", S["table_hdr"]),
         Paragraph("<b>Role</b>", S["table_hdr"]),
         Paragraph("<b>Relevance</b>", S["table_hdr"])],
        [Paragraph("highschool@linnbenton.edu", S["table_cell"]),
         Paragraph("LBCC High School Partnerships", S["table_cell"]),
         Paragraph("First contact for all College Now inquiries — IDEA, DREAM", S["table_cell"])],
        [Paragraph("LBCC Engineering Dept.", S["table_cell"]),
         Paragraph("ENGR 248 / ENGR 102 faculty", S["table_cell"]),
         Paragraph("Syllabus review and equivalency determination for IDEA/DREAM", S["table_cell"])],
        [Paragraph("LBCC CADD Program", S["table_cell"]),
         Paragraph("EG4.412 faculty", S["table_cell"]),
         Paragraph("CAD component review for Woodworking 2 (longer-term)", S["table_cell"])],
        [Paragraph("Oregon BOLI Apprenticeship\n(503) 378-3272", S["table_cell"]),
         Paragraph("Pre-Apprenticeship Programs", S["table_cell"]),
         Paragraph("Carpentry construction hours toward Carpenters Union apprenticeship", S["table_cell"])],
        [Paragraph("ODE CTE Office\node.oregon.gov/cte", S["table_cell"]),
         Paragraph("Oregon CTE Standards & Articulation", S["table_cell"]),
         Paragraph("Oregon Skill Set documentation, Perkins V compliance, articulation guidance", S["table_cell"])],
    ]
    contact_tbl = Table(contact_data, colWidths=[1.7*inch, 1.7*inch, 3.1*inch])
    contact_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("TEXTCOLOR", (0,0), (-1,0), WHITE),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ("LINEBELOW", (0,0), (-1,-1), 0.3, RULE_GRAY),
        ("BOX", (0,0), (-1,-1), 0.5, RULE_GRAY),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(contact_tbl)
    story.append(sp(16))

    # Footer note
    story.append(rule())
    story.append(p(
        "<i>This analysis was prepared as part of the 509j CTE Alignment Project, March 2026. "
        "Course content sourced from Mr. Kirsch's 2025-2026 class websites "
        "(sites.google.com/corvallis.k12.or.us/adam-kirsch-homepage). "
        "LBCC program data from linnbenton.edu current catalog and SmartCatalog. "
        "College Now eligibility requires formal LBCC faculty review per ODE requirements.</i>",
        "body_small"
    ))
    return story

# ── Page Template ─────────────────────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    w, h = letter
    # Header bar
    canvas.setFillColor(NAVY)
    canvas.rect(0, h - 0.45*inch, w, 0.45*inch, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(0.5*inch, h - 0.27*inch, "509j CTE Alignment — Adam Kirsch College Now Analysis")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(w - 0.5*inch, h - 0.27*inch, "Corvallis School District  |  March 2026")
    # Footer
    canvas.setFillColor(RULE_GRAY)
    canvas.rect(0, 0, w, 0.35*inch, fill=1, stroke=0)
    canvas.setFillColor(MID_GRAY)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(0.5*inch, 0.13*inch, "CVHS Pre-Engineering & Applied Technology")
    canvas.drawCentredString(w/2, 0.13*inch, f"Page {doc.page}")
    canvas.drawRightString(w - 0.5*inch, 0.13*inch, "Confidential — For internal alignment use")
    canvas.restoreState()

def on_first_page(canvas, doc):
    # No header/footer on cover
    pass

# ── Build Document ────────────────────────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=letter,
        leftMargin=0.65*inch,
        rightMargin=0.65*inch,
        topMargin=0.65*inch,
        bottomMargin=0.55*inch,
        title="Adam Kirsch — College Now Eligibility Analysis",
        author="509j CTE Alignment Project",
        subject="College Now articulation analysis for CVHS Pre-Engineering courses"
    )

    story = []
    story += build_cover()
    story += build_exec_summary()
    story += build_courses()
    story += build_action_plan()

    doc.build(story,
              onFirstPage=on_first_page,
              onLaterPages=on_page)
    print(f"PDF written to: {OUTPUT}")

if __name__ == "__main__":
    build()
