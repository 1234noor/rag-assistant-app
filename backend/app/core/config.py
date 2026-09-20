from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    vector_store_path: str = "data/vector_store"
    collection_name: str = "ai_study_docs"
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: str = "llama3.2:1b"
    cors_origins: str = "http://localhost:8501"

    class Config:
        env_file = ".env"


settings = Settings()