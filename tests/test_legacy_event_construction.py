import pandas as pd


def legacy_first_validated_near_term_target(targets):
    df = targets.copy()
    df["validation_date"] = pd.to_datetime(df["validation_date"], errors="coerce")
    eligible = df[
        (df["target_class"].str.lower() == "near-term")
        & (df["status"].str.lower() == "validated")
    ]
    return eligible.sort_values(["sbti_id", "validation_date"]).groupby("sbti_id").first()


def legacy_post_event(fyear, validation_date):
    validation_year = pd.Timestamp(validation_date).year
    return int(fyear >= validation_year)


def test_first_validated_near_term_target_selected_with_multiple_targets():
    targets = pd.DataFrame(
        [
            {"sbti_id": "A", "target_class": "near-term", "status": "validated", "validation_date": "2021-06-01"},
            {"sbti_id": "A", "target_class": "near-term", "status": "validated", "validation_date": "2023-01-01"},
            {"sbti_id": "A", "target_class": "net-zero", "status": "validated", "validation_date": "2020-01-01"},
        ]
    )

    events = legacy_first_validated_near_term_target(targets)

    assert events.loc["A", "validation_date"] == pd.Timestamp("2021-06-01")


def test_commitment_rows_are_not_validation_events():
    targets = pd.DataFrame(
        [
            {"sbti_id": "A", "target_class": "near-term", "status": "committed", "validation_date": None},
            {"sbti_id": "A", "target_class": "near-term", "status": "validated", "validation_date": "2022-04-15"},
        ]
    )

    events = legacy_first_validated_near_term_target(targets)

    assert events.loc["A", "status"] == "validated"
    assert events.loc["A", "validation_date"] == pd.Timestamp("2022-04-15")


def test_later_target_revisions_do_not_change_legacy_first_event():
    targets = pd.DataFrame(
        [
            {"sbti_id": "A", "target_class": "near-term", "status": "validated", "validation_date": "2020-03-01"},
            {"sbti_id": "A", "target_class": "near-term", "status": "validated", "validation_date": "2024-09-01"},
        ]
    )

    events = legacy_first_validated_near_term_target(targets)

    assert events.loc["A", "validation_date"] == pd.Timestamp("2020-03-01")


def test_commitment_only_firms_do_not_receive_validation_event():
    targets = pd.DataFrame(
        [
            {"sbti_id": "A", "target_class": "near-term", "status": "committed", "validation_date": None},
            {"sbti_id": "B", "target_class": "near-term", "status": "validated", "validation_date": "2021-01-01"},
        ]
    )

    events = legacy_first_validated_near_term_target(targets)

    assert "A" not in events.index
    assert "B" in events.index


def test_post_event_uses_fiscal_year_relative_to_validation_year():
    assert legacy_post_event(2020, "2021-06-30") == 0
    assert legacy_post_event(2021, "2021-06-30") == 1
    assert legacy_post_event(2022, "2021-06-30") == 1
