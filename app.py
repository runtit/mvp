# app.py

import streamlit as st

from components.sidebar_milestone import render_milestone_controls
from data_input import get_input_df
from services.export_utils import png_to_pdf_bytes, generate_score_table, extract_diagnostic_info, detect_risks, \
    build_full_pdf
from services.utils import clean_df
from constant import SCORING_RULES
from services.scoring import compute_scores, build_customdata, build_hovertemplate
from services.trend import build_trend_segments
from components.dashboard_blocks import render_all_blocks
from components.velocity_map import render_velocity_map
from components.snapshots import render_snapshot_controls
from components.sidebar_controls import render_weights_and_thresholds
from constant import TREND_COLORS, QUADRANT_CONFIG

# ========== 数据加载 ==========
df = get_input_df()
df = clean_df(df)

missing_cols = [c for c in SCORING_RULES if c not in df.columns]
if missing_cols:
    st.warning(f"️ Missing columns treated as NaN: {', '.join(missing_cols)}")

bad_rows = df["__row_has_nan"].sum()
if bad_rows:
    st.info(f"️ {bad_rows} rows contain NaNs and are labeled **Incomplete**.")

st.success(f"Loaded {len(df)} rows ")
with st.expander("View Raw Data"):
    st.dataframe(df, use_container_width=True)

weights, norm_weights, age_threshold = render_weights_and_thresholds(SCORING_RULES)
milestone_config = render_milestone_controls(df)
score_threshold = 60

if "_loaded_df" in st.session_state:
    df_scored = st.session_state.pop("_loaded_df")
else:
    try:
        df_scored = compute_scores(df, norm_weights, age_threshold, score_threshold, milestone_config)
    except Exception as e:
        st.error(f" Scoring failed: {e}")
        st.stop()

render_all_blocks(df)

metric_cols = list(SCORING_RULES)
customdata = build_customdata(df_scored, metric_cols)
hover_tmpl = build_hovertemplate(metric_cols)

seg_dict = build_trend_segments(df_scored)

velocity_fig = render_velocity_map(
    df_scored=df_scored,
    customdata=customdata,
    seg_dict=seg_dict,
    hover_tmpl=hover_tmpl,
    age_threshold=age_threshold,
    score_threshold=score_threshold,
    quadrant_config=QUADRANT_CONFIG,
    trend_colors=TREND_COLORS,
    use_milestone=milestone_config["enabled"],
    milestone_field=milestone_config["field"],
    milestone_op=milestone_config["op"],
    milestone_threshold=milestone_config["threshold"],
)

render_snapshot_controls(df_scored, weights, age_threshold)

with st.expander(" Export Reports & Scored Data"):
    st.download_button(
        label="️ Download Scored Data (CSV)",
        data=df_scored.to_csv(index=False).encode(),
        file_name="scored_data.csv",
        mime="text/csv"
    )
    with st.expander(" View Scored Data"):
        st.dataframe(df_scored, use_container_width=True)

    st.subheader(" Diagnostic Reports")

    full_mode = st.toggle(" Include Full Diagnosis (Score Table + Risk Analysis)", value=True)

    if st.button(" Generate PDF Report"):
        png_bytes = velocity_fig.to_image(format="png")

        if full_mode:
            score_table = generate_score_table(df_scored, SCORING_RULES)
            quadrant, trend, composite_score = extract_diagnostic_info(df_scored)
            risks = detect_risks(df_scored)

            pdf_bytes = build_full_pdf(png_bytes, score_table, quadrant, trend, composite_score, risks,df)

            file_name = "velocity_map_diagnostic.pdf"
        else:
            pdf_bytes = png_to_pdf_bytes(png_bytes, title="Velocity Map Report")
            file_name = "velocity_map_simple.pdf"

        st.download_button(
            label="️ Download PDF",
            data=pdf_bytes,
            file_name=file_name,
            mime="application/pdf"
        )