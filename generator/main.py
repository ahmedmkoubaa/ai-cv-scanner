import logging
import sys
from pathlib import Path

from adapters.llm.gemini import create_gemini_adapter
from adapters.llm.openrouter import create_openrouter_adapter
from adapters.pdf.reportlab_renderer import ReportLabRenderer
from config import settings
from services.cv_generator import CVGeneratorService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def create_llm_adapter():
    provider = settings.llm_provider
    if provider == "gemini":
        return create_gemini_adapter(settings.gemini_api_key, settings.gemini_model)
    if provider == "openrouter":
        return create_openrouter_adapter(
            settings.openrouter_api_key, settings.openrouter_model
        )
    raise ValueError(
        f"Unsupported LLM_PROVIDER: {provider!r}. Use 'gemini' or 'openrouter'."
    )


def main() -> int:
    base_dir = Path(__file__).resolve().parent
    output_dir = settings.resolve_output_dir(base_dir)

    count = settings.cv_count
    if count < 25 or count > 30:
        logger.warning(
            "CV_COUNT is %d; recommended range is 25–30. Proceeding anyway.",
            count,
        )

    logger.info("Provider: %s", settings.llm_provider)
    logger.info("Output directory: %s", output_dir)
    if settings.api_request_delay_seconds > 0:
        logger.info(
            "API request delay: %.1fs between calls",
            settings.api_request_delay_seconds,
        )
    else:
        logger.info("API request delay: disabled")
    logger.info("Generating %d CV PDFs...", count)

    try:
        llm = create_llm_adapter()
    except ValueError as exc:
        logger.error("%s", exc)
        return 1

    service = CVGeneratorService(
        llm=llm,
        renderer=ReportLabRenderer(),
        api_request_delay_seconds=settings.api_request_delay_seconds,
    )
    try:
        paths = service.generate_batch(count=count, output_dir=output_dir)
    except Exception as exc:
        logger.error("Generation failed: %s", exc)
        return 1

    logger.info("Done. Generated %d PDFs in %s", len(paths), output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
