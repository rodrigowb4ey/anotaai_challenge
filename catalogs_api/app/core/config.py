from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    PROJECT_NAME: str = 'Catalogs API'
    API_V1_STR: str = 'http://localhost:8000/api/v1'
    SECRET_KEY: str = 'your-secret-key-here'  # noqa: S105
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MONGODB_URL: str = 'mongodb://catalogs_db:27017'
    DATABASE_NAME: str = 'catalogs_db'


settings = Settings()
