from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_NAME: str
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int

    model_config = {
        "env_file": Path(__file__).resolve().parent.parent / '.env',
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


settings = Settings()
DB_URL = (f"asyncpg://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@"
          f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")

TORTOISE_ORM = {
    'connections': {
        'default': DB_URL
    },
    "apps": {
        "models": {
            "models": ["database.models"],
            "default_connection": "default",
            "default": True
        },
    },
}