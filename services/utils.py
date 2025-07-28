import pandas as pd

from constant import SCORING_RULES


def clean_df(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    ① 所有字段强制转数值（非法文本→NaN）
    ② 把所有数值裁剪到 [-1e6, 1e6]
    ③ 生成布尔列 __row_has_nan 供 UI 提示
    """
    df = df_raw.copy()

    # 1. 强制变数值
    df = df.apply(pd.to_numeric, errors="coerce")

    # 2. 裁剪极值
    num_cols = df.select_dtypes("number").columns
    df[num_cols] = df[num_cols].clip(lower=-1e6, upper=1e6)

    # 3. 标记脏行
    df["__row_has_nan"] = df[list(SCORING_RULES)].isna().any(axis=1)
    return df
