from sqlalchemy import inspect, text
import pytest


@pytest.mark.integration
def test_schema_initialization(schema_connection):
    # Check that the schema and table exist
    inspector = inspect(schema_connection)

    assert "raw" in inspector.get_schema_names()
    assert "decp_record" in inspector.get_table_names(schema="raw")

    # Retrieve table column definitions
    result = schema_connection.execute(
        text("""
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default,
                is_identity,
                identity_generation
            FROM information_schema.columns
            WHERE table_schema = 'raw'
              AND table_name = 'decp_record'
        """)
    )

    columns = {row["column_name"]: row for row in result.mappings()}

    # Check some important columns
    expected_columns = {
        "record_id",
        "source_file",
        "ingested_at",
        "id",
        "nature",
        "objet",
        "code_cpv",
        "montant",
        "source",
    }

    assert expected_columns.issubset(columns.keys())

    # Check pk
    primary_key = inspector.get_pk_constraint(
        "decp_record",
        schema="raw",
    )

    assert primary_key["constrained_columns"] == ["record_id"]

    # Check definitions
    assert columns["record_id"]["data_type"] == "bigint"
    assert columns["record_id"]["is_identity"] == "YES"
    assert columns["record_id"]["identity_generation"] == "ALWAYS"

    # Check ingestion metadata
    assert columns["source_file"]["is_nullable"] == "NO"
    assert columns["ingested_at"]["is_nullable"] == "NO"
    assert columns["ingested_at"]["column_default"] is not None
