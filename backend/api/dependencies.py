from functools import lru_cache
from pathlib import Path

from application.chat import ChatUseCase
from application.ingest_cvs import IngestCVsUseCase
from config import Settings, settings
from domain.ports import LLMPort
from infrastructure.llm.gemini_adapter import create_gemini_adapter
from infrastructure.llm.openrouter_adapter import create_openrouter_adapter
from infrastructure.pdf.pdf_parser import PyPDFParser
from infrastructure.vector_store.chroma_store import create_chroma_store

BASE_DIR = Path(__file__).resolve().parent.parent


@lru_cache
def get_settings() -> Settings:
    return settings


def create_llm_adapter(app_settings: Settings) -> LLMPort:
    provider = app_settings.llm_provider
    if provider == "gemini":
        return create_gemini_adapter(
            app_settings.gemini_api_key,
            app_settings.gemini_model,
        )
    if provider == "openrouter":
        return create_openrouter_adapter(
            app_settings.openrouter_api_key,
            app_settings.openrouter_model,
        )
    raise ValueError(
        f"Unsupported LLM_PROVIDER: {provider!r}. Use 'gemini' or 'openrouter'."
    )


@lru_cache
def get_vector_store():
    app_settings = get_settings()
    chroma_dir = app_settings.resolve_chroma_dir(BASE_DIR)
    return create_chroma_store(str(chroma_dir), app_settings.embedding_model)


@lru_cache
def get_pdf_parser() -> PyPDFParser:
    return PyPDFParser()


@lru_cache
def get_ingest_use_case() -> IngestCVsUseCase:
    app_settings = get_settings()
    data_dir = app_settings.resolve_data_dir(BASE_DIR)
    return IngestCVsUseCase(
        pdf_parser=get_pdf_parser(),
        vector_store=get_vector_store(),
        data_dir=data_dir,
        chunk_size=app_settings.chunk_size,
        chunk_overlap=app_settings.chunk_overlap,
    )


@lru_cache
def get_chat_use_case() -> ChatUseCase:
    app_settings = get_settings()
    return ChatUseCase(
        llm=create_llm_adapter(app_settings),
        vector_store=get_vector_store(),
        retrieval_top_k=app_settings.retrieval_top_k,
    )
