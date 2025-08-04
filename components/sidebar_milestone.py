import streamlit as st

def render_milestone_controls(df):
    st.sidebar.markdown("###  Milestone Logic")
    enabled = st.sidebar.toggle("Enable milestone-based stage")

    if not enabled:
        return {
            "enabled": False,
            "field": None,
            "op": None,
            "threshold": None
        }

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    field = st.sidebar.selectbox("Milestone Field", numeric_cols)
    op = st.sidebar.radio(
        "Operator",
        options=[">=", "<="],
        index=0,
        format_func=lambda x: {"<=": "≤", ">=": "≥"}[x],
        horizontal=True
    )

    threshold = st.sidebar.number_input("Milestone Threshold", value=50.0)

    return {
        "enabled": True,
        "field": field,
        "op": op,
        "threshold": threshold
    }

