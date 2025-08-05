from typing import Dict

import numpy as np
import pandas as pd


def _normalize(val:float,rule:dict)->float:
    g,b,hib = rule["good"], rule["bad"], rule["hib"]
    if np.isnan(val):
        return np.nan

    if hib:
        score = np.clip((val - b) / (g - b), 0, 1) * 100
    else:
        score = np.clip((b - val) / (b - g), 0, 1) * 100
    return float(score)

def _row_score(row: pd.Series, weights: Dict[str, float]) -> float:
    total, w_sum = 0.0, 0.0
    for m, w in weights.items():
        if m not in row:
            continue
        score = _normalize(row[m], SCORING_RULES[m])
        if not np.isnan(score):
            total += score * w
            w_sum += w
    return total / w_sum if w_sum else np.nan

from constant import QUADRANT_LABELS, SCORING_RULES


def _quadrant_rule(score, score_threshold=60, is_mature=False):
    if score >= score_threshold and is_mature:
        return QUADRANT_LABELS["q1"]  # Technologically Elite
    elif score >= score_threshold and not is_mature:
        return QUADRANT_LABELS["q2"]  # Feasible
    elif score < score_threshold and is_mature:
        return QUADRANT_LABELS["q4"]  # Failing
    else:
        return QUADRANT_LABELS["q3"]  # Pre-Concept Barrier



def evaluate(df, weights, age_threshold=12, score_threshold=60, milestone_config=None):
    out = df.copy()
    out["CompositeScore"] = out.apply(_row_score, axis=1, weights=weights)

    for m in weights:
        out[f"S_{m}"] = out[m].apply(lambda v: _normalize(v, SCORING_RULES[m]))
        out[f"W_{m}"] = weights[m] * 100

    def _weakest_metric(row):
        scores = {
            m: row[f"S_{m}"] * weights[m]
            if f"S_{m}" in row and not pd.isna(row[f"S_{m}"])
            else np.inf
            for m in weights
        }
        return min(scores, key=scores.get) if scores else None

    out["LaggingMetric"] = (
        out.apply(_weakest_metric, axis=1)
            .str.replace("_%", "", regex=False)
            .str.replace("_kUSD", "", regex=False)
    )

    out["_is_mature"] = False
    if milestone_config and milestone_config.get("enabled"):
        field = milestone_config.get("field")
        op = milestone_config.get("op")
        threshold = milestone_config.get("threshold")

        if field in out.columns:
            if op == ">=":
                mature_mask = out[field] >= threshold
            elif op == "<=":
                mature_mask = out[field] <= threshold
            else:
                raise ValueError("Unsupported milestone operator")

            met_indices = out.index[mature_mask]
            if len(met_indices) > 0:
                first_idx = met_indices[0]
                out.loc[first_idx:, "_is_mature"] = True
    else:
        out["_is_mature"] = out["Month"] >= age_threshold

    def _label(r):
        if np.isnan(r["CompositeScore"]):
            return "Incomplete"
        return _quadrant_rule(r["CompositeScore"], score_threshold, r["_is_mature"])

    out["Quadrant"] = out.apply(_label, axis=1)
    out["Delta"] = out["CompositeScore"].diff()
    out.loc[out.index[0], "Delta"] = 0
    out["Trend"] = pd.cut(out["Delta"], [-np.inf, -0.5, 0.5, np.inf], labels=["down", "flat", "up"])

    return out


