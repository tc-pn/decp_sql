import pandas as pd
from datetime import datetime, timezone
from sqlalchemy import Engine
import re

from decp_sql.validation.column_mapping_validator import ColumnMappingValidator

# some column names from source are a bit awkward
EXPLICIT_COLUMN_MAPPING = {
    "acheteur.id": "acheteur_id",
    "lieuExecution.code": "lieu_execution_code",
    "lieuExecution.typeCode": "lieu_execution_type_code",
    "dateNotificationModificationModification": "date_notification_donnees_modification",
    "datePublicationDonneesModificationModification": "date_publication_donnees_modification",
    "dureeMoisModificationActeSousTraitanceModificationActeSousTraitance": "duree_mois_modification_acte_sous_traitance",
}


class RawIngester:
    """Ingest raw DECP records into the PostgreSQL raw schema."""

    def __init__(self, data: pd.DataFrame, engine: Engine, source_file: str) -> None:
        """Initialize the raw ingester.

        Args:
            data: DataFrame containing the records to ingest.
            engine: SQLAlchemy engine used to connect to PostgreSQL.
            source_file: Name or path of the source file being ingested.
        """
        self.data = data.copy()
        self.engine = engine
        self.source_file = source_file

    def __call__(self):
        """Validate, transform, and insert records into the raw table."""
        mapping = build_column_mapping(list(self.data.columns))

        validator = ColumnMappingValidator(mapping)
        if not validator():
            raise ValueError(f"Invalid column mapping: {validator.errors}")

        self.data = self.data.rename(columns=mapping)

        self.data["source_file"] = self.source_file
        self.data["ingested_at"] = datetime.now(timezone.utc)
        self.data.to_sql(
            name="decp_record",
            schema="raw",
            con=self.engine,
            if_exists="append",
            index=False,
            chunksize=10_000,
            method="multi",
        )


def build_column_mapping(columns: list[str]) -> dict[str, str]:
    """Build the mapping from DECP source columns to SQL column names.

    Explicit mappings are used for DECP-specific column names that
    cannot be handled correctly by the generic snake_case conversion.

    Returns:
        A dictionary mapping source column names to database column
        names.
    """
    return {
        column: EXPLICIT_COLUMN_MAPPING.get(column, to_snake(column))
        for column in columns
    }


def to_snake(column: str) -> str:
    """Convert a camelCase column name to snake_case.

    Args:
        column: Column name to convert.

    Returns:
        The converted column name in snake_case.
    """
    column = re.sub(pattern=r"(.)([A-Z][a-z]+)", repl=r"\1_\2", string=column)
    column = re.sub(pattern=r"([a-z0-9])([A-Z])", repl=r"\1_\2", string=column)
    return column.lower()
