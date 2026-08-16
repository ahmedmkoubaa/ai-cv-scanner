import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

from domain.models import CVProfile


class ReportLabRenderer:
    MARGIN = 0.75 * inch

    def render(self, profile: CVProfile, output_path: Path) -> None:
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            leftMargin=self.MARGIN,
            rightMargin=self.MARGIN,
            topMargin=self.MARGIN,
            bottomMargin=self.MARGIN,
        )

        styles = getSampleStyleSheet()
        name_style = ParagraphStyle(
            "Name",
            parent=styles["Heading1"],
            fontSize=22,
            spaceAfter=4,
            textColor=colors.HexColor("#1a1a2e"),
        )
        contact_style = ParagraphStyle(
            "Contact",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#444444"),
            spaceAfter=12,
        )
        section_style = ParagraphStyle(
            "Section",
            parent=styles["Heading2"],
            fontSize=12,
            spaceBefore=10,
            spaceAfter=4,
            textColor=colors.HexColor("#16213e"),
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            spaceAfter=4,
        )
        bullet_style = ParagraphStyle(
            "Bullet",
            parent=body_style,
            leftIndent=12,
            bulletIndent=0,
            spaceAfter=2,
        )
        job_title_style = ParagraphStyle(
            "JobTitle",
            parent=body_style,
            fontName="Helvetica-Bold",
            spaceAfter=2,
        )
        job_meta_style = ParagraphStyle(
            "JobMeta",
            parent=body_style,
            fontSize=9,
            textColor=colors.HexColor("#555555"),
            spaceAfter=4,
        )

        story: list = []

        contact = profile.contact
        story.append(Paragraph(self._escape(contact.full_name), name_style))

        contact_parts = [
            contact.email,
            contact.phone,
            contact.location,
        ]
        if contact.linkedin:
            contact_parts.append(contact.linkedin)
        story.append(
            Paragraph(self._escape(" | ".join(contact_parts)), contact_style)
        )
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")))
        story.append(Spacer(1, 6))

        story.append(Paragraph("Professional Summary", section_style))
        story.append(Paragraph(self._escape(profile.summary), body_style))

        story.append(Paragraph("Work Experience", section_style))
        for job in profile.work_experience:
            date_range = f"{job.start_date} – {job.end_date or 'Present'}"
            story.append(
                Paragraph(
                    self._escape(f"{job.title} — {job.company}"),
                    job_title_style,
                )
            )
            story.append(
                Paragraph(
                    self._escape(f"{job.location} | {date_range}"),
                    job_meta_style,
                )
            )
            for bullet in job.description:
                story.append(
                    Paragraph(
                        self._escape(bullet),
                        bullet_style,
                        bulletText="•",
                    )
                )
            story.append(Spacer(1, 4))

        story.append(Paragraph("Education", section_style))
        for edu in profile.education:
            story.append(
                Paragraph(
                    self._escape(
                        f"{edu.degree}, {edu.institution} ({edu.graduation_year})"
                    ),
                    body_style,
                )
            )
            story.append(
                Paragraph(self._escape(edu.location), job_meta_style)
            )

        story.append(Paragraph("Skills", section_style))
        skills_text = ", ".join(profile.skills)
        story.append(Paragraph(self._escape(skills_text), body_style))

        doc.build(story)

    @staticmethod
    def _escape(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )


def profile_to_filename(profile: CVProfile, index: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", profile.contact.full_name.lower()).strip("_")
    if not slug:
        slug = f"candidate_{index:02d}"
    return f"{slug}.pdf"
