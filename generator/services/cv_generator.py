import json
import logging
import re
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

    def __init__(self, llm: LLMAdapter, renderer: ReportLabRenderer) -> None:
        self._llm = llm
        self._renderer = renderer

    def generate_batch(self, count: int, output_dir: Path) -> list[Path]:
        generated: list[Path] = []
        hints = self._select_hints(count)

        for index, hint in enumerate(hints, start=1):
            logger.info("Generating CV %d/%d: %s", index, count, hint)
            profile = self._generate_profile(hint, index)
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

    def _generate_profile(self, diversity_hint: str, index: int) -> CVProfile:
        prompt = (
            f"Generate CV #{index} for this candidate archetype: {diversity_hint}\n"
            "Ensure this profile is distinct from typical templates — vary industry, "
            "seniority, geography, and skill emphasis."
        )

        last_error: Exception | None = None
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                raw = self._llm.generate(prompt, system=SYSTEM_PROMPT)
                data = self._parse_json(raw)
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

    @staticmethod
    def _parse_json(raw: str) -> dict:
        text = raw.strip()
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if fence_match:
            text = fence_match.group(1).strip()
        return json.loads(text)
