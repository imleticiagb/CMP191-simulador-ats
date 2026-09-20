"""Contrato: os modelos pydantic e as respostas gravadas seguem contracts/llm-*.schema.json."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from ats.domain.models import ExtractionOutput, MatchOutput, TranslationOutput

CONTRACTS = Path(__file__).parent.parent.parent / "specs" / "001-simulador-analise-curriculo" / "contracts"
FIXTURES = Path(__file__).parent.parent / "fixtures"

CASES = [
    ("llm-extract-requirements.schema.json", ExtractionOutput, ["extract_ok.json"]),
    ("llm-match-requirements.schema.json", MatchOutput, ["match_ok.json", "match_sem_evidencia.json"]),
    ("llm-translate.schema.json", TranslationOutput, ["translate_en.json", "translate_es.json"]),
]


def _resolve(node, defs):
    if isinstance(node, dict) and "$ref" in node:
        return _resolve(defs[node["$ref"].split("/")[-1]], defs)
    return node


def _shape(node, defs):
    """Reduz um esquema ao que importa para o contrato: tipo, propriedades, obrigatórios e enumerações."""
    node = _resolve(node, defs)
    shape = {}
    if "enum" in node:
        shape["enum"] = sorted(node["enum"])
    if "properties" in node:
        shape["required"] = sorted(node.get("required", []))
        shape["properties"] = {k: _shape(v, defs) for k, v in node["properties"].items()}
        assert node.get("additionalProperties") is False, "additionalProperties deve ser false"
    if "items" in node:
        shape["items"] = _shape(node["items"], defs)
    if node.get("type") in ("boolean", "array", "object"):
        shape["type"] = node["type"]
    return shape


@pytest.mark.parametrize(("contract", "model", "_fixtures"), CASES)
def test_pydantic_model_matches_contract(contract, model, _fixtures):
    spec = json.loads((CONTRACTS / contract).read_text(encoding="utf-8"))
    generated = model.model_json_schema()
    defs = generated.get("$defs", {})
    assert _shape(generated, defs) == _shape(spec, spec.get("$defs", {}))


@pytest.mark.parametrize(("contract", "model", "fixtures"), CASES)
def test_recorded_responses_validate(contract, model, fixtures):
    spec = json.loads((CONTRACTS / contract).read_text(encoding="utf-8"))
    for name in fixtures:
        data = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
        jsonschema.validate(data, spec)
        model.model_validate(data)
