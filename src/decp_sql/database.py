from os import getenv

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

load_dotenv()


def create_db_engine() -> Engine:
    user = getenv("POSTGRES_USER")
    password = getenv("POSTGRES_PASSWORD")
    database = getenv("POSTGRES_DB")
    port = getenv("POSTGRES_PORT", "5432")

    if not all((user, password, database)):
        raise RuntimeError(
            "Database configuration is incomplete. Check your .env file."
        )

    url = f"postgresql+psycopg://{user}:{password}@localhost:{port}/{database}"

    return create_engine(url)


def test_connection(engine: Engine) -> None:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print(result.scalar_one())
