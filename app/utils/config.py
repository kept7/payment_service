from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_USER_NAME: str
    DB_USER_PASS: str
    DB_HOST: str
    DB_NAME: str
    BASE_URL_1: str
    BASE_URL_2: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    SU: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
