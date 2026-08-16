import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from domain.models import DocumentChunk
from domain.ports import VectorStorePort

COLLECTION_NAME = "cv_documents"


class ChromaVectorStore:
    def __init__(self, persist_dir: str, embedding_model: str) -> None:
        self._client = chromadb.PersistentClient(path=persist_dir)
        self._embedding_fn = SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self._embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def list_indexed_files(self) -> set[str]:
        result = self._collection.get(include=["metadatas"])
        metadatas = result.get("metadatas") or []
        return {
            meta["source_file"]
            for meta in metadatas
            if meta and "source_file" in meta
        }

    def add_chunks(self, chunks: list[DocumentChunk]) -> None:
        if not chunks:
            return

        ids = [
            f"{chunk.source_file}::{chunk.chunk_index}" for chunk in chunks
        ]
        documents = [chunk.text for chunk in chunks]
        metadatas = [
            {
                "source_file": chunk.source_file,
                "candidate_name": chunk.candidate_name,
                "chunk_index": chunk.chunk_index,
            }
            for chunk in chunks
        ]

        self._collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

    def query(self, query_text: str, top_k: int) -> list[DocumentChunk]:
        if top_k <= 0:
            return []

        count = self._collection.count()
        if count == 0:
            return []

        result = self._collection.query(
            query_texts=[query_text],
            n_results=min(top_k, count),
            include=["documents", "metadatas", "distances"],
        )

        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]

        chunks: list[DocumentChunk] = []
        for text, meta in zip(documents, metadatas):
            if not text or not meta:
                continue
            chunks.append(
                DocumentChunk(
                    text=text,
                    source_file=meta["source_file"],
                    candidate_name=meta["candidate_name"],
                    chunk_index=int(meta["chunk_index"]),
                )
            )
        return chunks


def create_chroma_store(persist_dir: str, embedding_model: str) -> VectorStorePort:
    return ChromaVectorStore(
        persist_dir=persist_dir,
        embedding_model=embedding_model,
    )
