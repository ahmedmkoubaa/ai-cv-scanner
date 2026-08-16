import unittest

from domain.models import ChatResult, DocumentChunk, IngestResult, SourceDocument


class TestDomainModels(unittest.TestCase):
    def test_document_chunk_properties(self) -> None:
        chunk = DocumentChunk(
            text="Experienced in Python and FastAPI.",
            source_file="john_doe.pdf",
            candidate_name="John Doe",
            chunk_index=0,
        )
        self.assertEqual(chunk.text, "Experienced in Python and FastAPI.")
        self.assertEqual(chunk.source_file, "john_doe.pdf")
        self.assertEqual(chunk.candidate_name, "John Doe")
        self.assertEqual(chunk.chunk_index, 0)

    def test_source_document_properties(self) -> None:
        source = SourceDocument(
            file_name="jane_smith.pdf",
            candidate_name="Jane Smith",
        )
        self.assertEqual(source.file_name, "jane_smith.pdf")
        self.assertEqual(source.candidate_name, "Jane Smith")

    def test_chat_result_defaults_and_custom(self) -> None:
        result_default = ChatResult(response="Hello world")
        self.assertEqual(result_default.response, "Hello world")
        self.assertEqual(result_default.source_documents, [])

        source = SourceDocument(file_name="a.pdf", candidate_name="Alice")
        result_custom = ChatResult(
            response="Found Alice",
            source_documents=[source],
        )
        self.assertEqual(len(result_custom.source_documents), 1)
        self.assertEqual(result_custom.source_documents[0].candidate_name, "Alice")

    def test_ingest_result_defaults_and_custom(self) -> None:
        ingest_default = IngestResult()
        self.assertEqual(ingest_default.ingested_files, [])
        self.assertEqual(ingest_default.skipped_files, [])
        self.assertEqual(ingest_default.total_chunks, 0)

        ingest_custom = IngestResult(
            ingested_files=["file1.pdf"],
            skipped_files=["file2.pdf"],
            total_chunks=5,
        )
        self.assertEqual(ingest_custom.ingested_files, ["file1.pdf"])
        self.assertEqual(ingest_custom.skipped_files, ["file2.pdf"])
        self.assertEqual(ingest_custom.total_chunks, 5)


if __name__ == "__main__":
    unittest.main()
