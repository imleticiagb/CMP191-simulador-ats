"""Tradução sob demanda: só textos escritos pelo modelo, nunca evidência, número ou status."""

from __future__ import annotations

import pytest

from ats.analysis.llm_client import FakeLlmClient
from ats.analysis.pipeline import analyze
from ats.analysis.translate import collect_items, get_translation, missing_items, translate_result
from ats.domain.models import ExtractionOutput, MatchOutput, TranslationOutput
from ats.ui.components.requirement_card import render_requirement_card


@pytest.fixture
def result(read_fixture):
    client = FakeLlmClient(
        extract=ExtractionOutput.model_validate_json(read_fixture("extract_ok.json")),
        match=MatchOutput.model_validate_json(read_fixture("match_ok.json")),
    )
    return analyze(read_fixture("job_licenciatura.txt"), read_fixture("resume_licenciatura.txt"), client)


def test_only_llm_written_texts_are_collected(result):
    items = collect_items(result)
    assert items["R1.text"] == "Licenciatura em curso"
    assert "concluiu a licenciatura" in items["R1.justification"]
    assert "R4.justification" not in items, "justificativa vazia não é traduzida"
    joined = " ".join(items.values())
    for verdict in result.verdicts:
        for excerpt in verdict.evidence:
            assert excerpt not in joined, "evidência nunca é traduzida"
    assert not any(v in items for v in ("86", "atendido"))


def test_translate_result_calls_the_client_once_and_keeps_only_requested_keys(result, read_fixture):
    extra = TranslationOutput.model_validate_json(read_fixture("translate_en.json"))
    extra.items.append(type(extra.items[0])(key="Z9.text", text="não pedido"))
    client = FakeLlmClient(translate=extra)
    bundle = translate_result(client, result, "en")
    assert client.calls == ["translate"]
    assert bundle.result_id == result.result_id and bundle.language == "en"
    assert "Z9.text" not in bundle.items
    assert bundle.items["R1.text"] == "[EN] Ongoing bachelor's degree"


def test_missing_keys_are_reported_and_fall_back_to_portuguese(result, read_fixture):
    partial = TranslationOutput.model_validate_json(read_fixture("translate_es.json"))
    bundle = translate_result(FakeLlmClient(translate=partial), result, "es")
    missing = missing_items(result, bundle)
    assert "R3.text" in missing
    card = render_requirement_card(result.requirements[2], result.verdict_for("R3"), "es", bundle.items)
    assert "Domínio de pacote Office" in card, "sem tradução, o texto original em português aparece"
    card1 = render_requirement_card(result.requirements[0], result.verdict_for("R1"), "es", bundle.items)
    assert "Licenciatura en curso" in card1


def test_translation_is_cached_per_result_and_language(result):
    client, cache = FakeLlmClient(), {}
    first = get_translation(result, "en", cache, client)
    get_translation(result, "en", cache, client)
    assert client.calls == ["translate"]
    get_translation(result, "es", cache, client)
    assert client.calls == ["translate", "translate"]
    assert set(cache) == {(result.result_id, "en"), (result.result_id, "es")}
    assert first.language == "en"


def test_portuguese_needs_no_translation(result):
    client = FakeLlmClient()
    assert get_translation(result, "pt_BR", {}, client) is None
    assert client.calls == []


def test_evidence_and_numbers_are_not_touched_by_translation(result):
    bundle = translate_result(FakeLlmClient(), result, "es")
    card = render_requirement_card(result.requirements[0], result.verdict_for("R1"), "es", bundle.items)
    assert "Licenciatura em Pedagogia, concluída em 2022" in card
