from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    #swap for PostgreSQL in the future
    DATABASE_URL : str = "sqlite:///./len_dev.db"
    ENV : str = "development"
    SECRET_KEY : str = "your-secret-key-change-in-production"  # Change this in production!
    ALGORITHM : str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES : int = 60 * 24 * 7  # 7 days
    class Config:
        env_file = ".env"
settings = Settings()