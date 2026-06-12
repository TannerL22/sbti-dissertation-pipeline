from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import LegacyConfig


def ensure_output_dirs(config: LegacyConfig) -> None:
    for name in ["tables", "figures", "diagnostics", "logs", "comparisons"]:
        config.output_subdir(name)


def load_panel(config: LegacyConfig) -> pd.DataFrame:
    return pd.read_parquet(config.panel_path)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
