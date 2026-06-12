HISTORICAL_TREATMENT_COLUMNS = {
    "post_event",
    "earliest_near_term_validation_date",
    "s1s2_annual_reduction_rate",
    "has_s3_absolute_target",
    "s3_annual_reduction_rate",
}


def is_overlay_column(column):
    return column.startswith("current_") or column.startswith("overlay_") or column.endswith("_current")


def historical_treatment_uses_overlay_columns(mapping):
    violations = {}
    for treatment_col, input_cols in mapping.items():
        if treatment_col not in HISTORICAL_TREATMENT_COLUMNS:
            continue
        bad_inputs = [col for col in input_cols if is_overlay_column(col)]
        if bad_inputs:
            violations[treatment_col] = bad_inputs
    return violations


def test_current_sbti_overlay_variables_are_marked_as_current_metadata():
    overlay_columns = [
        "current_company_status",
        "current_near_term_target_status",
        "overlay_finance_sector_flag",
        "target_status_current",
    ]

    assert all(is_overlay_column(col) for col in overlay_columns)


def test_current_target_status_must_not_define_historical_treatment_variables():
    mapping = {
        "post_event": ["fyear", "earliest_near_term_validation_date"],
        "earliest_near_term_validation_date": ["target_validation_date"],
        "has_s3_absolute_target": ["scope", "type", "current_target_status"],
    }

    violations = historical_treatment_uses_overlay_columns(mapping)

    assert violations == {"has_s3_absolute_target": ["current_target_status"]}


def test_non_overlay_historical_inputs_do_not_trigger_lookahead_violation():
    mapping = {
        "post_event": ["fyear", "target_validation_date"],
        "s1s2_annual_reduction_rate": ["base_year", "target_year", "absolute_reduction_percent"],
    }

    assert historical_treatment_uses_overlay_columns(mapping) == {}
