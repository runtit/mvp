import base64
import pandas as pd
import streamlit as st
from constant import SCORING_RULES
from pathlib import Path

import re
from typing import Union


def _parse_month_to_yyyymm(value, base_year=2024, base_month=1) -> Union[int, type(pd.NA)]:
    if pd.isna(value):
        return pd.NA

    s = str(value).strip()
    if not s:
        return pd.NA

    try:
        dt = pd.to_datetime(s, errors="raise")
        return int(dt.year * 100 + dt.month)
    except:
        pass

    nums = re.findall(r"\d+", s)
    if not nums:
        return pd.NA

    if len(nums) == 1:
        num = int(nums[0])

        if 19000101 <= num <= 21001231:
            y = num // 10000
            m = (num // 100) % 100
            if 1 <= m <= 12:
                return int(y * 100 + m)
            else:
                return pd.NA

        elif 190001 <= num <= 210012:
            y, m = divmod(num, 100)
            if 1 <= m <= 12:
                return int(y * 100 + m)
            else:
                return pd.NA

        elif 1900 <= num <= 2100:
            return int(num * 100 + base_month)

        elif 1 <= num <= 12:
            return int(base_year * 100 + num)

    elif len(nums) >= 2:
        y1, y2 = int(nums[0]), int(nums[1])

        if 1900 <= y1 <= 2100 and 1 <= y2 <= 12:
            return int(y1 * 100 + y2)

        elif 1 <= y1 <= 12 and 1900 <= y2 <= 2100:
            return int(y2 * 100 + y1)

    return pd.NA


def format_month_for_display(yyyymm: int) -> str:
    if pd.isna(yyyymm) or yyyymm == 0:
        return "Unknown"

    year = yyyymm // 100
    month = yyyymm % 100

    return f"{year}-{month:02d}"


def clean_df(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()

    missing_cols = [c for c in SCORING_RULES if c not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns: {', '.join(missing_cols)}")
        st.stop()

    metric_cols = [col for col in SCORING_RULES if col != "Month"]
    for col in metric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].clip(lower=-1e6, upper=1e6)

    df["__row_has_nan"] = df[metric_cols].isna().any(axis=1)

    if "Month" in df.columns:
        df["Month"] = df["Month"].apply(_parse_month_to_yyyymm)

        invalid_count = df["Month"].isna().sum()
        if invalid_count > 0:
            st.info(f" {invalid_count} rows with invalid Month format were dropped.")
            df = df.dropna(subset=["Month"])

        if len(df) > 0:
            df["Month"] = df["Month"].astype(int)

            df["Month_Display"] = df["Month"].apply(format_month_for_display)

            df = df.sort_values("Month").reset_index(drop=True)
            df["Month_Index"] = range(len(df))

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
