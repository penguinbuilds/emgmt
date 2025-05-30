from pydantic_settings import BaseSettings
from functools import cached_property
from dotenv import load_dotenv

load_dotenv(".env")  # explicitly load .env early


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    @cached_property
    def DATABASE_URL(self):
        return (
            # f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            # f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"


settings = Settings()
