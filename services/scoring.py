# services/scoring.py

import pandas as pd

from services.evaluation import evaluate


def compute_scores(df, norm_weights, age_threshold, score_threshold, milestone_config):
    return evaluate(df, norm_weights, age_threshold, score_threshold, milestone_config)


def build_customdata(df_scored, metric_cols):
    hover_cols = ["Quadrant", "CompositeScore", "LaggingMetric"]

    for m in metric_cols:
        hover_cols += [m, f"W_{m}", f"S_{m}"]

    return df_scored[hover_cols].apply(
        lambda r: [None if pd.isna(x) else x for x in r], axis=1
    ).to_numpy()


def build_hovertemplate(metric_cols):
    lines = []
    for i, m in enumerate(metric_cols):
        lbl = m.replace("_%", "").replace("_kUSD", "")
        base = 3 + i * 3
        lines.append(
            f"{lbl}: "
            f"%{{customdata[{base}]:,.1f}} / "
            f"%{{customdata[{base + 1}]:,.0f}}% / "
            f"%{{customdata[{base + 2}]:,.1f}}"
        )
    return (
        "<b>Month %{x}</b><br>"
        "Composite %{customdata[1]:.1f}<br>"
        "<b>Quadrant → %{customdata[0]}</b><br>"
        "🛠️ Lagging Metric: <b>%{customdata[2]}</b><br>"
        "<b>Metric / W% / Score</b><br>" +
        "<br>".join(lines) + "<extra></extra>"
    )


