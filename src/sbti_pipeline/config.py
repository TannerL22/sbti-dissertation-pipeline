from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class LegacyConfig:
    raw: dict[str, Any]
    root: Path

    @property
    def panel_path(self) -> Path:
        return self.root / self.raw["canonical_panel_path"]

    @property
    def output_dir(self) -> Path:
        return self.root / self.raw["output_dir"]

    @property
    def benchmark_dir(self) -> Path:
        return self.root / self.raw["legacy_benchmark_dir"]

    @property
    def legacy_reproduction_benchmark_dir(self) -> Path:
        return self.root / self.raw.get(
            "legacy_reproduction_benchmark_dir", self.raw.get("legacy_benchmark_dir", "")
        )

    def output_subdir(self, name: str) -> Path:
        path = self.output_dir / name
        path.mkdir(parents=True, exist_ok=True)
        return path


def load_config(path: str | Path, root: str | Path | None = None) -> LegacyConfig:
    config_path = Path(path)
    project_root = Path(root) if root is not None else Path.cwd()
    with config_path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    return LegacyConfig(raw=raw, root=project_root)
