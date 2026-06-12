from __future__ import annotations

import pandas as pd


def significance_stars(p_value: float) -> str:
    if p_value < 0.01:
        return "***"
    if p_value < 0.05:
        return "**"
    if p_value < 0.1:
        return "*"
    return ""


def format_coef(value: float, p_value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}{significance_stars(p_value)}"


def registry_to_csv(rows: list[dict], path) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df
