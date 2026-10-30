import pytest

from decp_sql.database.connection import DatabaseConnexion


@pytest.fixture(scope="session")
def db_engine():
    database_connexion = DatabaseConnexion()
    engine = database_connexion.engine

    yield engine

    engine.dispose()
