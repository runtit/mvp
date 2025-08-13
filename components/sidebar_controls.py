# components/sidebar_controls.py

import streamlit as st
import pandas as pd

def render_weights_and_thresholds(scoring_rules):
    # Snapshot override
    if "_pending_snapshot" in st.session_state:
        meta = st.session_state.pop("_pending_snapshot")
        for k, v in meta["weights"].items():
            st.session_state[f"w_{k}"] = v
        st.session_state["age_threshold"] = meta["age_threshold"]

    weights = {
        m: st.sidebar.slider(
            m, 0, 100,
            st.session_state.get(f"w_{m}", 10), 1, key=f"w_{m}"
        )
        for m in scoring_rules
    }

    total = sum(weights.values()) or 1
    norm_weights = {k: v / total for k, v in weights.items()}

    MAX_WARN = 0.8
    over = [k for k, v in norm_weights.items() if v > MAX_WARN]
    if over:
        st.sidebar.error(f"️ The proportion {', '.join(over)} is over {MAX_WARN*100:.0f}%, which may bias scoring.")

    with st.sidebar.expander(" How do the weights work?"):
        st.markdown("""
        - The sliders set raw weights.
        - The system normalizes them to total 100%.
        - Effective % = raw ÷ total raw.
        - Recommended: keep any single metric ≤ 40%.
        """)

    st.sidebar.markdown("####  Actual proportion (%)")
    norm_df = (pd.Series(norm_weights) * 100).round(1).to_frame("Effective %")
    st.sidebar.dataframe(norm_df, height=200)

    age_threshold = st.sidebar.number_input(
        "Early-Stage Cutoff (months)",
        min_value=0,
        max_value=None,
        value=12,
        step=1
    )

    return weights, norm_weights, age_threshold
