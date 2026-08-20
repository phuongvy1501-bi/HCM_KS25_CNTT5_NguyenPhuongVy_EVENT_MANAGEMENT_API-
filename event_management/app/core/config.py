from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # App
    APP_NAME: str = "Event Management API"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str

    # Security / JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Singleton settings object - import cái này ở mọi nơi cần config
settings = Settings()
