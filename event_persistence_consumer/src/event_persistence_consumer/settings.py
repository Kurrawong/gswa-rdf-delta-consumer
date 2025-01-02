from pydantic_settings import BaseSettings, SettingsConfigDict

from event_persistence_consumer.env import env_file


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="app__", env_file=env_file, env_file_encoding="utf-8", extra="allow"
    )

    mssql_database: str
    mssql_server: str = "localhost,1433"
    mssql_master_database: str = "master"
    mssql_username: str = "sa"
    mssql_password: str


settings = Settings()
