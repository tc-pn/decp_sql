import pytest
from pathlib import Path
from decp_sql.database.connection import DatabaseConnexion


@pytest.fixture(scope="session")
def db_engine():
    database_connexion = DatabaseConnexion()
    engine = database_connexion.engine

    yield engine

    engine.dispose()


@pytest.fixture
def schema_connection(db_engine):
    schema_path = Path(__file__).resolve().parents[1] / "sql/001_create_raw_schema.sql"

    with db_engine.connect() as connection:
        transaction = connection.begin()

        try:
            # initialize new clean schema
            connection.exec_driver_sql("DROP SCHEMA IF EXISTS raw CASCADE")

            # execute schema
            schema_sql = schema_path.read_text(encoding="utf-8")

            for statement in schema_sql.split(";"):
                if statement.strip():
                    connection.exec_driver_sql(statement)

            yield connection

        finally:
            # Undo all changes, including the DROP SCHEMA
            transaction.rollback()
