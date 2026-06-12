from __future__ import annotations

import argparse

from src.sbti_pipeline.config import load_config
from src.sbti_pipeline.methodology_robustness_4b import run_methodology_robustness_4b


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Phase 4B public/private and leverage robustness checks.")
    parser.add_argument("--config", default="configs/methodology_robustness_4b.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    outputs = run_methodology_robustness_4b(config)
    for name, path in outputs.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
