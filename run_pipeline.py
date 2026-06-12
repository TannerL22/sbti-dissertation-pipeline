from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


COMMANDS: dict[str, list[str]] = {
    "legacy": [sys.executable, "run_legacy_reproduction.py"],
    "refactored-legacy": [sys.executable, "run_refactored_legacy.py", "--config", "configs/legacy_2012_2024.yaml"],
    "refactored-clean": [sys.executable, "run_refactored_clean.py", "--config", "configs/refactored_clean_2012_2024.yaml"],
    "current-overlay": [sys.executable, "run_current_sbti_overlay.py", "--config", "configs/current_sbti_overlay.yaml"],
    "methodology-robustness": [sys.executable, "run_methodology_robustness.py", "--config", "configs/methodology_robustness.yaml"],
    "methodology-robustness-4b": [sys.executable, "run_methodology_robustness_4b.py", "--config", "configs/methodology_robustness_4b.yaml"],
    "final-synthesis": [sys.executable, "validate_project.py"],
    "manifest": [sys.executable, "build_output_manifest.py"],
    "test": [sys.executable, "-m", "pytest", "tests"],
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run dissertation pipeline modes.")
    parser.add_argument("mode", choices=sorted(COMMANDS))
    parser.add_argument("--dry-run", action="store_true", help="Print the command without executing it.")
    args = parser.parse_args()

    command = COMMANDS[args.mode]
    print(" ".join(command))
    if args.dry_run:
        return 0
    return subprocess.call(command, cwd=Path(__file__).resolve().parent)


if __name__ == "__main__":
    raise SystemExit(main())
