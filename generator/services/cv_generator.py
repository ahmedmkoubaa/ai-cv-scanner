import json
import logging
import re
import time
from pathlib import Path

from adapters.llm.base import LLMAdapter
from adapters.pdf.reportlab_renderer import ReportLabRenderer, profile_to_filename
from domain.models import CVProfile

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a professional CV writer. Generate realistic, diverse candidate profiles for a hiring database.
Return ONLY valid JSON matching the schema below. Do not include markdown fences or commentary.

Schema:
{
  "contact": {
    "full_name": "string",
    "email": "string",
    "phone": "string",
    "location": "City, Country",
    "linkedin": "string or null"
  },
  "summary": "2-3 sentence professional summary",
  "work_experience": [
    {
      "title": "string",
      "company": "string",
      "location": "string",
      "start_date": "Mon YYYY",
      "end_date": "Mon YYYY or null for current role",
      "description": ["bullet point", "..."]
    }
  ],
  "education": [
    {
      "degree": "string",
      "institution": "string",
      "location": "string",
      "graduation_year": "YYYY"
    }
  ],
  "skills": ["skill1", "skill2", "..."]
}

Requirements:
- 2-4 work experiences with 2-4 bullet points each
- 1-2 education entries
- 8-15 relevant skills
- Use realistic but fictional names, companies, and contact details
- Dates must be consistent and plausible"""

DIVERSITY_HINTS = [
    "Senior backend software engineer with Python and cloud experience",
    "Junior frontend developer specializing in React and TypeScript",
    "Data scientist with machine learning and NLP background",
    "DevOps engineer experienced in Kubernetes and CI/CD",
    "Product manager in fintech with agile leadership experience",
    "UX/UI designer with mobile app portfolio",
    "Cybersecurity analyst with SOC and incident response skills",
    "Mobile developer (iOS/Android) with published apps",
    "Full-stack engineer at an early-stage startup",
    "QA automation engineer with Selenium and pytest",
    "Cloud architect with AWS and multi-region deployments",
    "Technical project manager in enterprise SaaS",
    "Business intelligence analyst with SQL and Tableau",
    "Embedded systems engineer with C/C++ and IoT",
    "Site reliability engineer focused on observability",
    "Machine learning engineer deploying models to production",
    "Scrum master transitioning from software development",
    "Database administrator with PostgreSQL optimization expertise",
    "Solutions architect for healthcare technology",
    "Marketing technologist with analytics and MarTech stack",
    "AI research engineer with publications and patents",
    "Blockchain developer with smart contract experience",
    "Technical writer for developer documentation",
    "Engineering manager leading a 10-person team",
    "Sales engineer bridging pre-sales and implementation",
    "Graduate software engineer seeking first full-time role",
    "Platform engineer building internal developer tools",
    "Release manager coordinating cross-functional launches",
    "Network engineer with enterprise infrastructure background",
    "Computer science lecturer with industry consulting",
]


class CVGeneratorService:
    MAX_RETRIES = 3

    def __init__(
        self,
        llm: LLMAdapter,
        renderer: ReportLabRenderer,
        *,
        api_request_delay_seconds: float = 4.0,
    ) -> None:
        self._llm = llm
        self._renderer = renderer
        self._api_request_delay_seconds = api_request_delay_seconds
        self._last_request_start: float | None = None

    def generate_batch(self, count: int, output_dir: Path) -> list[Path]:
        generated: list[Path] = []
        hints = self._select_hints(count)

        # Step 1: Pre-generate all unique candidate names (First + Last Name) in one shot
        logger.info("Pre-generating %d unique candidate names in initial query...", count)
        names = self._pre_generate_names(count)
        logger.info("Generated %d unique names: %s", len(names), ", ".join(names))

        # Step 2: Generate each CV sequentially with the assigned unique name
        for index, (hint, name) in enumerate(zip(hints, names), start=1):
            logger.info("Generating CV %d/%d: %s [%s]", index, count, hint, name)
            profile = self._generate_profile(hint, name, index)
            filename = profile_to_filename(profile, index)
            output_path = output_dir / filename

            if output_path.exists():
                stem = output_path.stem
                output_path = output_dir / f"{stem}_{index:02d}.pdf"

            self._renderer.render(profile, output_path)
            generated.append(output_path)
            logger.info("Saved %s", output_path.name)

        return generated

    def _select_hints(self, count: int) -> list[str]:
        if count <= len(DIVERSITY_HINTS):
            return DIVERSITY_HINTS[:count]
        hints = list(DIVERSITY_HINTS)
        while len(hints) < count:
            hints.append(DIVERSITY_HINTS[len(hints) % len(DIVERSITY_HINTS)])
        return hints[:count]

    def _pre_generate_names(self, count: int) -> list[str]:
        prompt = (
            f"Generate a JSON array containing exactly {count} distinct, realistic full names "
            f"(first name + last name) for fictional job candidates. "
            f"Every single combination of first name and last name must be unique. "
            f"Ensure global diversity (varied cultural, gender, and regional origins).\n"
            f"Return ONLY valid JSON matching this format: [\"First Last\", ...]"
        )

        last_error: Exception | None = None
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                raw = self._generate_with_rate_limit(prompt)
                names = self._parse_name_list(raw, count)
                return names
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Name pre-generation attempt %d/%d failed: %s",
                    attempt,
                    self.MAX_RETRIES,
                    exc,
                )

        raise RuntimeError(
            f"Failed to pre-generate {count} unique names after {self.MAX_RETRIES} attempts"
        ) from last_error

    def _parse_name_list(self, raw: str, expected_count: int) -> list[str]:
        text = raw.strip()
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if fence_match:
            text = fence_match.group(1).strip()
        parsed = json.loads(text)
        if not isinstance(parsed, list):
            raise ValueError("Expected a JSON array of names")

        seen: set[str] = set()
        unique_names: list[str] = []
        for item in parsed:
            name = str(item).strip()
            normalized = " ".join(name.lower().split())
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_names.append(name)

        if len(unique_names) < expected_count:
            raise ValueError(
                f"Expected {expected_count} unique names, but only received {len(unique_names)}"
            )

        return unique_names[:expected_count]

    def _generate_profile(self, diversity_hint: str, assigned_name: str, index: int) -> CVProfile:
        prompt = (
            f"Generate CV #{index} for this candidate archetype: {diversity_hint}\n"
            f"The candidate's full_name MUST be exactly: {assigned_name}\n"
            "Ensure this profile is distinct from typical templates — vary industry, "
            "seniority, geography, and skill emphasis."
        )

        last_error: Exception | None = None
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                raw = self._generate_with_rate_limit(prompt)
                data = self._parse_json(raw)
                # Ensure the full_name in the parsed contact matches the assigned unique name
                if "contact" in data and isinstance(data["contact"], dict):
                    data["contact"]["full_name"] = assigned_name
                return CVProfile.model_validate(data)
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Attempt %d/%d failed for CV #%d: %s",
                    attempt,
                    self.MAX_RETRIES,
                    index,
                    exc,
                )

        raise RuntimeError(
            f"Failed to generate CV #{index} after {self.MAX_RETRIES} attempts"
        ) from last_error

    def _generate_with_rate_limit(self, prompt: str) -> str:
        self._wait_until_interval_elapsed()
        self._last_request_start = time.monotonic()
        return self._llm.generate(prompt, system=SYSTEM_PROMPT)

    def _wait_until_interval_elapsed(self) -> None:
        delay = self._api_request_delay_seconds
        if delay <= 0 or self._last_request_start is None:
            return

        elapsed = time.monotonic() - self._last_request_start
        remaining = delay - elapsed
        if remaining > 0:
            logger.info(
                "Waiting %.1fs before next API request (quota limit)", remaining
            )
            time.sleep(remaining)

    @staticmethod
    def _parse_json(raw: str) -> dict:
        text = raw.strip()
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if fence_match:
            text = fence_match.group(1).strip()
        return json.loads(text)
