from constant import SCORING_RULES
import streamlit as st
import plotly.express as px
from constant import EXPLANATION_TEMPLATES

def get_teasers(latest_row: dict) -> list:
    """Return list of teaser strings for critically abnormal metrics."""
    teasers = []
    for metric, value in latest_row.items():
        rule = SCORING_RULES.get(metric)
        if not rule:
            continue
        if rule["hib"]:
            if value < rule["bad"]:
                teasers.append((metric, f"️ {metric.replace('_', ' ')} critically low"))
        else:
            if value > rule["bad"]:
                teasers.append((metric, f"️ {metric.replace('_', ' ')} critically high"))
    return teasers


def render_drilldown(df, metric: str, show_explanation=True):
    st.markdown(f"####  Detail for `{metric}`")

    if metric in df.columns:
        fig = px.line(df, x="Month", y=metric, markers=True, title=f"{metric} Trend")
        fig.update_xaxes(type="category")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No historical data for this metric.")

    tpl = EXPLANATION_TEMPLATES.get(metric)
    if show_explanation and tpl:
        st.markdown(f"**What's happening:** {tpl['happening']}")
        st.markdown(f"**Why it matters:** {tpl['why']}")
        st.markdown(f"**Suggested actions:** {tpl['action']}")
    elif show_explanation:
        st.info("️ No custom diagnosis available for this metric.")

    from constant import SUPPORTING_METRICS

    support = SUPPORTING_METRICS.get(metric, [])
    for supp_metric in support:
        if supp_metric in df.columns:
            fig_supp = px.line(df, x="Month", y=supp_metric, markers=True, title=f"{supp_metric} Trend")
            fig_supp.update_layout(height=250)
            st.plotly_chart(fig_supp, use_container_width=True)
