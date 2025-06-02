from pydantic_settings import BaseSettings
from functools import cached_property
from dotenv import load_dotenv

load_dotenv(".env")  # explicitly load .env early


class Settings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    @cached_property
    def DATABASE_URL(self):
        return (
            # f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            # f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            # f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"


settings = Settings()
