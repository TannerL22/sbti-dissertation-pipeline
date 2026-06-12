from __future__ import annotations

from pathlib import Path
import csv
from datetime import datetime


ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = ROOT / "outputs"


MODE_MAP = {
    "legacy_reproduction": ("legacy reproduction", "canonical/archived"),
    "refactored_legacy": ("refactored legacy", "canonical"),
    "refactored_clean": ("refactored clean", "diagnostic"),
    "current_sbti_overlay": ("current SBTi overlay", "diagnostic"),
    "methodology_robustness": ("methodology robustness", "robustness"),
    "methodology_robustness_4b": ("methodology robustness 4B", "robustness"),
    "final_synthesis": ("final synthesis", "canonical"),
    "final_polish": ("final polish", "diagnostic"),
}


def classify(path: Path) -> tuple[str, str, bool, str]:
    rel = path.relative_to(OUTPUT_ROOT)
    top = rel.parts[0] if rel.parts else ""
    mode, category = MODE_MAP.get(top, ("other outputs", "diagnostic"))
    safe_to_cite = category in {"canonical", "robustness", "diagnostic"} and "preview" not in path.name.lower()
    description = _description(path)
    return mode, category, safe_to_cite, description


def _description(path: Path) -> str:
    name = path.name
    if name.endswith(".md"):
        return "Readable report or memo"
    if name.endswith(".csv"):
        return "Machine-readable table"
    if name.endswith(".parquet"):
        return "Parquet data artifact"
    if name.endswith(".png"):
        return "Figure"
    if name.endswith(".txt"):
        return "Text output"
    return "Generated output"


def build_manifest() -> list[dict[str, str]]:
    rows = []
    for path in sorted(OUTPUT_ROOT.rglob("*")):
        if not path.is_file():
            continue
        mode, category, safe_to_cite, description = classify(path)
        stat = path.stat()
        rows.append(
            {
                "output_path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "phase_mode": mode,
                "file_type": path.suffix.lstrip(".") or "unknown",
                "description": description,
                "modified_timestamp": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
                "size": str(stat.st_size),
                "category": category,
                "safe_to_cite_use": str(safe_to_cite),
            }
        )
    return rows


def write_manifest() -> None:
    rows = build_manifest()
    csv_path = OUTPUT_ROOT / "output_manifest.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)
    summary = ["# Output Manifest", "", f"Files indexed: {len(rows):,}", ""]
    by_mode: dict[str, int] = {}
    for row in rows:
        by_mode[row["phase_mode"]] = by_mode.get(row["phase_mode"], 0) + 1
    summary.extend(f"- {mode}: {count:,}" for mode, count in sorted(by_mode.items()))
    (OUTPUT_ROOT / "output_manifest.md").write_text("\n".join(summary) + "\n", encoding="utf-8")


if __name__ == "__main__":
    write_manifest()
