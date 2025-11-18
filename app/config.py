from pydantic import BaseSettings

class Settings(BaseSettings):
    #swap for PostgreSQL in the future
    DATABASE_URL = "sqlite:///./len_dev.db"
    ENV = "development"
    class Config:
        env_file = ".env"
settings = Settings()