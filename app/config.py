from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    #swap for PostgreSQL in the future
    DATABASE_URL : str = "sqlite:///./len_dev.db"
    ENV : str = "development"
    class Config:
        env_file = ".env"
settings = Settings()