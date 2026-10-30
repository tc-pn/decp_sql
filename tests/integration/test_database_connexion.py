import pytest
from sqlalchemy import text


@pytest.mark.integration
def test_database_connexion(db_engine):
    with db_engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        assert result.scalar_one() == 1
