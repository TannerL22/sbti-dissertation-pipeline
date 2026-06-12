from __future__ import annotations

from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "outputs/final_polish/project_validation_report.md"


REQUIRED_FILES = [
    "configs/legacy_2012_2024.yaml",
    "configs/refactored_clean_2012_2024.yaml",
    "configs/current_sbti_overlay.yaml",
    "configs/methodology_robustness.yaml",
    "configs/methodology_robustness_4b.yaml",
    "data/derived/final_analytical_panel_v3.parquet",
    "data/raw/current_sbti/targets-excel.xlsx",
    "data/raw/current_sbti/companies-excel(2).xlsx",
    "data/raw/current_sbti/Alpha-Dashboard-Data-Dictionary(3).xlsx",
    "outputs/final_synthesis/memos/final_dissertation_update_memo.md",
    "outputs/final_synthesis/tables/final_conclusion_matrix.csv",
    "README.md",
    "docs/developer_guide.md",
    "docs/pipeline_modes.md",
    "run_pipeline.py",
]

REQUIRED_DIRS = [
    "outputs/legacy_reproduction",
    "outputs/refactored_legacy",
    "outputs/refactored_clean",
    "outputs/current_sbti_overlay",
    "outputs/methodology_robustness",
    "outputs/methodology_robustness_4b",
    "outputs/final_synthesis",
    "outputs/final_polish",
]


def validate() -> tuple[bool, list[str]]:
    messages: list[str] = []
    ok = True
    for rel in REQUIRED_FILES:
        exists = (ROOT / rel).exists()
        ok = ok and exists
        messages.append(f"- {'OK' if exists else 'MISSING'} `{rel}`")
    for rel in REQUIRED_DIRS:
        exists = (ROOT / rel).is_dir()
        ok = ok and exists
        messages.append(f"- {'OK' if exists else 'MISSING'} `{rel}/`")

    panel_path = ROOT / "data/derived/final_analytical_panel_v3.parquet"
    if panel_path.exists():
        panel_rows = len(pd.read_parquet(panel_path, columns=["sbti_id"]))
        panel_ok = panel_rows == 59496
        ok = ok and panel_ok
        messages.append(f"- {'OK' if panel_ok else 'FAIL'} canonical panel rows = {panel_rows:,}")

    overlay_path = ROOT / "outputs/current_sbti_overlay/current_sbti_firm_overlay.parquet"
    if overlay_path.exists():
        overlay = pd.read_parquet(overlay_path, columns=["sbti_id"])
        overlay_ok = overlay["sbti_id"].is_unique
        ok = ok and overlay_ok
        messages.append(f"- {'OK' if overlay_ok else 'FAIL'} current overlay one row per `sbti_id`")

    legacy_outputs = [ROOT / "outputs/legacy_reproduction", ROOT / "outputs/refactored_legacy"]
    overwrite_ok = all(path.exists() for path in legacy_outputs)
    ok = ok and overwrite_ok
    messages.append(f"- {'OK' if overwrite_ok else 'FAIL'} legacy output folders still present")
    return ok, messages


def write_report() -> bool:
    ok, messages = validate()
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    status = "PASS" if ok else "FAIL"
    lines = ["# Project Validation Report", "", f"Status: {status}", "", "## Checks", *messages]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(REPORT)
    print(status)
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if write_report() else 1)
