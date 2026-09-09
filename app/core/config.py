from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Reef AI"
    ENVIRONMENT: str = "development"

    GHL_ENABLED: bool = False
    GHL_HOST: str = "192.168.1.120"
    GHL_PORT: int = 10001

    DATABASE_URL: str = "sqlite:///reefai.db"


settings = Settings()
