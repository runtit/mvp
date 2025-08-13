# components/velocity_map.py
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.risk_teasers import get_teasers, render_drilldown
from constant import TEXT_LABELS
from services.utils import render_logo_with_title


def render_velocity_map(df_scored,
    customdata,
    seg_dict,
    hover_tmpl,
    score_threshold,
    quadrant_config,
    trend_colors,
    use_milestone,
    milestone_field,
    milestone_op,
    milestone_threshold,
    age_threshold,):

    st.markdown(render_logo_with_title(TEXT_LABELS["velocity_map_title"]), unsafe_allow_html=True)


    y_min = min(40, df_scored["CompositeScore"].min())
    y_max = max(80, df_scored["CompositeScore"].max())

    fig = go.Figure()

    for quad, meta in quadrant_config.items():
        sub = df_scored[df_scored["Quadrant"] == quad]
        fig.add_trace(go.Scatter(
            x=sub["Month"], y=sub["CompositeScore"],
            mode="markers",
            marker=dict(color=meta["color"], size=10),
            name=meta["label"],
            customdata=customdata[sub.index],
            hovertemplate=hover_tmpl
        ))

    for t in ["up", "flat", "down"]:
        fig.add_trace(go.Scatter(
            x=seg_dict[t]["x"],
            y=seg_dict[t]["y"],
            mode="lines",
            line=dict(color=trend_colors[t], width=1.5),
            name=f"Trend: {t}"
        ))

    if use_milestone:
        met = milestone_field
        op_text = "≥" if milestone_op == ">=" else "≤"
        first_met = df_scored[df_scored["_is_mature"]]["Month"].min()
        if pd.notna(first_met):
            fig.add_vline(
                x=first_met,
                line=dict(color="#6a0dad", width=3, dash="dot"),
                annotation_text=f"{met} {op_text} {milestone_threshold:.2f}",
                annotation_position="top",
                annotation=dict(yshift=10)
            )
    else:
        fig.add_vline(
            x=age_threshold,
            line=dict(color="#0070f3", width=3, dash="dot"),
            annotation_text="Early Stage Cutoff",
            annotation_position="top",
            annotation=dict(yshift=10)
        )

    fig.add_hline(y=score_threshold, line=dict(color="black", width=3),
                  annotation_text="Score Threshold", annotation_position="right", annotation=dict(xshift=15))

    fig.update_layout(
        template="simple_white",
        width=1600, height=480,
        xaxis=dict(title=TEXT_LABELS["x_axis_label"], showgrid=True, gridcolor="rgba(0,0,0,0.15)", linecolor="black", mirror=True, dtick=2),
        yaxis=dict(title=TEXT_LABELS["y_axis_label"], showgrid=True, gridcolor="rgba(0,0,0,0.15)", linecolor="black", mirror=True, range=[y_min, y_max]),
        legend_title_text="Legend",
        margin=dict(l=40, r=40, t=30, b=40),
        clickmode="event+select"
    )

    zoom = st.checkbox(" Zoom to data (un-check for full 0-100 scale)", value=True)
    fig.update_yaxes(range=[y_min, y_max] if zoom else [0, 100])
    st.plotly_chart(fig, use_container_width=False)

    # === Add Risk Teasers after chart ===
    st.markdown("###  Risk Teasers")
    latest = df_scored.iloc[-1].to_dict()
    teasers = get_teasers(latest)

    if not teasers:
        st.success(" No critical risks detected in latest snapshot.")
    else:
        for metric, teaser in teasers:
            with st.expander(teaser):
                render_drilldown(df_scored, metric)
    return fig
