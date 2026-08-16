import unittest

from application.chat import ChatUseCase
from domain.models import DocumentChunk, SourceDocument


class FakeLLM:
    def __init__(self) -> None:
        self.generate_called = False

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        self.generate_called = True
        return "Semantic answer from LLM."


class FakeVectorStore:
    def __init__(self) -> None:
        self.query_called = False
        self.sources = [
            SourceDocument(file_name="jane_doe.pdf", candidate_name="Jane Doe"),
            SourceDocument(file_name="john_smith.pdf", candidate_name="John Smith"),
            SourceDocument(file_name="amina_diallo.pdf", candidate_name="Amina Diallo"),
        ]
        self.chunks = [
            DocumentChunk(
                text="Python and React experience.",
                source_file="jane_doe.pdf",
                candidate_name="Jane Doe",
                chunk_index=0,
            )
        ]

    def list_indexed_files(self) -> set[str]:
        return {source.file_name for source in self.sources}

    def list_indexed_sources(self) -> list[SourceDocument]:
        return list(self.sources)

    def add_chunks(self, chunks: list[DocumentChunk]) -> None:
        return None

    def query(self, query_text: str, top_k: int) -> list[DocumentChunk]:
        self.query_called = True
        return self.chunks[:top_k]


class ChatRoutingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.llm = FakeLLM()
        self.vector_store = FakeVectorStore()
        self.use_case = ChatUseCase(
            llm=self.llm,
            vector_store=self.vector_store,
            retrieval_top_k=5,
        )

    def test_count_query_uses_metadata_not_vector_search(self) -> None:
        result = self.use_case.execute("How many candidates do we have?")

        self.assertFalse(self.vector_store.query_called)
        self.assertFalse(self.llm.generate_called)
        self.assertIn("3 candidate CVs", result.response)
        self.assertEqual(len(result.source_documents), 3)

    def test_list_query_returns_all_candidate_names(self) -> None:
        result = self.use_case.execute("List all candidate names")

        self.assertFalse(self.vector_store.query_called)
        self.assertFalse(self.llm.generate_called)
        self.assertIn("Jane Doe", result.response)
        self.assertIn("John Smith", result.response)
        self.assertIn("Amina Diallo", result.response)
        self.assertEqual(len(result.source_documents), 3)

    def test_semantic_query_uses_vector_search_and_llm(self) -> None:
        result = self.use_case.execute("Who has React experience?")

        self.assertTrue(self.vector_store.query_called)
        self.assertTrue(self.llm.generate_called)
        self.assertEqual(result.response, "Semantic answer from LLM.")
        self.assertEqual(len(result.source_documents), 1)


if __name__ == "__main__":
    unittest.main()
