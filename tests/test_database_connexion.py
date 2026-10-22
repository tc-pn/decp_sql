from sqlalchemy import text
from decp_sql.database.connection import DatabaseConnexion


def test_database_connexion():
    database_connexion = DatabaseConnexion()
    engine = database_connexion.engine
    try:
        with database_connexion.engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            assert next(iter(result.one())) == 1
    finally:
        engine.dispose()
