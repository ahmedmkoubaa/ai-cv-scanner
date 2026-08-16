import unittest
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from api.dependencies import get_chat_use_case, get_ingest_use_case
from application.chat import ChatUseCase
from domain.models import DocumentChunk, IngestResult, SourceDocument
from main import app


class FakeLLM:
    def generate(self, prompt: str, *, system: str | None = None) -> str:
        return "Maya Lin has extensive React experience."


class FakeVectorStore:
    def __init__(self) -> None:
        self.sources = [
            SourceDocument(file_name="maya_lin.pdf", candidate_name="Maya Lin"),
            SourceDocument(file_name="lars_lindqvist.pdf", candidate_name="Lars Lindqvist"),
        ]

    def list_indexed_files(self) -> set[str]:
        return {s.file_name for s in self.sources}

    def list_indexed_sources(self) -> list[SourceDocument]:
        return self.sources

    def add_chunks(self, chunks: list[DocumentChunk]) -> None:
        pass

    def query(self, query_text: str, top_k: int) -> list[DocumentChunk]:
        return [
            DocumentChunk(
                text="React developer",
                source_file="maya_lin.pdf",
                candidate_name="Maya Lin",
                chunk_index=0,
            )
        ]


class TestAPIRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        fake_ingest = MagicMock()
        fake_ingest.ingest_all.return_value = IngestResult(
            ingested_files=[], skipped_files=[], total_chunks=0
        )
        fake_chat_use_case = ChatUseCase(
            llm=FakeLLM(),
            vector_store=FakeVectorStore(),
            retrieval_top_k=3,
        )

        app.dependency_overrides[get_ingest_use_case] = lambda: fake_ingest
        app.dependency_overrides[get_chat_use_case] = lambda: fake_chat_use_case
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls) -> None:
        app.dependency_overrides.clear()

    def test_health_check_returns_ok(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_chat_inventory_count_query(self) -> None:
        response = self.client.post(
            "/api/chat",
            json={"message": "How many candidates do we have?"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("2 candidate CVs", data["response"])
        self.assertEqual(len(data["source_documents"]), 2)
        self.assertEqual(data["source_documents"][0]["candidate_name"], "Maya Lin")
        self.assertEqual(data["source_documents"][1]["candidate_name"], "Lars Lindqvist")

    def test_chat_inventory_list_query(self) -> None:
        response = self.client.post(
            "/api/chat",
            json={"message": "List all candidates"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("Maya Lin", data["response"])
        self.assertIn("Lars Lindqvist", data["response"])
        self.assertEqual(len(data["source_documents"]), 2)

    def test_chat_validation_error_empty_message(self) -> None:
        response = self.client.post(
            "/api/chat",
            json={"message": ""},
        )
        self.assertEqual(response.status_code, 422)

    def test_chat_validation_error_missing_message_field(self) -> None:
        response = self.client.post(
            "/api/chat",
            json={},
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
