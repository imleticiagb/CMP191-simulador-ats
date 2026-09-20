"""Princípio I, regra 3 (marcador `live`): mede quanto os vereditos variam entre execuções independentes.

Não há meta de 100%: o resultado é medido e informado. Roda com o modelo real:
`uv run pytest -m live tests/live/test_determinism.py -s`
"""

from __future__ import annotations

import os
from collections import Counter
from pathlib import Path

import pytest

from ats.analysis.llm_client import GeminiLlmClient, resolve_api_key
from ats.analysis.pipeline import analyze

pytestmark = pytest.mark.live
FIXTURES = Path(__file__).parent.parent / "fixtures"
RUNS = int(os.environ.get("ATS_LIVE_RUNS", "5"))


@pytest.mark.skipif(
    not resolve_api_key(),
    reason="exige GEMINI_API_KEY (ou .streamlit/secrets.toml)",
)
def test_reports_the_rate_of_identical_verdicts_across_independent_runs():
    job = (FIXTURES / "job_licenciatura.txt").read_text(encoding="utf-8")
    resume = (FIXTURES / "resume_licenciatura.txt").read_text(encoding="utf-8")
    signatures: list[tuple] = []
    for _ in range(RUNS):  # cliente e cache novos a cada execução, como em sessões diferentes
        result = analyze(job, resume, GeminiLlmClient(), cache={})
        signatures.append(tuple((v.requirement_id, v.status) for v in result.verdicts) + (result.overall,))
    most_common, count = Counter(signatures).most_common(1)[0]
    print(f"\nexecuções idênticas: {count}/{RUNS} ({count / RUNS:.0%}); assinatura mais comum: {most_common}")
    assert count >= 1
