from __future__ import annotations

import argparse

from src.sbti_pipeline.config import load_config
from src.sbti_pipeline.current_overlay_pipeline import run_current_overlay


def main() -> None:
    parser = argparse.ArgumentParser(description="Build current SBTi metadata overlay.")
    parser.add_argument("--config", default="configs/current_sbti_overlay.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    outputs = run_current_overlay(config)
    for name, path in outputs.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
