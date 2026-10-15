import os

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import URL

load_dotenv()


class DatabaseConnexion:
    def __init__(self) -> None:
        self._verify_required_keys()
        self.engine = self._get_engine()
        pass

    def _get_engine(self) -> Engine:
        url = URL.create(
            drivername="postgresql+psycopg",
            username=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
            port=int(os.environ["POSTGRES_PORT"]),
            database=os.environ["POSTGRES_DB"],
        )

        return create_engine(url, pool_pre_ping=True)

    def _verify_required_keys(self):
        required = [
            "POSTGRES_DB",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "POSTGRES_PORT",
        ]

        missing = [key for key in required if not os.getenv(key)]
        if missing:
            raise RuntimeError(f"Missing database configuration: {', '.join(missing)}")
