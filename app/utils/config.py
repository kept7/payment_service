from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_NAME: str
    BASE_URL_1: str
    BASE_URL_2: str


settings = Settings()