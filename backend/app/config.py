from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    database_url: str | None = None
    db_host: str = "localhost"
    db_name: str = "lastbite"
    db_user: str = "lastbite"
    db_password: str = "lastbite-local-only"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def connection_url(self):
        return self.database_url or URL.create("postgresql+psycopg", username=self.db_user,
            password=self.db_password, host=self.db_host, port=5432, database=self.db_name)


settings = Settings()
