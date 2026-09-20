"""Extração dos requisitos da vaga pelo modelo de linguagem (chamada 1)."""

from __future__ import annotations

from dataclasses import dataclass

from ats import config
from ats.analysis.llm_client import LlmClient
from ats.domain.errors import NoRequirementsFound, NotAJobPosting
from ats.domain.models import JobPosting, Language, Requirement


@dataclass(frozen=True)
class ExtractionResult:
    requirements: list[Requirement]
    language: Language


def extract_requirements(client: LlmClient, job: JobPosting) -> ExtractionResult:
    output = client.extract_requirements(job.text)
    if not output.document_check.looks_like_job_posting:
        raise NotAJobPosting()
    raw = output.requirements[: config.MAX_REQUIREMENTS]
    if not raw:
        raise NoRequirementsFound()
    # ids únicos e em ordem: R1, R2, R3...
    requirements = [
        Requirement(
            id=f"R{i}",
            text=r.text.strip(),
            kind=r.kind,
            importance=r.importance,
            source_excerpt=r.source_excerpt.strip(),
        )
        for i, r in enumerate(raw, start=1)
    ]
    return ExtractionResult(requirements=requirements, language=output.document_check.language)
