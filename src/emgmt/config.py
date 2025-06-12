from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import cached_property
from dotenv import load_dotenv

load_dotenv(".env")  # explicitly load .env early


class Settings(BaseSettings):
    # For DB
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    # JWT token related
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    # TIMEOUT: int

    ADMIN_PASSWORD: str

    # Celery and Redis related
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    @cached_property
    def DATABASE_URL(self):
        return (
            # f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            # f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            # f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # # class based config deprecated in Pydantic V2, will be removed in V3
    # class Config:
    #     env_file = ".env"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
