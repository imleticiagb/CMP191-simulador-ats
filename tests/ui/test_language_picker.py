"""Troca de idioma pelas bandeirinhas (FR-027 a FR-030), sem perder entradas nem resultado."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from ats.analysis.llm_client import FakeLlmClient
from ats.domain.models import ExtractionOutput, MatchOutput

APP = str(Path(__file__).parent.parent.parent / "app.py")


def _all_text(at: AppTest) -> str:
    parts = [m.value for m in at.markdown] + [c.value for c in at.caption]
    parts += [b.label for b in at.button] + [t.label for t in at.text_area]
    parts += [e.value for e in at.error]
    return "\n".join(parts)


@pytest.fixture
def app(read_fixture):
    def _make() -> AppTest:
        at = AppTest.from_file(APP, default_timeout=60)
        at.session_state["llm_override"] = FakeLlmClient(
            extract=ExtractionOutput.model_validate_json(read_fixture("extract_ok.json")),
            match=MatchOutput.model_validate_json(read_fixture("match_ok.json")),
        )
        at.run()
        return at

    return _make


def _switch(at: AppTest, code: str) -> AppTest:
    at.button(key=f"lang_{code}").click().run()
    assert not at.exception
    return at


def test_default_is_portuguese_and_the_picker_shows_the_three_flags(app):
    at = app()
    assert at.session_state["ui_language"] == "pt_BR"
    assert [b.key for b in at.button if b.key and b.key.startswith("lang_")] == [
        "lang_pt_BR",
        "lang_en",
        "lang_es",
    ]
    md = "\n".join(m.value for m in at.markdown)
    assert md.count('class="ats-flag"') == 3
    for name in ("Português (Brasil)", "English", "Español"):
        assert f'alt="{name}"' in md
    assert at.button(key="lang_pt_BR").label == "PT ✓"
    assert at.button(key="lang_en").label == "EN"


@pytest.mark.parametrize(
    ("code", "submit", "title"),
    [("en", "Analyze", "ATS Simulator"), ("es", "Analizar", "Simulador de ATS")],
)
def test_switching_translates_the_whole_input_screen(app, code, submit, title):
    at = _switch(app(), code)
    text = _all_text(at)
    assert submit in text and title in text
    assert "Analisar" not in text and "Texto da vaga" not in text
    assert at.button(key=f"lang_{code}").label.endswith("✓")


def test_switching_keeps_what_was_typed(app, read_fixture):
    at = app()
    at.text_area(key="job_text").input("texto da vaga em andamento")
    at.text_area(key="resume_text").input("texto do currículo em andamento")
    _switch(at, "en")
    assert at.text_area(key="job_text").value == "texto da vaga em andamento"
    assert at.text_area(key="resume_text").value == "texto do currículo em andamento"
    _switch(at, "pt_BR")
    assert at.text_area(key="job_text").value == "texto da vaga em andamento"


def test_error_messages_follow_the_language(app):
    at = app()
    _switch(at, "es")
    at.button(key="submit").click().run()
    assert any("Pega el texto de la vacante" in e.value for e in at.error)
    _switch(at, "en")
    at.button(key="submit").click().run()
    assert any("Paste the job text" in e.value for e in at.error)


def test_result_is_translated_and_scores_stay_the_same(app, read_fixture):
    at = app()
    at.text_area(key="job_text").input(read_fixture("job_licenciatura.txt"))
    at.text_area(key="resume_text").input(read_fixture("resume_licenciatura.txt"))
    at.button(key="submit").click().run()
    md_pt = "\n".join(m.value for m in at.markdown)
    overall = re.search(r"(\d{1,3})/100", md_pt).group(1)
    results_before = dict(at.session_state["results"])

    _switch(at, "en")
    md_en = "\n".join(m.value for m in at.markdown)
    assert "Overall score" in md_en and "Met" in md_en
    assert "Nota geral" not in md_en
    assert f"{overall}/100" in md_en
    assert "[EN] " in md_en, "justificativas e requisitos traduzidos"
    assert "Licenciatura em Pedagogia, concluída em 2022" in md_en, "evidência no original"
    assert at.session_state["results"] == results_before, "não refez a análise"
    assert at.button(key="new_analysis").label == "New analysis"

    _switch(at, "es")
    md_es = "\n".join(m.value for m in at.markdown)
    assert "Nota general" in md_es and "Cumplido" in md_es and f"{overall}/100" in md_es

    _switch(at, "pt_BR")
    assert "Nota geral" in "\n".join(m.value for m in at.markdown)


def test_picker_is_visible_on_the_result_screen_too(app, read_fixture):
    at = app()
    at.text_area(key="job_text").input(read_fixture("job_licenciatura.txt"))
    at.text_area(key="resume_text").input(read_fixture("resume_licenciatura.txt"))
    at.button(key="submit").click().run()
    assert {b.key for b in at.button} >= {"lang_pt_BR", "lang_en", "lang_es", "new_analysis"}
