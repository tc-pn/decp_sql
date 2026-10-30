import hashlib
import pathlib
import re
from datetime import UTC, datetime

import pandas as pd
from sqlalchemy import Connection, Engine, text
from sqlalchemy.dialects.postgresql import insert

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


REGISTER_FILE = text("""
    INSERT INTO raw.ingestion_file (
        source_file,
        file_hash,
        ingested_at,
        record_count
    )
    VALUES (
        :source_file,
        :file_hash,
        :ingested_at,
        :record_count
    )
    ON CONFLICT (file_hash) DO NOTHING
    RETURNING file_id
""")


class RawIngester:
    """Ingest raw DECP records into the PostgreSQL raw schema."""

    def __init__(
        self,
        data: pd.DataFrame,
        engine: Engine | Connection,
        source_file: pathlib.Path,
    ) -> None:
        """Initialize the raw ingester.

        Args:
            data: DataFrame containing the records to ingest.
            engine: SQLAlchemy engine used to connect to PostgreSQL.
            source_file: Name or path of the source file being ingested.
        """
        self.data = data.copy()
        self.engine = engine
        self.source_file = source_file

    def __call__(self) -> bool:
        """Ingest new records only if the source file has not already been processed."""

        mapping = build_column_mapping(list(self.data.columns))

        validator = ColumnMappingValidator(mapping)
        if not validator():
            raise ValueError(f"Invalid column mapping: {validator.errors}")

        file_hash = calculate_file_hash(self.source_file)
        ingested_at = datetime.now(UTC)

        transformed_data = self.data.rename(columns=mapping)
        transformed_data["source_file"] = str(self.source_file)
        transformed_data["ingested_at"] = ingested_at

        parameters = {
            "source_file": str(self.source_file),
            "file_hash": file_hash,
            "ingested_at": ingested_at,
            "record_count": len(transformed_data),
        }

        if isinstance(self.engine, Engine):
            with self.engine.begin() as connection:
                return self._ingest(connection, transformed_data, parameters)

        if self.engine.in_transaction():
            return self._ingest(self.engine, transformed_data, parameters)

        with self.engine.begin():
            return self._ingest(self.engine, transformed_data, parameters)

    @staticmethod
    def _ingest(
        connection: Connection,
        data: pd.DataFrame,
        parameters: dict,
    ) -> bool:
        """Practical ingestion of the raw csv file."""

        result = connection.execute(REGISTER_FILE, parameters)
        file_id = result.scalar_one_or_none()

        if file_id is None:
            return False

        data.to_sql(
            name="decp_record",
            schema="raw",
            con=connection,
            if_exists="append",
            index=False,
            chunksize=1_000,
            method="multi",
        )

        return True


def calculate_file_hash(path: pathlib.Path) -> str:
    """
    Calculate the hash for a raw csv file that will be ingested.
    iter is used to read file by chunks to not load the enteire file ine memory a second time."""
    sha256 = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


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
