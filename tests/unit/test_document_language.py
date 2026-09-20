"""FR-031 e FR-032: idiomas dos documentos."""

from __future__ import annotations

import json

import pytest

from ats.analysis.llm_client import FakeLlmClient
from ats.analysis.pipeline import analyze
from ats.domain.errors import UnsupportedLanguage
from ats.domain.models import ExtractionOutput, MatchOutput


def _client(read_fixture, job_lang="pt", resume_lang="pt"):
    extract = json.loads(read_fixture("extract_ok.json"))
    extract["document_check"]["language"] = job_lang
    match = json.loads(read_fixture("match_ok.json"))
    match["document_check"]["language"] = resume_lang
    return FakeLlmClient(
        extract=ExtractionOutput.model_validate(extract), match=MatchOutput.model_validate(match)
    )


@pytest.fixture
def texts(read_fixture):
    return read_fixture("job_licenciatura.txt"), read_fixture("resume_licenciatura.txt")


def test_unsupported_resume_language_gives_no_score(read_fixture, texts):
    with pytest.raises(UnsupportedLanguage) as caught:
        analyze(*texts, _client(read_fixture, resume_lang="other"))
    assert caught.value.message_key == "error.unsupported_language"


def test_unsupported_job_language_gives_no_score(read_fixture, texts):
    with pytest.raises(UnsupportedLanguage):
        analyze(*texts, _client(read_fixture, job_lang="other"))


def test_different_supported_languages_are_analyzed_with_a_note(read_fixture, texts):
    result = analyze(*texts, _client(read_fixture, job_lang="en", resume_lang="pt"))
    assert result.language_notes == ["result.language_note.mixed"]
    assert (result.job_language, result.resume_language) == ("en", "pt")
    assert result.category("conteudo").score == 86


@pytest.mark.parametrize("lang", ["pt", "en", "es"])
def test_same_language_has_no_note(read_fixture, texts, lang):
    result = analyze(*texts, _client(read_fixture, job_lang=lang, resume_lang=lang))
    assert result.language_notes == []
