from __future__ import annotations

import argparse
from pathlib import Path

from .clean_comparison import write_clean_comparison
from .clean_event_study import run as run_clean_event_study
from .clean_leverage import run as run_centered_leverage
from .config import load_config
from .io import ensure_output_dirs


def run_pipeline(config_path: str | Path = "configs/refactored_clean_2012_2024.yaml") -> dict:
    config = load_config(config_path)
    ensure_output_dirs(config)
    outputs = {}
    outputs.update(run_clean_event_study(config))
    outputs.update(run_centered_leverage(config))
    outputs["comparison_report"] = write_clean_comparison(config)
    return outputs


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/refactored_clean_2012_2024.yaml")
    args = parser.parse_args(argv)
    outputs = run_pipeline(args.config)
    for name, path in outputs.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
