import pandas as pd
import pytest

from decp_sql.ingestion.raw_ingestion import RawIngester


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
