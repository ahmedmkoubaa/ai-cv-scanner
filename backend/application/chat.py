from application.query_intent import QueryIntent, detect_query_intent
from domain.models import ChatResult, DocumentChunk, SourceDocument
from domain.ports import LLMPort, VectorStorePort

SYSTEM_PROMPT = """You are a CV screening assistant for recruiters.
Answer ONLY using the CV excerpts provided in the user message.
If the excerpts do not contain enough information, say you cannot find that information in the available CVs.
Be concise, factual, and mention candidate names when relevant.
Do not invent qualifications, experience, or contact details."""


class ChatUseCase:
    def __init__(
        self,
        llm: LLMPort,
        vector_store: VectorStorePort,
        *,
        retrieval_top_k: int,
    ) -> None:
        self._llm = llm
        self._vector_store = vector_store
        self._retrieval_top_k = retrieval_top_k

    def execute(self, query: str) -> ChatResult:
        trimmed = query.strip()
        if not trimmed:
            return ChatResult(
                response="Please provide a question about the candidates.",
                source_documents=[],
            )

        intent = detect_query_intent(trimmed)
        if intent in (QueryIntent.INVENTORY_COUNT, QueryIntent.INVENTORY_LIST):
            return self._handle_inventory_query(intent)

        return self._handle_semantic_query(trimmed)

    def _handle_inventory_query(self, intent: QueryIntent) -> ChatResult:
        sources = self._vector_store.list_indexed_sources()
        if not sources:
            return ChatResult(
                response=(
                    "No CV data is available yet. Please ensure PDFs have been "
                    "ingested into the system."
                ),
                source_documents=[],
            )

        total = len(sources)
        if intent is QueryIntent.INVENTORY_LIST:
            names = [source.candidate_name for source in sources]
            names_text = "\n".join(f"- {name}" for name in names)
            response = (
                f"There are {total} indexed candidate CVs in the system:\n\n"
                f"{names_text}"
            )
        else:
            label = "CV" if total == 1 else "CVs"
            response = (
                f"There are currently {total} candidate {label} fully indexed "
                "in the system."
            )

        return ChatResult(response=response, source_documents=sources)

    def _handle_semantic_query(self, query: str) -> ChatResult:
        chunks = self._vector_store.query(query, self._retrieval_top_k)
        if not chunks:
            return ChatResult(
                response=(
                    "No CV data is available yet. Please ensure PDFs have been "
                    "ingested into the system."
                ),
                source_documents=[],
            )

        prompt = self._build_prompt(query, chunks)
        response = self._llm.generate(prompt, system=SYSTEM_PROMPT)
        source_documents = self._collect_sources(chunks)

        return ChatResult(
            response=response.strip(),
            source_documents=source_documents,
        )

    @staticmethod
    def _build_prompt(query: str, chunks: list[DocumentChunk]) -> str:
        context_blocks = []
        for chunk in chunks:
            context_blocks.append(
                "\n".join(
                    [
                        f"[CV: {chunk.candidate_name} | File: {chunk.source_file}]",
                        chunk.text,
                    ]
                )
            )

        context = "\n\n---\n\n".join(context_blocks)
        return (
            "Use ONLY the following CV excerpts to answer the question.\n\n"
            f"{context}\n\n"
            f"Question: {query}"
        )

    @staticmethod
    def _collect_sources(chunks: list[DocumentChunk]) -> list[SourceDocument]:
        seen: set[str] = set()
        sources: list[SourceDocument] = []
        for chunk in chunks:
            if chunk.source_file in seen:
                continue
            seen.add(chunk.source_file)
            sources.append(
                SourceDocument(
                    file_name=chunk.source_file,
                    candidate_name=chunk.candidate_name,
                )
            )
        return sources
