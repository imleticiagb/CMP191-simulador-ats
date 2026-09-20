"""SC-012: notas e status idênticos nos três idiomas, e a troca não refaz a análise."""

from __future__ import annotations

import pytest

from ats.analysis.llm_client import FakeLlmClient
from ats.analysis.pipeline import analyze
from ats.analysis.translate import get_translation
from ats.domain.models import ExtractionOutput, MatchOutput
from ats.ui.components.requirement_card import render_requirement_card
from ats.ui.components.result_view import explain_criterion, render_overall_html, resolve_hint


@pytest.fixture
def setup(read_fixture):
    client = FakeLlmClient(
        extract=ExtractionOutput.model_validate_json(read_fixture("extract_ok.json")),
        match=MatchOutput.model_validate_json(read_fixture("match_ok.json")),
    )
    cache = {}
    result = analyze(
        read_fixture("job_licenciatura.txt"), read_fixture("resume_licenciatura.txt"), client, cache=cache
    )
    return client, result, cache


def test_switching_language_never_reruns_the_analysis_or_changes_the_result(setup):
    client, result, cache = setup
    before = result.model_dump()
    calls = list(client.calls)
    translations = {}
    for lang in ("en", "es", "pt_BR", "en"):
        get_translation(result, lang, translations, client)
    assert [c for c in client.calls if c != "translate"] == [c for c in calls if c != "translate"]
    assert result.model_dump() == before
    assert len(cache) == 1


def test_scores_and_statuses_are_identical_in_the_three_languages(setup):
    client, result, _ = setup
    translations = {}
    for lang in ("pt_BR", "en", "es"):
        bundle = get_translation(result, lang, translations, client)
        items = bundle.items if bundle else None
        assert f"{result.overall}/100" in render_overall_html(result, lang)
        for requirement in result.requirements:
            verdict = result.verdict_for(requirement.id)
            html = render_requirement_card(requirement, verdict, lang, items)
            assert f"status-{verdict.status}" in html
            for excerpt in verdict.evidence:
                assert excerpt in html, "a evidência fica no idioma original"


def test_labels_change_language_but_criteria_points_do_not(setup):
    _, result, _ = setup
    content = result.category("conteudo")
    texts = {lang: explain_criterion(content.criteria[0], lang) for lang in ("pt_BR", "en", "es")}
    assert texts["pt_BR"] != texts["en"] != texts["es"]
    assert "2" in texts["en"] and "2" in texts["es"]


def test_hints_render_in_every_language(setup):
    client, result, _ = setup
    for lang in ("pt_BR", "en", "es"):
        bundle = get_translation(result, lang, {}, client)
        for hint in result.improvement_hints:
            assert resolve_hint(hint, result, lang, bundle.items if bundle else None)
