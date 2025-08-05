import pandas as pd

from constant import SCORING_RULES


def clean_df(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()

    df = df.apply(pd.to_numeric, errors="coerce")

    num_cols = df.select_dtypes("number").columns
    df[num_cols] = df[num_cols].clip(lower=-1e6, upper=1e6)

    existing_cols = [c for c in SCORING_RULES if c in df.columns]
    if existing_cols:
        df["__row_has_nan"] = df[existing_cols].isna().any(axis=1)
    else:
        df["__row_has_nan"] = True

    if "Month" in df.columns:
        df["Month"] = pd.to_numeric(df["Month"], errors="coerce").fillna(0).astype(int)
        df = df.sort_values("Month").reset_index(drop=True)

    return df


