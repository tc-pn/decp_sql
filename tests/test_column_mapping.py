"""
This module contains unit tests for the raw ingestion pipeline
The test philosophy is a mix between precise cases tests and property verification using the Hypothesis package
"""

from hypothesis import given, strategies as st

from decp_sql.ingestion.raw_ingestion import to_snake, build_column_mapping


def test_to_snake():
    columns = ["updated_at", "titulaire_denominationSociale_3", "codeCPV"]
    transformed_columns = {column: to_snake(column) for column in columns}
    assert transformed_columns["codeCPV"] == "code_cpv"
    assert transformed_columns["updated_at"] == "updated_at"
    assert (
        transformed_columns["titulaire_denominationSociale_3"]
        == "titulaire_denomination_sociale_3"
    )


@given(st.from_regex(r"[a-z][a-z0-9_]*", fullmatch=True))
def test_to_snake_is_idempotent(column):
    assert to_snake(column) == column


@given(
    st.lists(st.from_regex(r"[a-z][a-z0-9_]*", fullmatch=True), min_size=1, unique=True)
)
def test_column_mapping_is_idempotent(columns: list[str]):
    mapping = build_column_mapping(columns)
    values = [val for val in mapping.values()]
    assert set(mapping) == set(build_column_mapping(values))
