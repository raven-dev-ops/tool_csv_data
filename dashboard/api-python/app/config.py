from pydantic import BaseSettings, AnyUrl


class Settings(BaseSettings):
    app_name: str = "MamboLite API"
    environment: str = "dev"

    database_url: str = "postgresql://user:pass@localhost:5432/mambolite"
    redis_url: str = "redis://localhost:6379/0"

    auth0_domain: str = ""
    auth0_client_id: str = ""
    auth0_client_secret: str = ""

    class Config:
        env_file = ".env"


settings = Settings()

