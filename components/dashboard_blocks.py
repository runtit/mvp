from metric_clusters import ALL_METRIC_CLUSTERS
from constant import DASHBOARD_TITLES, SCORING_RULES
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def get_existing_columns(df, desired_cols):
    """
    返回在 df 中实际存在、且至少有一个非空值的列名列表。
    用于绘图前做健壮性校验。
    """
    return [
        col for col in desired_cols
        if col in df.columns and df[col].notna().any()
    ]


def diagnose(metric: str, value: float) -> str:
    """
    返回单个指标的诊断文字（带 emoji 状态 + 提示建议），用于图表下方诊断区。
    """
    rule = SCORING_RULES.get(metric)
    if not rule:
        return ""

    tip = ""
    if rule["hib"]:  # Higher Is Better
        if value < rule["bad"]:
            tip = f"🔻 {metric}: critically low ({value})"
        elif value < rule["good"]:
            tip = f"🟡 {metric}: below target ({value})"
    else:  # Lower Is Better
        if value > rule["bad"]:
            tip = f"🔻 {metric}: critically high ({value})"
        elif value > rule["good"]:
            tip = f"🟡 {metric}: above ideal ({value})"

    if tip:
        action = rule.get("action")
        return f"{tip}" + (f" → 💡 {action}" if action else "")
    return ""

def render_block(df, title, metric_list, chart_type="line", height=280):
    with st.expander(title):
        cols = get_existing_columns(df, metric_list)
        if not cols:
            st.warning(f"No available metrics for {title}.")
            return

        if chart_type == "bar":
            fig = px.bar(df, x="Month", y=cols, barmode="group", height=height)

        elif chart_type == "pie":
            latest = df.iloc[-1]
            raw_values = [latest.get(c, 0) for c in cols]
            total = sum(raw_values)
            values = [v / total for v in raw_values] if total > 0 else [0 for _ in raw_values]

            fig = px.pie(names=cols, values=values, height=height)
            fig.update_traces(textinfo="percent+label", hovertemplate="%{label}: %{percent} ")
            st.caption(
                "This pie shows how your total identified risk breaks down by category. "
                "Each slice represents that category’s share (%) of your overall risk profile (100%), "
                "so you can see where you’re most exposed and prioritize accordingly."
            )

        elif chart_type == "radar":
            latest = df.iloc[-1]
            values = [latest.get(c, 0) for c in cols]
            labels = [c.replace("_%", "").replace("_hrs", " hrs").replace("_", " ") for c in cols]

            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=values, theta=labels, fill='toself', name="Current"))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False,
                height=height
            )
            st.caption(
                "Each axis represents a core operational metric. The shaded area shows your current performance "
                "across these metrics. Bigger and more balanced means stronger operations overall."
            )

        else:  # 默认折线图
            fig = px.line(df, x="Month", y=cols, markers=True, height=height)

        # 折线图 / 柱状图适配 hovertemplate
        if chart_type not in ["pie", "radar"]:
            fig.update_traces(hovertemplate='%{y} (%{x})')

        st.plotly_chart(fig, use_container_width=True)

        # 🔍 显示诊断
        latest_dict = df.iloc[-1].to_dict()
        for c in cols:
            diag = diagnose(c, latest_dict[c])
            if diag:
                st.warning(diag)


# 推荐每个模块对应图表类型配置（你可以自定义）
DEFAULT_CHART_TYPES = {
    "financial": "line",
    "sales": "bar",
    "operational": "radar",
    "talent": "bar",
    "customer": "bar",
    "risk": "pie"
}

def render_all_blocks(df):
    modules = list(ALL_METRIC_CLUSTERS.keys())
    for i in range(0, len(modules), 2):  # 每两列为一行
        col1, col2 = st.columns(2)
        with col1:
            m1 = modules[i]
            st.subheader(DASHBOARD_TITLES[m1])
            render_block(
                df,
                DASHBOARD_TITLES[m1],
                ALL_METRIC_CLUSTERS[m1],
                chart_type=DEFAULT_CHART_TYPES.get(m1, "line")
            )
        if i + 1 < len(modules):
            with col2:
                m2 = modules[i + 1]
                st.subheader(DASHBOARD_TITLES[m2])
                render_block(
                    df,
                    DASHBOARD_TITLES[m2],
                    ALL_METRIC_CLUSTERS[m2],
                    chart_type=DEFAULT_CHART_TYPES.get(m2, "line")
                )
