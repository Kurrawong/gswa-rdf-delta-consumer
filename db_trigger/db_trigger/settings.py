import os
import sys

from pydantic_settings import BaseSettings, SettingsConfigDict

from db_trigger.env import env_file

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file, env_file_encoding="utf-8", extra="allow"
    )

    service_bus: str = ""
    service_bus_topic: str = ""
    service_bus_session_id: str = ""
    use_amqp_over_ws: bool = True
    sql_connection_string = os.environ.get("SqlConnectionString", "")


settings = Settings()
