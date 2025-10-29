from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    polymarket_api_base_url: str = "https://gamma-api.polymarket.com"
    
    database_url: str = "postgresql://ranjanshahajishitole@localhost:5432/polymarket_db"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
