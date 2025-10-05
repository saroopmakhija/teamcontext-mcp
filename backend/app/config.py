from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "teamcontext"
    api_key_secret: str = "hackathon-demo-key-2025"
    jwt_secret_key: str = "your-secret-key-change-this-in-production"
    environment: str = "development"

    snowflake_account: Optional[str] = ""
    snowflake_user: Optional[str] = ""
    snowflake_password: Optional[str] = ""
    snowflake_database: Optional[str] = ""
    snowflake_schema: Optional[str] = ""
    snowflake_role: Optional[str] = ""

    class Config:
        env_file = ".env"


settings = Settings()


