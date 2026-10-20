import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def get_required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"Error: {name} must be set")
    return value


@dataclass
class Settings:
    sql_connection_string: str
    sql_table: str


settings = Settings(
    sql_connection_string=os.environ.get("SqlConnectionString", ""),
    sql_table=get_required_env("SQL_TABLE"),
)
