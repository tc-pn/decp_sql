import pandas as pd
from datetime import datetime, timezone
from sqlalchemy import Engine
import re

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
    def __init__(self, data: pd.DataFrame, engine: Engine, source_file: str) -> None:
        self.data = data.copy()
        self.engine = engine
        self.source_file = source_file

    def __call__(self):
        self.data = self.data.rename(
            columns=build_column_mapping(list(self.data.columns))
        )
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
    return {
        column: EXPLICIT_COLUMN_MAPPING.get(column, to_snake(column))
        for column in columns
    }


def to_snake(column: str) -> str:
    column = re.sub(pattern=r"(.)([A-Z][a-z]+)", repl=r"\1_\2", string=column)
    column = re.sub(pattern=r"([a-z0-9])([A-Z])", repl=r"\1_\2", string=column)
    return column.lower()
