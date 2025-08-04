from typing import List, Dict, Any

import streamlit as st
import pandas as pd

from services.synthetic import generate_synthetic_company_data

MANUAL_COLS: List[str] = [
    "Month",
    "RevenueGrowthRate_%",
    "BurnRate_kUSD",
    "CustomerRetentionRate_%",
    "ChurnRate_%",
    "MRR_kUSD",
    "GrossMargin_%",
    "OperationalEfficiency_%",
    "UserEngagement_%",
    "RegulatoryComplianceRisk_%",
]

TEXT_COLS: List[str] =[]


def get_input_df() ->pd.DataFrame:
    if "manual_df" not in st.session_state:
        st.session_state.manual_df = pd.DataFrame(columns=MANUAL_COLS)
    if "active_df" not in st.session_state:
        st.session_state.active_df = None


    st.sidebar.header("Data Input")
    upload_file = st.sidebar.file_uploader("Upload CSV / XLSX", ["csv","xlsx"],key="file_upload_main")
    demo = st.sidebar.button("Generate Demo")
    manual_on = st.sidebar.toggle("manual entry form")

    if demo:
        st.session_state.active_df = generate_synthetic_company_data(seed=42)
        st.sidebar.success("Demo data generated!")

    if upload_file:
        st.session_state.active_df = pd.read_csv(upload_file) \
            if upload_file.name.endswith("csv") \
            else pd.read_excel(upload_file)
        st.sidebar.success(f"Loaded {upload_file.name}")

    if manual_on:
        _render_manual_form()
        if not st.session_state.manual_df.empty:
            st.session_state.active_df = st.session_state.manual_df.copy()

    if st.session_state.active_df is not None:
        return st.session_state.active_df

    st.info(" Upload a file, generate demo data, or add rows manually.")
    st.stop()

def _render_manual_form() -> None:
    with st.sidebar.expander("Add new row"):
        with st.form("manual_form", clear_on_submit=True):
            inputs:Dict[str,Any] = {}
            for col in MANUAL_COLS:
                if col in TEXT_COLS:
                    inputs[col] = st.text_input(col)
                elif col=="Month":
                    inputs[col] = st.number_input(col,min_value=1,step=1)
                else:
                    inputs[col] = st.number_input(col,value=0.0)
            if st.form_submit_button("Add"):
                st.session_state.manual_df.loc[len(st.session_state.manual_df)]=inputs
                st.success("Row added!")

    if not st.session_state.manual_df.empty:
        st.sidebar.markdown("#### Current manual data")
        st.sidebar.dataframe(st.session_state.manual_df.reset_index(drop=True),
                             use_container_width=True,
                             height=220)

        row_opts = st.session_state.manual_df.index.tolist()
        del_idx = st.sidebar.selectbox(
            "Select row to delete", row_opts,
            format_func=lambda i:f"Row{i}"
        )

        if st.sidebar.button("Delete selected row"):
            st.session_state.manual_df.drop(del_idx,inplace=True)
            st.session_state.manual_df.reset_index(drop=True,inplace=True)
            st.sidebar.success(f"Row {del_idx} deleted!")
            st.rerun()

        if st.sidebar.button("Clear all manual data"):
            st.session_state.manual_df = pd.DataFrame(columns=MANUAL_COLS)
            st.session_state.active_df = st.session_state.manual_df
            st.sidebar.warning("All manual data cleared.")
            st.rerun()

        st.sidebar.download_button(
            "Export manual data CSV",
            st.session_state.manual_df.to_csv(index=False).encode(),
            "manual_data.csv",
            mime="text/csv"
        )

    st.sidebar.download_button(
        "Download empty template",
        pd.DataFrame(columns= MANUAL_COLS).to_csv(index=False).encode(),
        "startup_template.csv",
        mime="text/csv"
    )
