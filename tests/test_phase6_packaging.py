import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from run_pipeline import COMMANDS
from build_output_manifest import build_manifest


def test_command_registry_recognizes_all_modes():
    expected = {
        "legacy",
        "refactored-legacy",
        "refactored-clean",
        "current-overlay",
        "methodology-robustness",
        "methodology-robustness-4b",
        "final-synthesis",
        "test",
    }

    assert expected.issubset(COMMANDS)


def test_required_configs_parse_as_files():
    for rel in [
        "configs/legacy_2012_2024.yaml",
        "configs/refactored_clean_2012_2024.yaml",
        "configs/current_sbti_overlay.yaml",
        "configs/methodology_robustness.yaml",
        "configs/methodology_robustness_4b.yaml",
    ]:
        assert (ROOT / rel).exists()


def test_output_manifest_builder_indexes_final_synthesis():
    rows = build_manifest()
    paths = {row["output_path"] for row in rows}

    assert "outputs/final_synthesis/memos/final_dissertation_update_memo.md" in paths
    assert any(row["phase_mode"] == "final synthesis" for row in rows)


def test_current_overlay_remains_one_row_per_sbti_id():
    overlay = pd.read_parquet(ROOT / "outputs/current_sbti_overlay/current_sbti_firm_overlay.parquet", columns=["sbti_id"])

    assert overlay["sbti_id"].is_unique


def test_final_synthesis_files_exist():
    for rel in [
        "outputs/final_synthesis/memos/final_dissertation_update_memo.md",
        "outputs/final_synthesis/memos/methods_correction_memo.md",
        "outputs/final_synthesis/tables/final_conclusion_matrix.csv",
    ]:
        assert (ROOT / rel).exists()
