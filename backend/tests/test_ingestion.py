import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from application.ingest_cvs import IngestCVsUseCase
from domain.models import DocumentChunk, SourceDocument


class FakeVectorStoreForIngestion:
    def __init__(self, indexed_files: set[str]) -> None:
        self.indexed_files = indexed_files
        self.added_chunks: list[DocumentChunk] = []

    def list_indexed_files(self) -> set[str]:
        return set(self.indexed_files)

    def list_indexed_sources(self) -> list[SourceDocument]:
        return [
            SourceDocument(file_name=f, candidate_name=f.replace(".pdf", ""))
            for f in self.indexed_files
        ]

    def add_chunks(self, chunks: list[DocumentChunk]) -> None:
        self.added_chunks.extend(chunks)

    def query(self, query_text: str, top_k: int) -> list[DocumentChunk]:
        return []


class TestIngestion(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temp_dir.name)

        (self.data_dir / "maya_lin.pdf").write_bytes(b"%PDF-fake-content-maya")
        (self.data_dir / "tariq_al_mansoor.pdf").write_bytes(b"%PDF-fake-content-tariq")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_duplicate_pdfs_are_skipped_on_re_ingestion(self) -> None:
        pdf_parser = MagicMock()
        pdf_parser.extract_text.return_value = (
            "Tariq Al-Mansoor\nSenior Software Engineer"
        )

        vector_store = FakeVectorStoreForIngestion(indexed_files={"maya_lin.pdf"})

        use_case = IngestCVsUseCase(
            pdf_parser=pdf_parser,
            vector_store=vector_store,
            data_dir=self.data_dir,
            chunk_size=500,
            chunk_overlap=50,
        )

        result = use_case.ingest_all()

        self.assertIn("maya_lin.pdf", result.skipped_files)
        self.assertIn("tariq_al_mansoor.pdf", result.ingested_files)
        self.assertEqual(len(result.skipped_files), 1)
        self.assertEqual(len(result.ingested_files), 1)
        self.assertGreater(result.total_chunks, 0)
        pdf_parser.extract_text.assert_called_once_with(
            str(self.data_dir / "tariq_al_mansoor.pdf")
        )

    def test_all_duplicates_skipped(self) -> None:
        pdf_parser = MagicMock()
        vector_store = FakeVectorStoreForIngestion(
            indexed_files={"maya_lin.pdf", "tariq_al_mansoor.pdf"}
        )

        use_case = IngestCVsUseCase(
            pdf_parser=pdf_parser,
            vector_store=vector_store,
            data_dir=self.data_dir,
            chunk_size=500,
            chunk_overlap=50,
        )

        result = use_case.ingest_all()

        self.assertEqual(len(result.ingested_files), 0)
        self.assertEqual(len(result.skipped_files), 2)
        self.assertEqual(result.total_chunks, 0)
        pdf_parser.extract_text.assert_not_called()


if __name__ == "__main__":
    unittest.main()
