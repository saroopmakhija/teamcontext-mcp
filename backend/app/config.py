from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "teamcontext"
    api_key_secret: str = "hackathon-demo-key-2025"
    environment: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()
