"""Fluxo de tela da história 1: colar vaga e currículo, analisar e ver o resultado."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from ats.analysis.llm_client import FakeLlmClient
from ats.domain.models import ExtractionOutput, MatchOutput

APP = str(Path(__file__).parent.parent.parent / "app.py")


def _markdown(at: AppTest) -> str:
    return "\n".join(m.value for m in at.markdown)


@pytest.fixture
def app(read_fixture):
    def _make(match="match_ok.json") -> AppTest:
        at = AppTest.from_file(APP, default_timeout=60)
        at.session_state["llm_override"] = FakeLlmClient(
            extract=ExtractionOutput.model_validate_json(read_fixture("extract_ok.json")),
            match=MatchOutput.model_validate_json(read_fixture(match)),
        )
        at.run()
        return at

    return _make


def _fill_and_submit(at: AppTest, read_fixture, job=None, resume=None) -> AppTest:
    at.text_area(key="job_text").input(job if job is not None else read_fixture("job_licenciatura.txt"))
    at.text_area(key="resume_text").input(
        resume if resume is not None else read_fixture("resume_licenciatura.txt")
    )
    at.button(key="submit").click().run()
    return at


def test_privacy_notice_is_visible_before_the_analyze_button(app):
    at = app()
    assert not at.exception
    assert "serviço de inteligência artificial externo" in _markdown(at) + " ".join(
        c.value for c in at.caption
    )
    assert at.button(key="submit").label == "Analisar"


def test_pasting_and_analyzing_shows_score_and_one_card_per_requirement(app, read_fixture):
    at = _fill_and_submit(app(), read_fixture)
    assert not at.exception
    md = _markdown(at)
    assert re.search(r"\d{1,3}/100", md), "nota geral no formato N/100"
    assert md.count('class="ats-card"') >= 4
    assert "Não encontramos nenhuma evidência no currículo." in md
    assert "Nível superior ao pedido" in md
    assert "Obrigatório" in md and "Desejável" in md


def test_input_errors_are_shown_without_a_score(app, read_fixture):
    at = _fill_and_submit(app(), read_fixture, job="curta", resume="curto")
    assert not at.exception
    assert not re.search(r"\d{1,3}/100", _markdown(at))
    assert any("Cole o texto da vaga" in e.value for e in at.error)


def test_new_analysis_clears_inputs_and_results(app, read_fixture):
    at = _fill_and_submit(app(), read_fixture)
    assert re.search(r"\d{1,3}/100", _markdown(at))
    at.button(key="new_analysis").click().run()
    assert not at.exception
    assert not re.search(r"\d{1,3}/100", _markdown(at))
    assert at.text_area(key="job_text").value == ""
    assert at.text_area(key="resume_text").value == ""
    assert at.session_state["results"] == {}
