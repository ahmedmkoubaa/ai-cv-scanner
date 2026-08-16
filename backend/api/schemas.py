from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User question about candidates")


class SourceDocumentSchema(BaseModel):
    file_name: str
    candidate_name: str


class ChatResponse(BaseModel):
    response: str
    source_documents: list[SourceDocumentSchema] = Field(default_factory=list)
