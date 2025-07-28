# services/trend.py

def build_trend_segments(df_scored):
    seg_dict = {t: {"x": [], "y": []} for t in ["up", "flat", "down"]}
    for i in range(len(df_scored) - 1):
        t = df_scored.iloc[i + 1]["Trend"]
        seg_dict[t]["x"] += [df_scored.iloc[i]["Month"], df_scored.iloc[i + 1]["Month"], None]
        seg_dict[t]["y"] += [df_scored.iloc[i]["CompositeScore"], df_scored.iloc[i + 1]["CompositeScore"], None]
    return seg_dict
