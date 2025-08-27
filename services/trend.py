# services/trend.py
'''
def build_trend_segments(df_scored):
    seg_dict = {t: {"x": [], "y": []} for t in ["up", "flat", "down"]}
    for i in range(len(df_scored) - 1):
        t = df_scored.iloc[i + 1]["Trend"]
        seg_dict[t]["x"] += [df_scored.iloc[i]["Month"], df_scored.iloc[i + 1]["Month"], None]
        seg_dict[t]["y"] += [df_scored.iloc[i]["CompositeScore"], df_scored.iloc[i + 1]["CompositeScore"], None]
    return seg_dict

'''


def build_trend_segments(df_scored):
    # 确保数据排序
    if "Month_Index" in df_scored.columns:
        df_sorted = df_scored.sort_values("Month_Index").reset_index(drop=True)
        x_col = "Month_Index"  # 关键改变！
    else:
        df_sorted = df_scored.sort_values("Month").reset_index(drop=True)
        x_col = "Month"

    seg_dict = {t: {"x": [], "y": []} for t in ["up", "flat", "down"]}

    for i in range(len(df_sorted) - 1):
        trend = df_sorted.iloc[i + 1]["Trend"]
        seg_dict[trend]["x"] += [
            df_sorted.iloc[i][x_col],  # 现在是 Month_Index
            df_sorted.iloc[i + 1][x_col],  # 现在是 Month_Index
            None
        ]
        seg_dict[trend]["y"] += [
            df_sorted.iloc[i]["CompositeScore"],
            df_sorted.iloc[i + 1]["CompositeScore"],
            None
        ]

    return seg_dict