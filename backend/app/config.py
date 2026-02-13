from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    REDIS_URL: str = "redis://redis:6379/0"
    DOWNLOADS_DIR: str = "/app/downloads"
    MAX_CONCURRENT_DOWNLOADS: int = 3
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:3001",
    ]

    class Config:
        env_file = ".env"


settings = Settings()
