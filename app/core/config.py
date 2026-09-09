from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    APP_NAME: str = "Reef AI"

    # Databas
    DATABASE_URL: str = "sqlite:///./reefai.db"

    # ProfiLux 3
    GHL_ENABLED: bool = True

    GHL_HOST: str = "192.168.86.172"

    GHL_PORT: int = 80

    GHL_USERNAME: str = "admin"

    GHL_PASSWORD: str = ""

    GHL_TIMEOUT: int = 10

    # Reef AI
    AUTO_SYNC: bool = False

    AUTO_SYNC_INTERVAL: int = 300

    class Config:
        env_file = ".env"


settings = Settings()