from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_pretrend_tests_exist_for_every_clean_event_study_dv():
    pretrend = pd.read_csv(ROOT / "outputs/refactored_clean/diagnostics/pretrend_tests.csv")
    expected = {
        "roa_winsorized",
        "op_margin_winsorized",
        "revenue_growth_winsorized",
        "log_revt",
        "log_ebitda",
        "log_emp",
    }

    assert set(pretrend["dependent_variable"]) == expected
    assert pretrend["p_value"].between(0, 1).all()


def test_pretrend_markdown_report_exists():
    path = ROOT / "outputs/refactored_clean/diagnostics/pretrend_tests.md"

    assert path.exists()
    assert "Refactored-Clean Pretrend Tests" in path.read_text(encoding="utf-8")
