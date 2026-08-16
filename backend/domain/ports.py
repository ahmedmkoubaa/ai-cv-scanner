from typing import Protocol

from domain.models import DocumentChunk


class LLMPort(Protocol):
    def generate(self, prompt: str, *, system: str | None = None) -> str:
        """Generate text from the LLM given a user prompt and optional system instruction."""
        ...


class PDFParserPort(Protocol):
    def extract_text(self, file_path: str) -> str:
        """Extract plain text from a PDF file."""
        ...


class VectorStorePort(Protocol):
    def list_indexed_files(self) -> set[str]:
        """Return source file names already stored in the vector database."""
        ...

    def add_chunks(self, chunks: list[DocumentChunk]) -> None:
        """Persist document chunks with embeddings."""
        ...

    def query(self, query_text: str, top_k: int) -> list[DocumentChunk]:
        """Retrieve the most relevant chunks for a query."""
        ...
