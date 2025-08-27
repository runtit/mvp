# components/velocity_map.py
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.risk_teasers import get_teasers, render_drilldown
from constant import TEXT_LABELS
from services.utils import render_logo_with_title, format_month_for_display

'''
def render_velocity_map_(df_scored,
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
        margin=dict(l=40, r=40, t=50, b=40),
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
'''

def render_velocity_map(df_scored, customdata, hover_tmpl, score_threshold,
                                   quadrant_config, trend_colors, use_milestone, milestone_field,
                                   milestone_op, milestone_threshold, age_threshold):
    """不需要seg_dict的velocity_map版本"""

    st.markdown(render_logo_with_title(TEXT_LABELS["velocity_map_title"]), unsafe_allow_html=True)

    y_min = min(40, df_scored["CompositeScore"].min())
    y_max = max(80, df_scored["CompositeScore"].max())

    fig = go.Figure()

    # 添加散点
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

    # 直接添加趋势线
    fig = add_trend_lines_segment_by_segment(fig, df_scored, trend_colors)

    # 添加里程碑线
    if use_milestone and "_is_mature" in df_scored.columns:
        mature_data = df_scored[df_scored["_is_mature"]]
        if len(mature_data) > 0:
            first_mature_month = mature_data["Month"].min()

            if "Month_Index" in df_scored.columns:
                milestone_matches = df_scored[df_scored["Month"] == first_mature_month]
                milestone_x = milestone_matches["Month_Index"].iloc[0] if len(milestone_matches) > 0 else 0
            else:
                milestone_x = first_mature_month

            fig.add_vline(
                x=milestone_x,
                line=dict(color="#6a0dad", width=3, dash="dot"),
                annotation_text=f"{milestone_field} {'>=' if milestone_op == '>=' else '<='} {milestone_threshold:.2f}",
                annotation_position="top"
            )
    else:
        # 修复：正确计算Early Stage Cutoff
        if "Month_Index" in df_scored.columns:
            # 方法1：使用Month_Index（推荐）
            # age_threshold是月数，直接用作Month_Index的阈值
            cutoff_x = min(age_threshold, df_scored["Month_Index"].max())
        elif "Month" in df_scored.columns:
            # 方法2：基于Month列计算
            # 从最早的月份开始，加上age_threshold个月
            df_sorted = df_scored.sort_values("Month")
            start_month = df_sorted["Month"].iloc[0]  # 最早的月份

            # 计算cutoff月份（YYYYMM格式）
            start_year = start_month // 100
            start_m = start_month % 100

            # 加上age_threshold个月
            total_months = (start_year * 12 + start_m - 1) + age_threshold
            cutoff_year = total_months // 12
            cutoff_month = (total_months % 12) + 1
            cutoff_yyyymm = cutoff_year * 100 + cutoff_month

            # 找到小于等于cutoff_yyyymm的最大Month值
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
    # 评分阈值线
    fig.add_hline(
        y=score_threshold,
        line=dict(color="black", width=3),
        annotation_text="Score Threshold",
        annotation_position="right"
    )

    # x轴设置
    if "Month_Display" in df_scored.columns and "Month_Index" in df_scored.columns:
        month_labels = df_scored["Month_Display"].tolist()
        month_indices = df_scored["Month_Index"].tolist()

        max_labels = 12
        if len(month_labels) > max_labels:
            step = len(month_labels) // max_labels
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
    """逐段绘制趋势线"""
    if "Month_Index" in df_scored.columns:
        df_sorted = df_scored.sort_values("Month_Index").reset_index(drop=True)
        x_col = "Month_Index"
    else:
        df_sorted = df_scored.sort_values("Month").reset_index(drop=True)
        x_col = "Month"

    # 为每种趋势类型准备数据
    trend_data = {trend: {"x": [], "y": []} for trend in ["up", "flat", "down"]}

    # 遍历相邻点对
    for i in range(len(df_sorted) - 1):
        current = df_sorted.iloc[i]
        next_point = df_sorted.iloc[i + 1]

        # 使用下一个点的趋势来决定线段颜色
        trend = next_point["Trend"]

        # 添加线段数据
        trend_data[trend]["x"].extend([current[x_col], next_point[x_col], None])
        trend_data[trend]["y"].extend([current["CompositeScore"], next_point["CompositeScore"], None])

    # 绘制趋势线
    for trend, data in trend_data.items():
        if data["x"]:  # 如果有数据
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