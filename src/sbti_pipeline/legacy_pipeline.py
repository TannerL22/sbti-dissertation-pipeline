from __future__ import annotations

import argparse
from pathlib import Path

from .comparison import write_comparison
from .config import load_config
from .diagnostics import panel_diagnostics
from .io import ensure_output_dirs, load_panel
from .legacy_event_study import run as run_event_study
from .legacy_main import run as run_main
from .legacy_predictive import run as run_predictive


def run_pipeline(config_path: str | Path = "configs/legacy_2012_2024.yaml") -> dict:
    config = load_config(config_path)
    ensure_output_dirs(config)
    outputs = {}
    panel = load_panel(config)
    diag = panel_diagnostics(panel)
    diagnostics_path = config.output_subdir("diagnostics") / "panel_diagnostics_refactored.csv"
    import pandas as pd

    pd.DataFrame([diag]).to_csv(diagnostics_path, index=False)
    outputs["panel_diagnostics"] = diagnostics_path
    outputs.update(run_main(config))
    outputs.update(run_event_study(config))
    outputs.update(run_predictive(config))
    outputs["comparison_report"] = write_comparison(config)
    return outputs


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/legacy_2012_2024.yaml")
    args = parser.parse_args(argv)
    outputs = run_pipeline(args.config)
    for name, path in outputs.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
