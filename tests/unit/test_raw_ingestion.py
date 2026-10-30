import pandas as pd
import pytest
from sqlalchemy import text
from decp_sql.ingestion.raw_ingestion import RawIngester


@pytest.mark.unit
def test_raw_ingester_rejects_invalid_mapping():
    data = pd.DataFrame(
        {
            "fooBar": ["value"],
            "foo_bar": ["value"],
        }
    )

    ingester = RawIngester(
        data=data,
        engine=None,
        source_file="test.csv",
    )

    with pytest.raises(ValueError, match="Invalid column mapping"):
        ingester()


@pytest.mark.unit
def test_raw_ingestion_inserts_records(schema_connection):
    data = pd.DataFrame(
        {
            "id": ["market_001", "market_002"],
            "nature": ["Marché", "Marché"],
            "montant": ["15000", "25000"],
        }
    )

    ingester = RawIngester(
        data=data,
        engine=schema_connection,
        source_file="test_decp.csv",
    )

    ingester()

    result = schema_connection.execute(
        text("""
            SELECT
                id,
                nature,
                montant,
                source_file,
                ingested_at
            FROM raw.decp_record
            ORDER BY id
        """)
    )

    records = result.mappings().all()

    assert len(records) == 2

    assert records[0]["id"] == "market_001"
    assert records[0]["nature"] == "Marché"
    assert records[0]["montant"] == "15000"

    assert records[1]["id"] == "market_002"
    assert records[1]["montant"] == "25000"

    for record in records:
        assert record["source_file"] == "test_decp.csv"
        assert record["ingested_at"] is not None


@pytest.mark.unit
def test_invalid_mapping_leaves_db_untouched(schema_connection):
    data = pd.DataFrame(
        {
            "fooBar": ["value"],
            "foo_bar": ["value"],
        }
    )

    ingester = RawIngester(
        data=data,
        engine=schema_connection,
        source_file="invalid.csv",
    )

    with pytest.raises(ValueError, match="Invalid column mapping"):
        ingester()

    result = schema_connection.execute(text("SELECT COUNT(*) FROM raw.decp_record"))

    assert result.scalar_one() == 0
