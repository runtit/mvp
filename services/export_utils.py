from fpdf import FPDF
from typing import List
import pandas as pd
import tempfile

def png_to_pdf_bytes(png_bytes: bytes, title: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=14)
    pdf.cell(200, 10, txt=title, ln=True, align="C")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        tmp_file.write(png_bytes)
        tmp_file_path = tmp_file.name

    pdf.image(tmp_file_path, x=10, y=30, w=180)

    return bytes(pdf.output(dest="S"))  # 👈 关键在这

# 构造评分表格（供 PDF 报告使用）
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

# 获取象限、趋势、总分
def extract_diagnostic_info(df_scored):
    quadrant = df_scored["Quadrant"].iloc[-1] if "Quadrant" in df_scored else "Unknown"
    trend = df_scored["VelocityTrend"].iloc[-1] if "VelocityTrend" in df_scored else "Flat"
    composite_score = df_scored["CompositeScore"].iloc[-1] if "CompositeScore" in df_scored else 0
    return quadrant, trend, composite_score

# 风险提示逻辑（可拓展）
def detect_risks(df_scored):
    risks = []
    latest = df_scored.iloc[-1]

    if "BurnRate_kUSD" in latest and "RevenueGrowRate" in latest:
        if latest["BurnRate_kUSD"] > latest["RevenueGrowRate"] * 10:
            risks.append(" Burn rate significantly exceeds revenue growth")

    if "ChurnRate_%" in latest and latest["ChurnRate_%"] > 20:
        risks.append(" Churn rate exceeds 20%")

    if "CustomerRetentionRate_%" in latest and latest["CustomerRetentionRate_%"] < 50:
        risks.append(" Customer retention below 50%")

    return risks

class VelocityPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 10, "Velocity Map Diagnostic Report", ln=True, align="C")
        self.set_y(50)

    def add_velocity_map(self, image_bytes: bytes):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            tmp_file.write(image_bytes)
            tmp_file_path = tmp_file.name
        self.image(tmp_file_path, x=10, y=30, w=180)
        self.set_y(170)

    def add_score_table(self, df: pd.DataFrame):
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 10, "Metric Score Breakdown ( Lastest Month )", ln=True)
        self.set_font("Helvetica", "", 9)

        col_widths = [50, 30, 30, 30]
        headers = ["Metric", "Raw Value", "Weight (%)", "Standardized Score"]
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 8, h, border=1)
        self.ln()

        for _, row in df.iterrows():
            self.cell(col_widths[0], 8, str(row["Metric"]), border=1)
            self.cell(col_widths[1], 8, str(row["Raw"]), border=1)
            self.cell(col_widths[2], 8, str(row["Weight"]), border=1)
            self.cell(col_widths[3], 8, str(row["Score"]), border=1)
            self.ln()

    def add_diagnosis(self, quadrant: str, trend: str, composite_score: float, risks: List[str]):
        # 避免在页底输出导致重叠
        if self.get_y() > 240:
            self.add_page()
            self.set_y(30)  # ✅ 设置合理的起始 Y 坐标（30 比较合适）

        self.ln(5)
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 10, "Summary Diagnosis (Latest Month)", ln=True)

        self.set_font("Helvetica", "", 9)
        self.multi_cell(0, 6, f"Quadrant: {quadrant}\nTrajectory: {trend}\nComposite Score: {composite_score:.1f}")

        if risks:
            self.ln(2)
            self.set_font("Helvetica", "B", 9)
            self.cell(0, 8, "Risk Flags", ln=True)

            self.set_font("Helvetica", "", 9)
            for risk in risks:
                self.multi_cell(0, 5, f"- {risk}")
                self.ln(1)


def build_full_pdf(
    png_bytes: bytes,
    score_df: pd.DataFrame,
    quadrant: str,
    trend: str,
    composite_score: float,
    risks: List[str]
) -> bytes:
    pdf = VelocityPDF()
    pdf.add_page()
    pdf.add_velocity_map(png_bytes)
    pdf.add_score_table(score_df)
    pdf.add_diagnosis(quadrant, trend, composite_score, risks)
    return bytes(pdf.output(dest="S"))
