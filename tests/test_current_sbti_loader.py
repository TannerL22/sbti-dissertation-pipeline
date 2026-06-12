import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sbti_pipeline.current_sbti_loader import normalize_columns


def test_normalize_columns_and_blank_row_drop_logic():
    raw = pd.DataFrame(
        {
            "SBTi ID": [1, None, 2],
            "Action": ["Target", None, "Commitment"],
            "Target": ["Near-term", None, None],
        }
    )
    normalized = normalize_columns(raw)
    cleaned = normalized.loc[~normalized.isna().all(axis=1)]

    assert list(normalized.columns) == ["sbti_id", "action", "target"]
    assert len(cleaned) == 2


def test_current_overlay_output_is_one_row_per_sbti_id():
    overlay = pd.read_csv(ROOT / "outputs/current_sbti_overlay/current_sbti_firm_overlay.csv")

    assert overlay["sbti_id"].notna().all()
    assert overlay["sbti_id"].duplicated().sum() == 0
