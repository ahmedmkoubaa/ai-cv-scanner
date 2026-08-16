from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    text: str
    source_file: str
    candidate_name: str
    chunk_index: int


class SourceDocument(BaseModel):
    file_name: str
    candidate_name: str


class ChatResult(BaseModel):
    response: str
    source_documents: list[SourceDocument] = Field(default_factory=list)


class IngestResult(BaseModel):
    ingested_files: list[str] = Field(default_factory=list)
    skipped_files: list[str] = Field(default_factory=list)
    total_chunks: int = 0
