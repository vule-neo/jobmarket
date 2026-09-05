from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    adzuna_app_id: str
    adzuna_api_key: str
    apify_api_key: str
    database_url: str


settings = Settings()