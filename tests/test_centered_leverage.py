from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_centered_leverage_mean_is_approximately_zero():
    diagnostics = pd.read_csv(
        ROOT / "outputs/refactored_clean/diagnostics/centered_leverage_diagnostics.csv"
    )

    assert (diagnostics["mean_centered_leverage"].abs() < 1e-12).all()


def test_centered_leverage_outputs_exist():
    result_path = ROOT / "outputs/refactored_clean/tables/centered_leverage_results.csv"
    note_path = ROOT / "outputs/refactored_clean/diagnostics/centered_leverage_interpretation.md"

    assert result_path.exists()
    assert note_path.exists()
    assert "does not replace" in note_path.read_text(encoding="utf-8")
