"""Julgamento dos requisitos contra o currículo: validação em código e reunião de blocos."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from ats.analysis.llm_client import LlmClient
from ats.domain.models import Language, RawVerdict, Requirement, Resume, Verdict
from ats.ingest.chunking import chunk_text, needs_chunking

MAX_EVIDENCE = 3
_RANK = {"atendido": 2, "parcial": 1, "nao_atendido": 0}


@dataclass(frozen=True)
class JudgeResult:
    verdicts: list[Verdict]
    language: Language
    looks_like_resume: bool


def _norm(text: str) -> str:
    return " ".join(text.split())


def _without_evidence(requirement_id: str, justification: str = "") -> Verdict:
    return Verdict(
        requirement_id=requirement_id,
        status="nao_atendido",
        evidence=[],
        deduction_type="sem_evidencia",
        certainty="alta",
        justification=justification,
    )


def sanitize_verdicts(
    raw: Sequence[RawVerdict], requirements: Sequence[Requirement], resume_text: str
) -> list[Verdict]:
    """Aplica as regras do data-model: evidência literal, sem evidência e um veredito por requisito."""
    full_text = _norm(resume_text)
    by_id: dict[str, RawVerdict] = {}
    for verdict in raw:
        by_id.setdefault(verdict.requirement_id, verdict)

    verdicts: list[Verdict] = []
    for requirement in requirements:
        model = by_id.get(requirement.id)
        if model is None:
            verdicts.append(_without_evidence(requirement.id))
            continue
        evidence: list[str] = []
        for excerpt in model.evidence:
            clean = _norm(excerpt)
            if clean and clean in full_text and clean not in evidence:
                evidence.append(clean)
        evidence = evidence[:MAX_EVIDENCE]
        if not evidence:
            # sem trecho verificável não há como sustentar o requisito (FR-010)
            keep = model.justification if model.status == "nao_atendido" else ""
            verdicts.append(_without_evidence(requirement.id, keep))
            continue
        deduction = "termo_relacionado" if model.deduction_type == "sem_evidencia" else model.deduction_type
        verdicts.append(
            Verdict(
                requirement_id=requirement.id,
                status=model.status,
                evidence=evidence,
                deduction_type=deduction,
                certainty=model.certainty,
                justification=model.justification,
            )
        )
    return verdicts


def merge_chunk_verdicts(
    per_chunk: Sequence[Sequence[Verdict]], requirements: Sequence[Requirement]
) -> list[Verdict]:
    """Vale o melhor status (atendido > parcial > não atendido); em empate, o bloco mais cedo."""
    merged: list[Verdict] = []
    for requirement in requirements:
        found = [
            verdict for chunk in per_chunk for verdict in chunk if verdict.requirement_id == requirement.id
        ]
        if not found:
            merged.append(_without_evidence(requirement.id))
            continue
        best = max(_RANK[v.status] for v in found)
        winners = [v for v in found if _RANK[v.status] == best]
        evidence: list[str] = []
        for verdict in winners:
            for excerpt in verdict.evidence:
                if excerpt not in evidence:
                    evidence.append(excerpt)
        merged.append(winners[0].model_copy(update={"evidence": evidence[:MAX_EVIDENCE]}))
    return merged


def judge(client: LlmClient, resume: Resume, requirements: Sequence[Requirement]) -> JudgeResult:
    """Julga todos os requisitos: em uma chamada, ou por blocos quando o currículo é muito longo."""
    if needs_chunking(resume.text):
        chunks = chunk_text(resume.text)
        outputs = [client.match_requirements(c.text, requirements, (c.index, len(chunks))) for c in chunks]
    else:
        outputs = [client.match_requirements(resume.text, requirements, None)]

    per_chunk = [sanitize_verdicts(o.verdicts, requirements, resume.text) for o in outputs]
    verdicts = per_chunk[0] if len(per_chunk) == 1 else merge_chunk_verdicts(per_chunk, requirements)
    languages = Counter(o.document_check.language for o in outputs)
    return JudgeResult(
        verdicts=verdicts,
        language=languages.most_common(1)[0][0],
        looks_like_resume=any(o.document_check.looks_like_resume for o in outputs),
    )
