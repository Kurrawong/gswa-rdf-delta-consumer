import os
import sys

from pydantic_settings import BaseSettings, SettingsConfigDict

from db_trigger.env import env_file

def get_odbc_conn_str(conn_str: str) -> str:
    # connection string must be given
    if conn_str is None:
        raise ValueError("Error: SqlConnectionString must be set")

    # add the odbc driver parameter, required for pyodbc but not
    # for the function app trigger.
    # the odbc driver version is different depending on the function app runtime
    # so we need to make a smart selection
    py_version = str(sys.version_info.major) + "." + str(sys.version_info.minor)
    if py_version == "3.10":
        odbc_driver_string = "Driver={ODBC Driver 17 for SQL Server}"
    elif py_version == "3.11":
        odbc_driver_string = "Driver={ODBC Driver 18 for SQL Server}"
    elif py_version == "3.12":
        odbc_driver_string = "Driver={ODBC Driver 18 for SQL Server}"
    else:
        raise Exception(f"odbc driver selection not implemented for python {py_version}")

    # remove the Authentication parameter from the connection string
    # it is required for the function app trigger but not the pyodbc
    # connection string.
    sql_connection_string_parts = conn_str.split(";") + [odbc_driver_string]
    for i, part in enumerate(sql_connection_string_parts):
        if part.startswith("Authentication"):
            sql_connection_string_parts.pop(i)

    return ";".join(sql_connection_string_parts)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file, env_file_encoding="utf-8", extra="allow"
    )

    service_bus: str = ""
    service_bus_topic: str = ""
    service_bus_session_id: str = ""
    use_amqp_over_ws: bool = True
    sql_connection_string_odbc: str = get_odbc_conn_str(os.environ.get("SqlConnectionString"))


settings = Settings()
