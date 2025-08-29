import textwrap

from PIL import Image
from fpdf import FPDF
from typing import List
import pandas as pd
import tempfile

from components.dashboard_blocks import render_block_for_pdf, DEFAULT_CHART_TYPES
from constant import DASHBOARD_TITLES
from metric_clusters import ALL_METRIC_CLUSTERS
from io import BytesIO


class VelocityPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.section_spacing = 8
        self.line_height = 6
        self.title_height = 12

    @property
    def usable_height(self):
        return self.h - self.t_margin - self.b_margin

    @property
    def remaining_height(self):
        return self.usable_height - (self.get_y() - self.t_margin)

    def check_space_and_add_page(self, required_height):
        if self.remaining_height < required_height:
            self.add_page()
            return True
        return False

    def header(self):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 10, "Velocity Map Diagnostic Report", ln=True, align="C")
        self.ln(5)

    def add_velocity_map(self, image_bytes: bytes):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            tmp_file.write(image_bytes)
            tmp_file_path = tmp_file.name

        img = Image.open(tmp_file_path)
        img_width, img_height = img.size
        aspect_ratio = img_height / img_width

        display_width = (self.w - 2 * self.l_margin) * 0.8
        display_height = display_width * aspect_ratio

        self.check_space_and_add_page(display_height + 10)

        x_offset = (self.w - display_width) / 2
        current_y = self.get_y()

        self.image(tmp_file_path, x=x_offset, y=current_y, w=display_width, h=display_height)
        self.set_y(current_y + display_height + self.section_spacing)

    def add_score_table(self, df: pd.DataFrame):
        table_height = (len(df) + 2) * 8 + 15
        self.check_space_and_add_page(table_height)

        self.set_font("Helvetica", "B", 10)
        self.cell(0, 10, "Metric Score Breakdown (Latest Month)", ln=True)

        self.set_font("Helvetica", "", 9)

        page_width = self.w - 2 * self.l_margin
        col_widths = [
            page_width * 0.4,  # 40% for Metric name
            page_width * 0.2,  # 20% for Raw Value
            page_width * 0.2,  # 20% for Weight
            page_width * 0.2   # 20% for Score
        ]

        headers = ["Metric", "Raw Value", "Weight (%)", "Score"]

        for i, h in enumerate(headers):
            self.cell(col_widths[i], 8, h, border=1, align='C')
        self.ln()

        for _, row in df.iterrows():
            if self.remaining_height < 10:
                self.add_page()
                for i, h in enumerate(headers):
                    self.cell(col_widths[i], 8, h, border=1, align='C')
                self.ln()

            metric_text = str(row["Metric"])
            if len(metric_text) > 25:
                metric_text = metric_text[:22] + "..."

            self.cell(col_widths[0], 8, metric_text, border=1)
            self.cell(col_widths[1], 8, str(row["Raw"]), border=1, align='C')
            self.cell(col_widths[2], 8, str(row["Weight"]), border=1, align='C')
            self.cell(col_widths[3], 8, str(row["Score"]), border=1, align='C')
            self.ln()

        self.ln(self.section_spacing)

    def add_all_blocks_to_pdf(self, df):
        page_width = self.w - 2 * self.l_margin

        for i, (module, metrics) in enumerate(ALL_METRIC_CLUSTERS.items()):
            title, png_bytes, diags = render_block_for_pdf(
                df,
                DASHBOARD_TITLES[module],
                metrics,
                chart_type=DEFAULT_CHART_TYPES.get(module, "line"),
            )

            if i > 0 and self.remaining_height < 60:
                self.add_page()

            self.set_font("Helvetica", "B", 11)
            self.cell(0, self.title_height, title, ln=True)

            if png_bytes:
                img_stream = BytesIO(png_bytes)
                img = Image.open(img_stream)
                img_width, img_height = img.size

                aspect_ratio = img_height / img_width
                display_width = page_width * 0.9
                display_height = display_width * aspect_ratio

                max_height = self.usable_height * 0.4
                if display_height > max_height:
                    display_height = max_height
                    display_width = display_height / aspect_ratio

                self.check_space_and_add_page(display_height + 10)

                x_offset = self.l_margin + (page_width - display_width) / 2
                current_y = self.get_y()

                self.image(img_stream, x=x_offset, y=current_y,
                          w=display_width, h=display_height)
                self.set_y(current_y + display_height + 5)

            if diags:
                valid_diags = [d for d in diags if d and d.strip()]
                if valid_diags:
                    estimated_height = len(valid_diags) * self.line_height + 10
                    self.check_space_and_add_page(estimated_height)

                    self.set_font("Helvetica", "", 9)
                    for d in valid_diags:
                        wrapped_text = textwrap.fill(d, width=80)
                        lines = wrapped_text.split('\n')

                        for line in lines:
                            if self.remaining_height < self.line_height:
                                self.add_page()

                            self.cell(page_width, self.line_height,
                                    f"- {line}" if line == lines[0] else f"  {line}",
                                    ln=True)

                    self.ln(self.section_spacing)

    def add_diagnosis(self, quadrant: str, trend: str, composite_score: float, risks: List[str]):
        base_height = 40
        risk_height = len(risks) * 8 if risks else 0
        total_height = base_height + risk_height

        self.check_space_and_add_page(total_height)

        self.set_font("Helvetica", "B", 11)
        self.cell(0, 10, "Executive Summary", ln=True)

        self.set_font("Helvetica", "", 9)

        summary_data = [
            ("Current Position:", quadrant),
            ("Trajectory:", trend),
            ("Composite Score:", f"{composite_score:.1f}/100")
        ]

        for label, value in summary_data:
            self.set_font("Helvetica", "B", 9)
            self.cell(40, 6, label, ln=False)
            self.set_font("Helvetica", "", 9)
            self.cell(0, 6, value, ln=True)

        if risks:
            self.ln(3)
            self.set_font("Helvetica", "B", 10)
            self.cell(0, 8, "Risk Alerts", ln=True)

            self.set_font("Helvetica", "", 9)
            for risk in risks:
                wrapped_risk = textwrap.fill(risk.strip(), width=85)
                lines = wrapped_risk.split('\n')

                for j, line in enumerate(lines):
                    if self.remaining_height < 6:
                        self.add_page()

                    prefix = "- " if j == 0 else "  "
                    self.cell(0, 6, f"{prefix}{line}", ln=True)
                self.ln(2)

        self.ln(self.section_spacing)


def build_full_pdf(
    png_bytes: bytes,
    score_df: pd.DataFrame,
    quadrant: str,
    trend: str,
    composite_score: float,
    risks: List[str],
    df: pd.DataFrame
) -> bytes:
    pdf = VelocityPDF()
    pdf.add_page()

    pdf.add_velocity_map(png_bytes)
    pdf.add_diagnosis(quadrant, trend, composite_score, risks)
    pdf.add_score_table(score_df)
    pdf.add_all_blocks_to_pdf(df)

    return bytes(pdf.output(dest="S"))


def png_to_pdf_bytes(png_bytes: bytes, title: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=14)
    pdf.cell(200, 10, txt=title, ln=True, align="C")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        tmp_file.write(png_bytes)
        tmp_file_path = tmp_file.name

    pdf.image(tmp_file_path, x=10, y=30, w=180)
    return bytes(pdf.output(dest="S"))

def generate_score_table(df_scored, scoring_rules):
    return pd.DataFrame([
        {
            "Metric": m,
            "Raw": f"{df_scored[m].iloc[-1]:.2f}" if m in df_scored else "N/A",
            "Weight": f"{df_scored[f'W_{m}'].iloc[-1]:.0f}%" if f"W_{m}" in df_scored else "N/A",
            "Score": f"{df_scored[f'S_{m}'].iloc[-1]:.0f}" if f"S_{m}" in df_scored else "N/A"
        }
        for m in scoring_rules
    ])

def extract_diagnostic_info(df_scored):
    quadrant = df_scored["Quadrant"].iloc[-1] if "Quadrant" in df_scored else "Unknown"
    trend = df_scored["VelocityTrend"].iloc[-1] if "VelocityTrend" in df_scored else "Flat"
    composite_score = df_scored["CompositeScore"].iloc[-1] if "CompositeScore" in df_scored else 0
    return quadrant, trend, composite_score

def detect_risks(df_scored):
    risks = []
    latest = df_scored.iloc[-1]

    if "BurnRate_kUSD" in latest and "RevenueGrowRate" in latest:
        if latest["BurnRate_kUSD"] > latest["RevenueGrowRate"] * 10:
            risks.append("Burn rate significantly exceeds revenue growth")

    if "ChurnRate_%" in latest and latest["ChurnRate_%"] > 20:
        risks.append("Churn rate exceeds 20%")

    if "CustomerRetentionRate_%" in latest and latest["CustomerRetentionRate_%"] < 50:
        risks.append("Customer retention below 50%")

    return risks