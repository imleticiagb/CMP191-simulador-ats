"""SC-003 (marcador `live`): mede a taxa de acerto do status em casos de relação semântica conhecida.

Roda com o modelo real: `uv run pytest -m live tests/live/test_semantic_accuracy.py -s`
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ats.analysis.llm_client import GeminiLlmClient, resolve_api_key
from ats.domain.models import Requirement
from ats.ingest.text_input import normalize_text

pytestmark = pytest.mark.live

CASES = json.loads(
    (Path(__file__).parent.parent / "fixtures" / "semantic_cases.json").read_text(encoding="utf-8")
)
TARGET = 0.90


@pytest.mark.skipif(
    not resolve_api_key(),
    reason="exige GEMINI_API_KEY (ou .streamlit/secrets.toml)",
)
def test_semantic_accuracy_meets_the_target():
    """SC-003: reconhecer as relações semânticas conhecidas (casos com status esperado `atendido`).

    Os casos `parcial` e `nao_atendido` também rodam, e o acerto geral é informado, mas a zona cinzenta entre
    "parcial" e "não atendido" é subjetiva e não entra na meta.
    """
    client = GeminiLlmClient()
    hits, total, relation_hits, relation_total, missing_explanation = 0, 0, 0, 0, 0
    false_positives = 0
    for case in CASES:
        requirement = Requirement(
            id="R1",
            text=case["requirement"],
            kind="outro",
            importance="obrigatorio",
            source_excerpt=case["requirement"],
        )
        output = client.match_requirements(normalize_text(case["resume_excerpt"]), [requirement])
        verdict = output.verdicts[0]
        hit = verdict.status == case["expected_status"]
        total, hits = total + 1, hits + hit
        if case["expected_status"] == "atendido":
            relation_total, relation_hits = relation_total + 1, relation_hits + hit
        if case["expected_status"] == "nao_atendido" and verdict.status == "atendido":
            false_positives += 1
        missing_explanation += verdict.status != "nao_atendido" and not verdict.justification.strip()
        if not hit:
            print(
                f"  divergiu {case['id']}: {case['requirement']!r} | esperado {case['expected_status']}, veio {verdict.status}"
            )
    rate = relation_hits / relation_total
    print(
        f"\nrelações semânticas reconhecidas: {relation_hits}/{relation_total} = {rate:.0%} | "
        f"acerto geral: {hits}/{total} = {hits / total:.0%} | falsos positivos: {false_positives} | "
        f"sem explicação: {missing_explanation}"
    )
    assert missing_explanation == 0, "toda dedução precisa vir com explicação"
    assert false_positives == 0, "um requisito sem relação não pode ser dado como atendido"
    assert rate >= TARGET
