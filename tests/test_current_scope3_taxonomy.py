import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sbti_pipeline.current_target_overlay import aggregate_target_overlay, normalize_target_rows


class DummyConfig:
    def __init__(self, output_dir):
        self.output_dir = output_dir


def test_standalone_scope3_absolute_is_distinct_from_scope_includes_3(tmp_path):
    raw = pd.DataFrame(
        {
            "row_entry_id": ["standalone", "combined"],
            "sbti_id": [1, 2],
            "action": ["Target", "Target"],
            "target": ["Near-term", "Near-term"],
            "status": [None, None],
            "scope": ["3", "1+2+3"],
            "type": ["Absolute", "Absolute"],
            "base_year": [2020, 2020],
            "target_year": [2030, 2030],
            "target_value": [50, 50],
            "date_published": ["2024-01-01", "2024-01-01"],
        }
    )

    (tmp_path / "tables").mkdir()
    config = DummyConfig(tmp_path)
    rows = normalize_target_rows(config, raw)
    firm = aggregate_target_overlay(config, rows).set_index("sbti_id")

    assert firm.loc[1, "current_has_legacy_like_absolute_scope3_target"] == 1
    assert firm.loc[1, "current_has_any_target_including_scope3"] == 1
    assert firm.loc[2, "current_has_legacy_like_absolute_scope3_target"] == 0
    assert firm.loc[2, "current_has_any_target_including_scope3"] == 1


def test_scope3_type_taxonomy_records_multiple_types(tmp_path):
    raw = pd.DataFrame(
        {
            "row_entry_id": ["a", "b"],
            "sbti_id": [1, 1],
            "action": ["Target", "Target"],
            "target": ["Near-term", "Near-term"],
            "status": [None, None],
            "scope": ["3", "1+2+3"],
            "type": ["Engagement", "Intensity"],
            "base_year": [None, 2020],
            "target_year": [None, 2030],
            "target_value": [None, 10],
            "date_published": ["2024-01-01", "2024-01-01"],
        }
    )

    (tmp_path / "tables").mkdir()
    config = DummyConfig(tmp_path)
    rows = normalize_target_rows(config, raw)
    firm = aggregate_target_overlay(config, rows).set_index("sbti_id")

    assert firm.loc[1, "current_has_engagement_target_including_scope3"] == 1
    assert firm.loc[1, "current_has_intensity_target_including_scope3"] == 1
    assert firm.loc[1, "current_scope3_target_type_count"] == 2
