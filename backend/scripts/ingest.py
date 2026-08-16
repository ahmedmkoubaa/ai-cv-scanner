import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api.dependencies import get_ingest_use_case

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> int:
    logger.info("Running manual CV ingestion")
    result = get_ingest_use_case().ingest_all()
    logger.info(
        "Done: %d ingested, %d skipped, %d chunks added",
        len(result.ingested_files),
        len(result.skipped_files),
        result.total_chunks,
    )
    if result.ingested_files:
        logger.info("Ingested: %s", ", ".join(result.ingested_files))
    if result.skipped_files:
        logger.info("Skipped: %s", ", ".join(result.skipped_files))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
