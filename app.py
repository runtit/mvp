import streamlit as st

from components.sidebar_milestone import render_milestone_controls
from data_input import get_input_df
from services.export_utils import png_to_pdf_bytes, generate_score_table, extract_diagnostic_info, detect_risks, \
    build_full_pdf
from services.utils import clean_df, render_brand_logo
from constant import SCORING_RULES
from services.scoring import compute_scores, build_customdata, build_hovertemplate
from components.dashboard_blocks import render_all_blocks
from components.velocity_map import render_velocity_map
from components.sidebar_controls import render_weights_and_thresholds
from constant import TREND_COLORS, QUADRANT_CONFIG
from services.utils import format_month_for_display


render_brand_logo(where="sidebar", width=100)

df = get_input_df()
df = clean_df(df)

import pandas as pd

st.sidebar.markdown("### Month Range (Snapshot)")

month_num = None
if "Month" in df.columns:
    month_num = pd.to_numeric(df["Month"], errors="coerce")

if month_num is None or not month_num.notna().any():
    st.sidebar.caption("No valid numeric 'Month' found; snapshot disabled.")
    st.session_state.pop("snap_active", None)
    st.session_state.pop("snap_range", None)

else:
    valid_months = month_num.dropna().astype(int).sort_values().tolist()

    if len(valid_months) == 1:
        month_val = valid_months[0]
        st.sidebar.caption(f"Only one month available: {format_month_for_display(month_val)}")
        st.session_state["snap_active"] = True
        st.session_state["snap_range"] = (month_val, month_val)

    else:
        # 创建月份选项
        month_options = {format_month_for_display(m): m for m in valid_months}
        month_labels = list(month_options.keys())

        # 起始月份选择
        start_label = st.sidebar.selectbox(
            "Start Month",
            options=month_labels,
            index=0
        )

        # 结束月份选择（只显示起始月份之后的选项）
        start_idx = month_labels.index(start_label)
        end_options = month_labels[start_idx:]

        end_label = st.sidebar.selectbox(
            "End Month",
            options=end_options,
            index=len(end_options) - 1  # 默认选择最后一个
        )

        c1, c2 = st.sidebar.columns(2)
        if c1.button("Apply Snapshot"):
            start_m = month_options[start_label]
            end_m = month_options[end_label]
            st.session_state["snap_active"] = True
            st.session_state["snap_range"] = (int(start_m), int(end_m))
            st.rerun()

        if c2.button("Clear"):
            st.session_state["snap_active"] = False
            st.session_state["snap_range"] = None

if st.session_state.get("snap_active") and st.session_state.get("snap_range"):
    sm, em = st.session_state["snap_range"]
    mask = pd.to_numeric(df["Month"], errors="coerce").between(sm, em, inclusive="both")
    df = df.loc[mask].sort_values("Month").reset_index(drop=True)
    st.caption(f"Snapshot active: Month {sm} → {em}")


bad_rows = df["__row_has_nan"].sum()
if bad_rows:
    st.info(f"️ {bad_rows} rows contain NaNs and are labeled.")

st.success(f"Loaded {len(df)} rows ")
with st.expander("View Raw Data"):
    st.dataframe(df, use_container_width=True)

weights, norm_weights, age_threshold = render_weights_and_thresholds(SCORING_RULES, df)
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
velocity_fig = render_velocity_map(
    df_scored, customdata, hover_tmpl, score_threshold,
    QUADRANT_CONFIG, TREND_COLORS, milestone_config["enabled"], milestone_config["field"],
    milestone_config["op"], milestone_config["threshold"], age_threshold
)

#render_snapshot_controls(df_scored, weights, age_threshold)

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

            file_name = "scale_curves_diagnostic.pdf"
        else:
            pdf_bytes = png_to_pdf_bytes(png_bytes, title="Scale_Curves Report")
            file_name = "Scale_Curves_Report.pdf"

        st.download_button(
            label="️ Download PDF",
            data=pdf_bytes,
            file_name=file_name,
            mime="application/pdf"
        )