from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_uri: str = "MONGODB_URI=mongodb+srv://saroopmakhija_db_user:saroop123@cluster0.l6woorw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    mongodb_db_name: str = "teamcontext"
    api_key_secret: str = "hackathon-demo-key-2025"
    jwt_secret_key: str = "your-secret-key-change-this-in-production"
    gemini_api_key: str = ""
    environment: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()
