from typing import Dict

import numpy as np
import pandas as pd


def _normalize(val, rule: dict) -> float:
    if not isinstance(rule, dict) or not all(k in rule for k in ("good", "bad", "hib")):
        return np.nan
    try:
        val = float(val)
    except (TypeError, ValueError):
        return np.nan
    if np.isnan(val):
        return np.nan

    g, b, hib = rule["good"], rule["bad"], rule["hib"]
    denom = (g - b) if hib else (b - g)
    if denom == 0 or pd.isna(denom):
        return np.nan

    score = ((val - b) / denom if hib else (b - val) / denom)
    return float(np.clip(score, 0.0, 1.0) * 100.0)


def _row_score(row: pd.Series, weights: Dict[str, float]) -> float:
    total, w_sum = 0.0, 0.0
    for m, w in weights.items():
        if m not in row or pd.isna(row[m]):
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
        if m in out.columns:
            col_num = pd.to_numeric(out[m], errors="coerce")
            out[f"S_{m}"] = col_num.apply(
                lambda v: _normalize(v, SCORING_RULES[m])
            ).fillna(0.0)
        else:
            out[f"S_{m}"] = 0.0
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
        # 修复：使用正确的逻辑判断成熟阶段
        if "Month_Index" in out.columns:
            # 使用 Month_Index：超过 age_threshold 的数据点为成熟阶段
            out["_is_mature"] = out["Month_Index"] > age_threshold
        else:
            # 备用方案：基于 Month 列计算
            if "Month" in out.columns and len(out) > 0:
                # 从最早的月份开始计算
                min_month = out["Month"].min()
                # 计算 age_threshold 个月后的月份值
                start_year = min_month // 100
                start_m = min_month % 100

                total_months = (start_year * 12 + start_m - 1) + age_threshold
                cutoff_year = total_months // 12
                cutoff_month = (total_months % 12) + 1
                cutoff_yyyymm = cutoff_year * 100 + cutoff_month

                out["_is_mature"] = out["Month"] > cutoff_yyyymm
            else:
                # 如果都没有，默认前几行为早期阶段
                out["_is_mature"] = out.index > age_threshold

    def _label(r):
        if np.isnan(r["CompositeScore"]):
            return "Incomplete"
        return _quadrant_rule(r["CompositeScore"], score_threshold, r["_is_mature"])

    out["Quadrant"] = out.apply(_label, axis=1)
    out["Delta"] = out["CompositeScore"].diff()
    out.loc[out.index[0], "Delta"] = 0
    out["Trend"] = pd.cut(out["Delta"], [-np.inf, -0.5, 0.5, np.inf], labels=["down", "flat", "up"])

    return out


