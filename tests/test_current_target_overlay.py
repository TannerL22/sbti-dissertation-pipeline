import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sbti_pipeline.current_target_overlay import aggregate_target_overlay, normalize_target_rows


class DummyConfig:
    def __init__(self, output_dir):
        self.output_dir = output_dir


def test_action_target_identifies_target_rows_not_status_target_set(tmp_path):
    raw = pd.DataFrame(
        {
            "row_entry_id": ["a", "b"],
            "sbti_id": [1, 1],
            "action": ["Commitment", "Target"],
            "target": [None, "Near-term"],
            "status": ["Target set", None],
            "scope": [None, "1+2"],
            "type": [None, "Absolute"],
            "base_year": [None, 2020],
            "target_year": [None, 2030],
            "target_value": [None, 50],
            "date_published": [None, "2024-01-01"],
        }
    )

    (tmp_path / "tables").mkdir()
    normalized = normalize_target_rows(DummyConfig(tmp_path), raw)

    assert normalized.loc[0, "is_commitment_row_current"] == 1
    assert normalized.loc[0, "is_target_row_current"] == 0
    assert normalized.loc[0, "is_target_set_commitment_current"] == 1
    assert normalized.loc[1, "is_target_row_current"] == 1
    assert normalized.loc[1, "is_near_term_target_row_current"] == 1


def test_target_horizon_and_target_year_validity(tmp_path):
    raw = pd.DataFrame(
        {
            "row_entry_id": ["a"],
            "sbti_id": [1],
            "action": ["Target"],
            "target": ["Near-term"],
            "status": [None],
            "scope": ["3"],
            "type": ["Absolute"],
            "base_year": [2020],
            "target_year": [2030],
            "target_value": [50],
            "date_published": ["2024-01-01"],
        }
    )

    (tmp_path / "tables").mkdir()
    normalized = normalize_target_rows(DummyConfig(tmp_path), raw)

    assert normalized.loc[0, "target_horizon_current"] == 10
    assert normalized.loc[0, "has_valid_target_year_current"] == 1
