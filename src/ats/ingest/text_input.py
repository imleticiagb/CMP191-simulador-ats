"""Normalização e validação do texto colado da vaga e do currículo (FR-005)."""

from __future__ import annotations

import re
import unicodedata

from ats import config
from ats.domain.errors import TextTooLong, TextTooShort
from ats.domain.models import InputSource, JobPosting, PdfMeta, Resume


def normalize_text(text: str) -> str:
    """Padroniza quebras de linha e espaços e junta palavras hifenizadas na quebra de linha."""
    text = unicodedata.normalize("NFC", text).replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    text = re.sub(r"[ \t\f\v ]+", " ", text)
    text = re.sub(r" ?\n ?", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def validate_job(text: str) -> JobPosting:
    """Vaga: de `MIN_JOB_CHARS` a `MAX_JOB_CHARS` caracteres depois de normalizar."""
    normalized = normalize_text(text or "")
    if len(normalized) < config.MIN_JOB_CHARS:
        raise TextTooShort("error.job.too_short")
    if len(normalized) > config.MAX_JOB_CHARS:
        raise TextTooLong("error.job.too_long")
    return JobPosting(text=normalized)


def validate_resume(text: str, source: InputSource = "pasted", pdf_meta: PdfMeta | None = None) -> Resume:
    """Currículo: de `MIN_RESUME_CHARS` a `MAX_RESUME_CHARS` caracteres depois de normalizar."""
    normalized = normalize_text(text or "")
    if len(normalized) < config.MIN_RESUME_CHARS:
        raise TextTooShort("error.resume.too_short")
    if len(normalized) > config.MAX_RESUME_CHARS:
        raise TextTooLong("error.resume.too_long")
    return Resume(source=source, text=normalized, pdf_meta=pdf_meta)
