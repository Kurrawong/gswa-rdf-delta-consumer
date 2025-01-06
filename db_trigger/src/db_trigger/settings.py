from pydantic_settings import BaseSettings, SettingsConfigDict

from db_trigger.env import env_file


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="app__", env_file=env_file, env_file_encoding="utf-8", extra="allow"
    )

    service_bus: str
    topic_name: str
    session_id: str
    ws: bool = True


settings = Settings()
