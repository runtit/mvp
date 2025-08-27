import base64
import pandas as pd
import streamlit as st
from constant import SCORING_RULES
from pathlib import Path


def clean_df(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()

    missing_cols = [c for c in SCORING_RULES if c not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns: {', '.join(missing_cols)}")
        st.stop()

    for col in SCORING_RULES:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].clip(lower=-1e6, upper=1e6)

    df["__row_has_nan"] = df[list(SCORING_RULES)].isna().any(axis=1)

    if "Month" in df.columns:
        df["Month"] = pd.to_numeric(df["Month"], errors="coerce").fillna(0).astype(int)
        df = df.sort_values("Month").reset_index(drop=True)

    return df


def get_img_as_base64(file_path):
    return base64.b64encode(Path(file_path).read_bytes()).decode()


def render_brand_logo(where="sidebar", width=100, return_html=False):
    theme = st.get_option("theme.base")
    logo_path = "resources/logo_transparent_dark.png" if theme == "dark" else "resources/logo_transparent.png"
    logo_base64 = get_img_as_base64(logo_path)
    img_html = f"<img src='data:image/png;base64,{logo_base64}' width='{width}'>"

    if return_html:
        return img_html

    if where == "sidebar":
        st.sidebar.markdown(img_html, unsafe_allow_html=True)
    else:
        st.markdown(img_html, unsafe_allow_html=True)


def render_logo_with_title(title):
    theme = st.get_option("theme.base")
    logo_path = "resources/logo_dark.png" if theme == "dark" else "resources/logo_transparent.png"
    logo_base64 = get_img_as_base64(logo_path)
    return f"""
    <div style='display: flex; align-items: center; gap: 16px;'>
        <img src='data:image/png;base64,{logo_base64}' style='width:120px; height:auto;'>
        <h2 style='margin:0; font-size:2rem;'>{title}</h2>
    </div>
    """
