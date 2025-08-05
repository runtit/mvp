import pandas as pd

from constant import SCORING_RULES


def clean_df(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()

    df = df.apply(pd.to_numeric, errors="coerce")

    num_cols = df.select_dtypes("number").columns
    df[num_cols] = df[num_cols].clip(lower=-1e6, upper=1e6)

    df["__row_has_nan"] = df[list(SCORING_RULES)].isna().any(axis=1)
    return df
