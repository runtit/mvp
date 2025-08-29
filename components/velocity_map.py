# components/velocity_map.py
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from constant import TEXT_LABELS
from services.utils import render_logo_with_title

def render_velocity_map(df_scored, customdata, hover_tmpl, score_threshold,
                                   quadrant_config, trend_colors, use_milestone, milestone_field,
                                   milestone_op, milestone_threshold, age_threshold):

    st.markdown(render_logo_with_title(TEXT_LABELS["scale_curves_title"]), unsafe_allow_html=True)

    y_min = min(40, df_scored["CompositeScore"].min())
    y_max = max(80, df_scored["CompositeScore"].max())

    fig = go.Figure()

    for quad, meta in quadrant_config.items():
        sub = df_scored[df_scored["Quadrant"] == quad]
        if len(sub) > 0:
            x_values = sub["Month_Index"] if "Month_Index" in sub.columns else sub["Month"]

            fig.add_trace(go.Scatter(
                x=x_values,
                y=sub["CompositeScore"],
                mode="markers",
                marker=dict(color=meta["color"], size=10),
                name=meta["label"],
                customdata=customdata[sub.index],
                hovertemplate=hover_tmpl
            ))

    fig = add_trend_lines_segment_by_segment(fig, df_scored, trend_colors)

    if use_milestone and "_is_mature" in df_scored.columns:
        mature_data = df_scored[df_scored["_is_mature"]]
        if len(mature_data) > 0:
            first_mature_month = mature_data["Month"].min()

            if "Month_Index" in df_scored.columns:
                milestone_matches = df_scored[df_scored["Month"] == first_mature_month]
                if len(milestone_matches) > 0:
                    milestone_x = milestone_matches["Month_Index"].min()  # 取最早的点
                else:
                    milestone_x = df_scored["Month_Index"].min()  # fallback 更合理
            else:
                milestone_x = first_mature_month

            fig.add_vline(
                x=milestone_x,
                line=dict(color="#6a0dad", width=3, dash="dot"),
                annotation_text=f"{milestone_field} {'>=' if milestone_op == '>=' else '<='} {milestone_threshold:.2f}",
                annotation_position="top"
            )
    else:
        if "Month_Index" in df_scored.columns:
            cutoff_x = min(age_threshold-1, df_scored["Month_Index"].max())
        elif "Month" in df_scored.columns:
            df_sorted = df_scored.sort_values("Month")
            start_month = df_sorted["Month"].iloc[0]

            start_year = start_month // 100
            start_m = start_month % 100

            total_months = (start_year * 12 + start_m - 1) + age_threshold
            cutoff_year = total_months // 12
            cutoff_month = (total_months % 12) + 1
            cutoff_yyyymm = cutoff_year * 100 + cutoff_month

            cutoff_matches = df_scored[df_scored["Month"] <= cutoff_yyyymm]
            cutoff_x = cutoff_matches["Month"].max() if len(cutoff_matches) > 0 else start_month
        else:
            cutoff_x = age_threshold

        fig.add_vline(
            x=cutoff_x,
            line=dict(color="#0070f3", width=3, dash="dot"),
            annotation_text="Early Stage Cutoff",
            annotation_position="top"
            )
    fig.add_hline(
        y=score_threshold,
        line=dict(color="black", width=3),
        annotation_text="Score Threshold",
        annotation_position="right"
    )

    if "Month_Display" in df_scored.columns and "Month_Index" in df_scored.columns:
        month_labels = df_scored["Month_Display"].tolist()
        month_indices = df_scored["Month_Index"].tolist()

        max_labels = 12
        if len(month_labels) > max_labels:
            step = max(1, len(month_labels)//max_labels)
            display_indices = month_indices[::step]
            display_labels = month_labels[::step]
            if month_indices[-1] not in display_indices:
                display_indices.append(month_indices[-1])
                display_labels.append(month_labels[-1])
        else:
            display_indices = month_indices
            display_labels = month_labels

        x_axis_config = dict(
            title="Month",
            showgrid=True,
            gridcolor="rgba(0,0,0,0.15)",
            tickmode='array',
            tickvals=display_indices,
            ticktext=display_labels,
            tickangle=45
        )
        bottom_margin = 80
    else:
        x_axis_config = dict(
            title="Month",
            showgrid=True,
            gridcolor="rgba(0,0,0,0.15)"
        )
        bottom_margin = 40

    fig.update_layout(
        template="simple_white",
        width=1600, height=480,
        xaxis=x_axis_config,
        yaxis=dict(
            title="Composite Score",
            showgrid=True,
            gridcolor="rgba(0,0,0,0.15)",
            range=[y_min, y_max]
        ),
        legend_title_text="Legend",
        margin=dict(l=40, r=40, t=50, b=bottom_margin),
        clickmode="event+select"
    )

    zoom = st.checkbox("🔍 Zoom to data (un-check for full 0-100 scale)", value=True)
    fig.update_yaxes(range=[y_min, y_max] if zoom else [0, 100])
    st.plotly_chart(fig, use_container_width=False)

    return fig


def add_trend_lines_segment_by_segment(fig, df_scored, trend_colors):
    if "Month_Index" in df_scored.columns:
        df_sorted = df_scored.sort_values("Month_Index").reset_index(drop=True)
        x_col = "Month_Index"
    else:
        df_sorted = df_scored.sort_values("Month").reset_index(drop=True)
        x_col = "Month"

    trend_data = {trend: {"x": [], "y": []} for trend in ["up", "flat", "down"]}

    for i in range(len(df_sorted) - 1):
        current = df_sorted.iloc[i]
        next_point = df_sorted.iloc[i + 1]

        trend = next_point["Trend"]

        trend_data[trend]["x"].extend([current[x_col], next_point[x_col], None])
        trend_data[trend]["y"].extend([current["CompositeScore"], next_point["CompositeScore"], None])

    for trend, data in trend_data.items():
        if data["x"]:
            fig.add_trace(go.Scatter(
                x=data["x"],
                y=data["y"],
                mode="lines",
                line=dict(
                    color=trend_colors.get(trend, "gray"),
                    width=2
                ),
                name=f"Trend: {trend}",
                showlegend=True,
                connectgaps=False
            ))

    return fig