import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sbti_pipeline.current_sector_flags import build_sector_flags


class DummyConfig:
    def __init__(self, output_dir):
        self.output_dir = output_dir


def test_finance_flag_from_organization_type(tmp_path):
    company = pd.DataFrame(
        {
            "sbti_id": [1],
            "sector_current": ["Professional Services"],
            "organization_type_current": ["Financial Institution"],
        }
    )
    target_rows = pd.DataFrame(
        {"sbti_id": [1], "reason_for_commitment_extension_or_removal_current": [None], "is_no_deforestation_target_current": [0]}
    )

    (tmp_path / "tables").mkdir()
    (tmp_path / "diagnostics").mkdir()
    flags = build_sector_flags(DummyConfig(tmp_path), company, target_rows, pd.DataFrame())

    assert flags.loc[0, "current_is_financial_institution"] == 1


def test_automotive_and_flag_proxies_use_sector_and_observed_reason_or_target(tmp_path):
    company = pd.DataFrame(
        {
            "sbti_id": [1, 2],
            "sector_current": ["Automobiles and Components", "Professional Services"],
            "organization_type_current": ["Corporate", "Corporate"],
        }
    )
    target_rows = pd.DataFrame(
        {
            "sbti_id": [1, 2],
            "reason_for_commitment_extension_or_removal_current": ["Automakers pathway", "Timber and Wood Fiber Pathway"],
            "is_no_deforestation_target_current": [0, 1],
        }
    )

    (tmp_path / "tables").mkdir()
    (tmp_path / "diagnostics").mkdir()
    flags = build_sector_flags(DummyConfig(tmp_path), company, target_rows, pd.DataFrame()).set_index("sbti_id")

    assert flags.loc[1, "current_is_automotive_any"] == 1
    assert flags.loc[2, "current_has_observed_flag_target_proxy"] == 1
    assert flags.loc[2, "current_is_flag_relevant_any"] == 1
