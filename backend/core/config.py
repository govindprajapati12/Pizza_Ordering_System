from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    # JWT Configuration
    JWT_SECRET_KEY: str = "your-very-secure-random-string"  # Default secret key, can be overridden via .env
    JWT_ALGORITHM: str = "HS256"  # Default algorithm
    JWT_TYPE: str = "Bearer"  # Token type (Bearer)
    JWT_EXPIRE_MINUTES: int = 60  # Default expiration time in minutes for the access token
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # Expiration for access token
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60  # Expiration for refresh token

    # Database Configuration (Add if necessary)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")  # Example for DB URL
    
    # Add any other necessary configurations here
    
    class Config:
        env_file = ".env"  # This will load environment variables from a .env file

# Instantiate the settings
settings = Settings()
