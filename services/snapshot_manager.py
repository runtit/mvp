from pathlib import Path
import json, pandas as pd

SNAP_DIR = Path("snapshots")
SNAP_DIR.mkdir(exist_ok=True)


def save(df_scored: pd.DataFrame, meta: dict):
    ts = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    df_scored.to_parquet(SNAP_DIR / f"{ts}.parquet")
    (SNAP_DIR / f"{ts}.meta.json").write_text(json.dumps(meta))
    return ts


def list_snapshots():
    return sorted([p.stem for p in SNAP_DIR.glob("*.parquet")], reverse=True)


def load(name: str):
    df   = pd.read_parquet(SNAP_DIR / f"{name}.parquet")
    meta = json.loads((SNAP_DIR / f"{name}.meta.json").read_text())
    return df, meta


def delete(name: str):
    (SNAP_DIR / f"{name}.parquet").unlink(missing_ok=True)
    (SNAP_DIR / f"{name}.meta.json").unlink(missing_ok=True)
