"""SC-006: o mesmo texto por PDF e colado dá os mesmos status e a mesma nota de Conteúdo."""

from __future__ import annotations

from ats.analysis.llm_client import FakeLlmClient
from ats.analysis.pipeline import analyze
from ats.domain.models import ExtractionOutput, MatchOutput
from ats.ingest.pdf_reader import read_pdf
from tests.pdf_factory import simple_pdf


def _client(read_fixture) -> FakeLlmClient:
    return FakeLlmClient(
        extract=ExtractionOutput.model_validate_json(read_fixture("extract_ok.json")),
        match=MatchOutput.model_validate_json(read_fixture("match_ok.json")),
    )


def test_pdf_and_pasted_text_give_the_same_statuses_and_content_score(read_fixture):
    job = read_fixture("job_licenciatura.txt")
    resume = read_fixture("resume_licenciatura.txt")
    lines = [ln for ln in resume.splitlines() if ln.strip()]
    content = read_pdf(simple_pdf(lines, fontsize=10), "cv.pdf")

    pasted = analyze(job, resume, _client(read_fixture))
    from_pdf = analyze(job, content.text, _client(read_fixture), source="pdf", pdf_meta=content.meta)

    assert from_pdf.source == "pdf" and pasted.source == "pasted"
    assert [(v.requirement_id, v.status) for v in from_pdf.verdicts] == [
        (v.requirement_id, v.status) for v in pasted.verdicts
    ]
    assert from_pdf.category("conteudo").score == pasted.category("conteudo").score == 86


def test_evidence_survives_pdf_line_breaks(read_fixture):
    job = read_fixture("job_licenciatura.txt")
    lines = [ln for ln in read_fixture("resume_licenciatura.txt").splitlines() if ln.strip()]
    content = read_pdf(simple_pdf(lines, fontsize=10), "cv.pdf")
    result = analyze(job, content.text, _client(read_fixture), source="pdf", pdf_meta=content.meta)
    assert result.verdict_for("R1").evidence, "a evidência literal precisa ser encontrada no texto extraído"
