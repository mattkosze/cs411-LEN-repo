from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    #swap for PostgreSQL in the future
    DATABASE_URL : str = "sqlite:///./len_dev.db"
    ENV : str = "development"
    SECRET_KEY : str = "your-secret-key-change-in-production"  # Change this in production!
    ALGORITHM : str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES : int = 60 * 24 * 7  # 7 days
    
    # CORS configuration - comma-separated list of allowed origins
    CORS_ORIGINS : str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into a list of origins."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    class Config:
        env_file = ".env"
settings = Settings()