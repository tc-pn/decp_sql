from pathlib import Path

import pytest

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
            # Undo all changes, including the DROP SCHEMA, to keep the testing database clean
            transaction.rollback()


@pytest.fixture
def source_csv(tmp_path):
    csv_file = tmp_path / "test_decp.csv"
    csv_file.write_text(
        "id;nature;montant\nmarket_001;Marché;15000\nmarket_002;Marché;25000\n",
        encoding="utf-8",
    )
    return csv_file


@pytest.fixture
def initialized_schema(db_engine):
    schema_path = Path(__file__).resolve().parents[1] / "sql/001_create_raw_schema.sql"
    schema_sql = schema_path.read_text(encoding="utf-8")

    with db_engine.begin() as connection:
        connection.exec_driver_sql("DROP SCHEMA IF EXISTS raw CASCADE")

        for statement in schema_sql.split(";"):
            if statement.strip():
                connection.exec_driver_sql(statement)

    yield

    with db_engine.begin() as connection:
        connection.exec_driver_sql("DROP SCHEMA IF EXISTS raw CASCADE")
