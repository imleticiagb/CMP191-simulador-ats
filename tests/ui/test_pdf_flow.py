"""Fluxo de tela da história 2: enviar o currículo em PDF."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from ats.analysis.llm_client import FakeLlmClient
from ats.domain.models import ExtractionOutput, MatchOutput
from tests.pdf_factory import encrypted_pdf, simple_pdf

APP = str(Path(__file__).parent.parent.parent / "app.py")


def _markdown(at: AppTest) -> str:
    return "\n".join(m.value for m in at.markdown)


@pytest.fixture
def app(read_fixture):
    def _make() -> AppTest:
        at = AppTest.from_file(APP, default_timeout=60)
        at.session_state["llm_override"] = FakeLlmClient(
            extract=ExtractionOutput.model_validate_json(read_fixture("extract_ok.json")),
            match=MatchOutput.model_validate_json(read_fixture("match_ok.json")),
        )
        at.run()
        at.button(key="mode_pdf").click().run()
        return at

    return _make


@pytest.fixture
def resume_pdf(read_fixture) -> bytes:
    lines = [ln for ln in read_fixture("resume_licenciatura.txt").splitlines() if ln.strip()]
    return simple_pdf(lines, fontsize=10)


def test_choosing_pdf_shows_the_uploader_instead_of_the_text_box(app):
    at = app()
    assert not at.exception
    assert len(at.file_uploader) == 1
    assert not at.text_area(key="job_text").value
    assert all(t.key != "resume_text" for t in at.text_area)


def test_valid_pdf_is_confirmed_by_name_and_analyzed(app, read_fixture, resume_pdf):
    at = app()
    at.text_area(key="job_text").input(read_fixture("job_licenciatura.txt"))
    at.file_uploader[0].set_value(("cv.pdf", resume_pdf, "application/pdf")).run()
    assert not at.exception
    assert any("cv.pdf" in s.value for s in at.success)
    at.button(key="submit").click().run()
    assert not at.exception
    assert re.search(r"\d{1,3}/100", _markdown(at))


def test_only_the_chosen_input_is_used(app, read_fixture, resume_pdf):
    at = app()
    at.session_state["resume_text"] = "curto"  # texto inválido guardado da outra opção
    at.text_area(key="job_text").input(read_fixture("job_licenciatura.txt"))
    at.file_uploader[0].set_value(("cv.pdf", resume_pdf, "application/pdf")).run()
    at.button(key="submit").click().run()
    assert not at.error
    assert re.search(r"\d{1,3}/100", _markdown(at))


def test_non_pdf_file_is_refused_with_a_gentle_message(app):
    at = app()
    at.file_uploader[0].set_value(("cv.docx", b"PK\x03\x04conteudo", "application/octet-stream")).run()
    assert not at.exception
    assert any("Só conseguimos ler arquivos PDF" in e.value for e in at.error)


def test_unreadable_pdf_suggests_pasting_the_text(app):
    at = app()
    at.file_uploader[0].set_value(("cv.pdf", encrypted_pdf(["segredo"] * 10), "application/pdf")).run()
    assert any("colar o texto" in e.value for e in at.error)
    at.text_area(key="job_text")  # a entrada da vaga continua na tela


def test_submitting_without_a_file_asks_for_content(app, read_fixture):
    at = app()
    at.text_area(key="job_text").input(read_fixture("job_licenciatura.txt"))
    at.button(key="submit").click().run()
    assert any("currículo está curto demais" in e.value for e in at.error)
