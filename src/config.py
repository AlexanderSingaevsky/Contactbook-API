from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    sqlalchemy_database_url: str = Field()
    secret_key: str = Field()
    algorithm: str = Field()
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
