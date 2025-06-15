from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    DB_CONNECTION_STRING: str = Field(alias="DB_CONNECTION_STRING", min_length=1)
    GEMINI_API_KEY: str = Field(alias="GEMINI_API_KEY", min_length=1)
    GEMINI_API_MODEL: str = Field(alias="GEMINI_API_MODEL", min_length=1)

    model_config = SettingsConfigDict(env_file=".env")


settings = AppSettings.model_validate({})
