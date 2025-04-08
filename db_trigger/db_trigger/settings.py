import os
import sys

from pydantic_settings import BaseSettings, SettingsConfigDict

from db_trigger.env import env_file

py_version = str(sys.version_info.major) + "." + str(sys.version_info.minor)
if py_version == "3.10":
    odbc_driver_string = "Driver={ODBC Driver 17 for SQL Server};"
elif py_version == "3.11":
    odbc_driver_string = "Driver={ODBC Driver 18 for SQL Server};"
else:
    raise Exception(f"odbc driver selection not implemented for python {py_version}")

sql_connection_string = os.environ.get("SqlConnectionString")
if sql_connection_string is None:
    raise ValueError("Error: SqlConnectionString must be set")

sql_connection_string_odbc = odbc_driver_string + sql_connection_string


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file, env_file_encoding="utf-8", extra="allow"
    )

    service_bus: str = ""
    service_bus_topic: str = ""
    service_bus_session_id: str = ""
    use_amqp_over_ws: bool = True
    sql_connection_string_odbc: str = sql_connection_string_odbc


settings = Settings()
