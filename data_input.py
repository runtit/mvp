from typing import List, Dict, Any

import pdfplumber
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
    upload_file = st.sidebar.file_uploader("Upload CSV / XLSX / PDF", ["csv","xlsx", "PDF"], key="file_upload_main")
    demo = st.sidebar.button("Generate Demo")
    st.sidebar.download_button(
        "Download empty template",
        pd.DataFrame(columns=MANUAL_COLS).to_csv(index=False).encode(),
        "startup_template.csv",
        mime="text/csv"
    )
    manual_on = st.sidebar.toggle("manual entry form")


    if demo:
        st.session_state.active_df = generate_synthetic_company_data(seed=42)
        st.sidebar.success("Demo data generated!")

    if upload_file:
        filename = upload_file.name.lower()
        if filename.endswith("csv"):
            st.session_state.active_df = pd.read_csv(upload_file)
        elif filename.endswith("xlsx"):
            st.session_state.active_df = pd.read_excel(upload_file)
        elif filename.endswith("pdf"):
            df_pdf = parse_pdf_flexible(upload_file, min_cols=1)
            if df_pdf.empty:
                st.warning(" No readable tables detected in the uploaded PDF.")
                st.stop()
            else:
                st.session_state.active_df = df_pdf
                st.sidebar.success(f"Loaded PDF with {df_pdf.shape[0]} rows and {df_pdf.shape[1]} columns")

        else:
            st.warning("Unsupported file format. Please upload CSV, XLSX, or PDF.")
            st.stop()

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
import pdfplumber
import pandas as pd

def parse_pdf_flexible(upload_file, min_cols: int = 1) -> pd.DataFrame:
    """
    通用 PDF 表格解析：
    - 表头相同 → 跨页 → 按行追加
    - 表头不同 → 宽表 → 按列追加
    - 自动清洗列名 & 最后补齐缺失指标
    """
    df = pd.DataFrame()
    last_header = None

    with pdfplumber.open(upload_file) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            rows = []
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    rows.extend(table)
            else:
                text = page.extract_text()
                if text:
                    for line in text.splitlines():
                        parts = line.split()
                        if len(parts) >= min_cols:
                            rows.append(parts)

            if not rows:
                continue

            # 🔑 清洗列名（去掉空格和隐藏字符）
            header = [h.strip().replace("\u200b", "") for h in rows[0]]
            data = rows[1:]
            df_page = pd.DataFrame(data, columns=header)

            if df.empty:
                df = df_page
                last_header = header
            else:
                if header == last_header:
                    df = pd.concat([df, df_page], ignore_index=True)
                else:
                    max_len = max(len(df), len(df_page))
                    df = df.reindex(range(max_len)).reset_index(drop=True)
                    df_page = df_page.reindex(range(max_len)).reset_index(drop=True)
                    df = pd.concat([df, df_page], axis=1)
                    last_header = header

    try:
        from constant import SCORING_RULES
        for col in SCORING_RULES:
            if col not in df.columns:
                df[col] = None
    except ImportError:
        pass  

    return df

