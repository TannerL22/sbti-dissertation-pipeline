from __future__ import annotations


def fixed_effect_controls(controls: str, firm_fe: str = "sbti_id", year_fe: str = "fyear") -> str:
    return f"{controls} + C({firm_fe}) + C({year_fe})"


def main_formula(dep_var: str, terms: str, controls: str) -> str:
    return f"{dep_var} ~ {terms} + {controls}"


def event_study_formula(dep_var: str, controls: str) -> str:
    terms = "pre3 + pre2 + post_event + post1 + post2 + post3plus"
    return f"{dep_var} ~ {terms} + {controls} + C(sbti_id) + C(fyear)"
