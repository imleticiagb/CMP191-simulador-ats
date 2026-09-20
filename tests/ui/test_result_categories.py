"""Tela de resultado da história 3: categorias com barra, número, justificativa e rubrica."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from ats.analysis.llm_client import FakeLlmClient
from ats.domain.models import ExtractionOutput, MatchOutput
from tests.pdf_factory import simple_pdf

APP = str(Path(__file__).parent.parent.parent / "app.py")


def _markdown(at: AppTest) -> str:
    return "\n".join(m.value for m in at.markdown)


@pytest.fixture
def analyzed(read_fixture):
    def _run(pdf: bool = False) -> AppTest:
        at = AppTest.from_file(APP, default_timeout=60)
        at.session_state["llm_override"] = FakeLlmClient(
            extract=ExtractionOutput.model_validate_json(read_fixture("extract_ok.json")),
            match=MatchOutput.model_validate_json(read_fixture("match_ok.json")),
        )
        at.run()
        at.text_area(key="job_text").input(read_fixture("job_licenciatura.txt"))
        if pdf:
            lines = [ln for ln in read_fixture("resume_licenciatura.txt").splitlines() if ln.strip()]
            at.button(key="mode_pdf").click().run()
            at.file_uploader[0].set_value(("cv.pdf", simple_pdf(lines, fontsize=10), "application/pdf")).run()
        else:
            at.text_area(key="resume_text").input(read_fixture("resume_licenciatura.txt"))
        at.button(key="submit").click().run()
        assert not at.exception
        return at

    return _run


def test_pasted_text_shows_content_and_structure_bars_and_design_not_evaluated(analyzed):
    md = _markdown(analyzed())
    assert md.count('role="progressbar"') == 3  # geral, Conteúdo e Estrutura
    for name in ("Conteúdo", "Estrutura", "Design"):
        assert name in md
    assert "não avaliada" in md
    assert "só é avaliado quando você envia o currículo em PDF" in md
    assert "Conteúdo 70 e Estrutura 30" in md


def test_pdf_shows_four_bars_and_the_60_25_15_weights(analyzed):
    md = _markdown(analyzed(pdf=True))
    assert md.count('role="progressbar"') == 4
    assert "Conteúdo 60, Estrutura 25 e Design 15" in md
    assert "não avaliada" not in md


def test_each_category_bar_has_number_and_a_justification_beside_it(analyzed):
    at = analyzed()
    md = _markdown(at)
    assert "86/100" in md
    assert "Quanto do que a vaga pede aparece no seu currículo." in md
    assert any("Detalhes da nota" in e.label for e in at.expander)


def test_overall_score_matches_the_weighted_categories(analyzed):
    at = analyzed()
    result = next(iter(at.session_state["results"].values()))
    from ats.analysis.scoring import compute_overall

    assert result.overall == compute_overall(result.categories)
    assert re.search(rf"{result.overall}/100", _markdown(at))


def test_low_categories_show_gentle_improvement_hints(analyzed):
    at = analyzed()
    md = _markdown(at)
    assert "Como melhorar" in md
    assert "seção de" in md or "e-mail" in md or "período" in md
