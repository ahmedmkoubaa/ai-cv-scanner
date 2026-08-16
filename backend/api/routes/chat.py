from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_chat_use_case
from api.schemas import ChatRequest, ChatResponse, SourceDocumentSchema
from application.chat import ChatUseCase

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    chat_use_case: ChatUseCase = Depends(get_chat_use_case),
) -> ChatResponse:
    try:
        result = chat_use_case.execute(request.message)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ChatResponse(
        response=result.response,
        source_documents=[
            SourceDocumentSchema(
                file_name=source.file_name,
                candidate_name=source.candidate_name,
            )
            for source in result.source_documents
        ],
    )
