from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

package_path = Path(__file__).parent.parent.parent
env_file = package_path / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DELTA_CONSUMER__", env_file=env_file, env_file_encoding="utf-8"
    )

    # Azure Service Bus
    conn_str: str
    subscription: str
    topic: str
    session_id: str

    # RDF Delta Server
    rdf_delta_url: str = "http://localhost:1066"
    rdf_delta_datasource: str = "ds"


settings = Settings()
