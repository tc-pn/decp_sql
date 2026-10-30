from decp_sql.ingestion.csv_loader import CSVLoader
import pandas as pd
from pathlib import Path
import pytest
import tempfile
from hypothesis import given, strategies as st


@pytest.mark.unit
def test_csv_loader_preserves_empty_values_and_leading_zeros(tmp_path):
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(
        "code;name\n00123;Example\n;Empty code\n",
        encoding="utf-8",
    )

    result = CSVLoader(csv_file)()

    assert result["code"].tolist() == ["00123", ""]
    assert result["name"].tolist() == ["Example", "Empty code"]


@pytest.mark.unit
@given(
    codes=st.lists(
        st.text(
            alphabet="0123456789",
            min_size=0,
            max_size=12,
        ),
        min_size=1,
        max_size=20,
    )
)
def test_csv_loader_preserves_identifiers(codes):
    with tempfile.TemporaryDirectory() as tmp_dir:
        csv_file = Path(tmp_dir) / "sample.csv"

        pd.DataFrame({"code": codes}).to_csv(
            csv_file,
            sep=";",
            index=False,
        )

        result = CSVLoader(csv_file)()

        assert result["code"].tolist() == codes
