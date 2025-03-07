import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


@dataclass
class Settings:
    sql_connection_string: str


settings = Settings(sql_connection_string=os.environ.get("SqlConnectionString", ""))
