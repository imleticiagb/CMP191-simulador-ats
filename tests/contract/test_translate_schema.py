"""Contrato da tradução: o modelo segue contracts/llm-translate.schema.json e as respostas gravadas validam."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from ats.domain.models import TranslationOutput

CONTRACT = (
    Path(__file__).parent.parent.parent
    / "specs"
    / "001-simulador-analise-curriculo"
    / "contracts"
    / "llm-translate.schema.json"
)
FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_recorded_translations_validate_against_the_contract_and_the_model():
    spec = json.loads(CONTRACT.read_text(encoding="utf-8"))
    for name in ("translate_en.json", "translate_es.json"):
        data = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
        jsonschema.validate(data, spec)
        out = TranslationOutput.model_validate(data)
        assert out.target_language == name[len("translate_") : -len(".json")]


def test_only_english_and_spanish_are_valid_targets():
    spec = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert spec["properties"]["target_language"]["enum"] == ["en", "es"]
    bad = {"target_language": "pt", "items": []}
    try:
        TranslationOutput.model_validate(bad)
    except Exception:
        return
    raise AssertionError("pt não é um destino de tradução")
