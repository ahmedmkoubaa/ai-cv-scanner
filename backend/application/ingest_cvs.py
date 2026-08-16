import logging
import re
from pathlib import Path

from domain.models import DocumentChunk, IngestResult
from domain.ports import PDFParserPort, VectorStorePort

logger = logging.getLogger(__name__)


class IngestCVsUseCase:
    def __init__(
        self,
        pdf_parser: PDFParserPort,
        vector_store: VectorStorePort,
        *,
        data_dir: Path,
        chunk_size: int,
        chunk_overlap: int,
    ) -> None:
        self._pdf_parser = pdf_parser
        self._vector_store = vector_store
        self._data_dir = data_dir
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def ingest_all(self) -> IngestResult:
        pdf_files = sorted(self._data_dir.glob("*.pdf"))
        if not pdf_files:
            logger.warning("No PDF files found in %s", self._data_dir)
            return IngestResult()

        indexed_files = self._vector_store.list_indexed_files()
        ingested_files: list[str] = []
        skipped_files: list[str] = []
        total_chunks = 0

        for pdf_path in pdf_files:
            file_name = pdf_path.name
            if file_name in indexed_files:
                logger.info("Skipping already indexed file: %s", file_name)
                skipped_files.append(file_name)
                continue

            logger.info("Ingesting %s", file_name)
            text = self._pdf_parser.extract_text(str(pdf_path))
            if not text.strip():
                logger.warning("No text extracted from %s — skipping", file_name)
                skipped_files.append(file_name)
                continue

            candidate_name = self._extract_candidate_name(text, file_name)
            chunks = self._chunk_text(
                text=text,
                source_file=file_name,
                candidate_name=candidate_name,
            )
            self._vector_store.add_chunks(chunks)
            ingested_files.append(file_name)
            total_chunks += len(chunks)
            logger.info("Indexed %d chunks from %s", len(chunks), file_name)

        return IngestResult(
            ingested_files=ingested_files,
            skipped_files=skipped_files,
            total_chunks=total_chunks,
        )

    def _chunk_text(
        self,
        *,
        text: str,
        source_file: str,
        candidate_name: str,
    ) -> list[DocumentChunk]:
        normalized = re.sub(r"\s+", " ", text).strip()
        if not normalized:
            return []

        chunks: list[DocumentChunk] = []
        start = 0
        chunk_index = 0
        step = max(1, self._chunk_size - self._chunk_overlap)

        while start < len(normalized):
            end = min(start + self._chunk_size, len(normalized))
            chunk_text = normalized[start:end].strip()
            if chunk_text:
                chunks.append(
                    DocumentChunk(
                        text=chunk_text,
                        source_file=source_file,
                        candidate_name=candidate_name,
                        chunk_index=chunk_index,
                    )
                )
                chunk_index += 1
            if end >= len(normalized):
                break
            start += step

        return chunks

    @staticmethod
    def _extract_candidate_name(text: str, file_name: str) -> str:
        first_line = text.strip().splitlines()[0].strip() if text.strip() else ""
        if first_line and len(first_line) <= 80 and not first_line.lower().startswith(
            "professional"
        ):
            return first_line

        stem = Path(file_name).stem
        return stem.replace("_", " ").title()
