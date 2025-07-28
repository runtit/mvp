# components/snapshots.py

import streamlit as st
import services.snapshot_manager as sm
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def render_snapshot_controls(df_scored, weights, age_threshold):
    if st.button("💾 Save Snapshot"):
        snap_name = sm.save(df_scored, {"weights": weights, "age_threshold": age_threshold})
        st.success(f"Snapshot {snap_name} saved!")

    st.sidebar.markdown("### 🗂 Snapshots")
    snaps = ["—"] + sm.list_snapshots()
    sel = st.sidebar.selectbox("Select a snapshot", snaps)

    if sel != "—":
        col1, col2, col3 = st.sidebar.columns(3)

        if col1.button("Load", key=f"load_{sel}"):
            df_scored, meta = sm.load(sel)
            st.session_state["_pending_snapshot"] = meta
            st.session_state["_loaded_df"] = df_scored
            st.rerun()

        if col2.button("Compare", key="cmp"):
            snap_df, _ = sm.load(sel)
            st.subheader(f"📊 Compare with {sel}")
            st.dataframe(pd.concat({
                "Current": df_scored.set_index("Month"),
                sel: snap_df.set_index("Month")
            }, axis=1), use_container_width=True)

            delta = df_scored.set_index("Month")["CompositeScore"] - snap_df.set_index("Month")["CompositeScore"]
            st.subheader("Difference in Composite Score")
            st.plotly_chart(go.Figure(go.Bar(
                x=delta.index, y=delta,
                marker_color=np.where(delta > 0, "green", "red")
            )).update_layout(height=300, template="simple_white"), use_container_width=True)

        if col3.button("🗑", key="del"):
            sm.delete(sel)
            st.sidebar.warning("Deleted")
            st.rerun()
