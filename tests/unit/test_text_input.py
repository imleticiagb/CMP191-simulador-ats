"""Entrada de texto: normalização e limites (FR-005)."""

from __future__ import annotations

import pytest

from ats.domain.errors import TextTooLong, TextTooShort
from ats.ingest.text_input import normalize_text, validate_job, validate_resume

JOB = "Requisitos: " + "experiência com atendimento ao cliente e domínio de planilhas. " * 3
RESUME = (
    "Experiência profissional: " + "atendimento ao cliente e organização de rotinas administrativas. " * 4
)


def test_normalization_collapses_spaces_and_hyphenation():
    raw = "Atendi-\nmento   ao\tcliente\r\n\r\n\r\n\r\nSegunda linha  "
    assert normalize_text(raw) == "Atendimento ao cliente\n\nSegunda linha"


def test_job_limits_are_100_to_20000_after_normalizing():
    assert validate_job(JOB).text
    with pytest.raises(TextTooShort) as short:
        validate_job("curta")
    assert short.value.message_key == "error.job.too_short"
    with pytest.raises(TextTooShort):
        validate_job("   \n  ")
    with pytest.raises(TextTooLong) as long:
        validate_job("a " * 10_001)
    assert long.value.message_key == "error.job.too_long"


def test_resume_limits_are_200_to_60000_after_normalizing():
    assert validate_resume(RESUME).source == "pasted"
    with pytest.raises(TextTooShort) as short:
        validate_resume("x" * 199)
    assert short.value.message_key == "error.resume.too_short"
    with pytest.raises(TextTooLong) as long:
        validate_resume("palavra " * 8_000)
    assert long.value.message_key == "error.resume.too_long"


def test_spaces_do_not_count_toward_the_minimum():
    with pytest.raises(TextTooShort):
        validate_resume("a" + " " * 500)
