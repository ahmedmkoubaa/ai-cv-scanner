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
    output_dir: Path
    cv_count: int

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            llm_provider=os.getenv("LLM_PROVIDER", "gemini").lower(),
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
            openrouter_model=os.getenv(
                "OPENROUTER_MODEL", "google/gemini-2.0-flash-001"
            ),
            output_dir=Path(os.getenv("OUTPUT_DIR", "../data")),
            cv_count=int(os.getenv("CV_COUNT", "28")),
        )

    def resolve_output_dir(self, base_dir: Path) -> Path:
        path = self.output_dir
        if not path.is_absolute():
            path = (base_dir / path).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path


settings = Settings.from_env()
