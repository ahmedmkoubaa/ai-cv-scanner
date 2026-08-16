import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    llm_provider: str
    gemini_api_key: str
    gemini_model: str
    openrouter_api_key: str
    openrouter_model: str
    data_dir: Path
    chroma_dir: Path
    embedding_model: str
    chunk_size: int
    chunk_overlap: int
    retrieval_top_k: int
    cors_origins: list[str]

    @classmethod
    def from_env(cls) -> "Settings":
        cors_raw = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:5173",
        )
        return cls(
            llm_provider=os.getenv("LLM_PROVIDER", "gemini").lower(),
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
            openrouter_model=os.getenv(
                "OPENROUTER_MODEL", "google/gemini-2.0-flash-001"
            ),
            data_dir=Path(os.getenv("DATA_DIR", "../data")),
            chroma_dir=Path(os.getenv("CHROMA_DIR", "./chroma_data")),
            embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            chunk_size=int(os.getenv("CHUNK_SIZE", "800")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "100")),
            retrieval_top_k=int(os.getenv("RETRIEVAL_TOP_K", "5")),
            cors_origins=[origin.strip() for origin in cors_raw.split(",") if origin.strip()],
        )

    def resolve_data_dir(self, base_dir: Path) -> Path:
        path = self.data_dir
        if not path.is_absolute():
            path = (base_dir / path).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path

    def resolve_chroma_dir(self, base_dir: Path) -> Path:
        path = self.chroma_dir
        if not path.is_absolute():
            path = (base_dir / path).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path


settings = Settings.from_env()
