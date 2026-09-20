"""Regras de validação dos vereditos (data-model.md) e reunião de blocos de currículo."""

from __future__ import annotations

from ats.analysis.matcher import merge_chunk_verdicts, sanitize_verdicts
from ats.domain.models import RawVerdict, Requirement, Verdict

RESUME = "Atendente por 3 anos.\nLicenciatura em Letras, concluída em 2021.\n  Excel   e Word."


def _req(i: int, importance: str = "obrigatorio") -> Requirement:
    return Requirement(
        id=f"R{i}", text=f"Requisito {i}", kind="outro", importance=importance, source_excerpt="x"
    )


def _raw(i: int, status="atendido", evidence=None, deduction="correspondencia_exata", justification="ok"):
    return RawVerdict(
        requirement_id=f"R{i}",
        status=status,
        evidence=evidence if evidence is not None else [],
        deduction_type=deduction,
        certainty="alta",
        justification=justification,
    )


def test_evidence_must_be_a_literal_substring_after_normalization():
    raw = [_raw(1, evidence=["Licenciatura em Letras, concluída em 2021.", "Texto inventado pelo modelo"])]
    [verdict] = sanitize_verdicts(raw, [_req(1)], RESUME)
    assert verdict.evidence == ["Licenciatura em Letras, concluída em 2021."]
    assert verdict.status == "atendido"


def test_whitespace_differences_are_ignored_when_checking_evidence():
    raw = [_raw(1, evidence=["Excel e Word."])]
    [verdict] = sanitize_verdicts(raw, [_req(1)], RESUME)
    assert verdict.evidence == ["Excel e Word."]


def test_no_verified_evidence_becomes_not_met_without_evidence():
    raw = [_raw(1, status="atendido", evidence=["Frase que não existe no currículo"])]
    [verdict] = sanitize_verdicts(raw, [_req(1)], RESUME)
    assert verdict.status == "nao_atendido"
    assert verdict.deduction_type == "sem_evidencia"
    assert verdict.evidence == []
    assert not verdict.has_evidence


def test_partial_without_evidence_is_also_downgraded():
    [verdict] = sanitize_verdicts([_raw(1, status="parcial", evidence=[])], [_req(1)], RESUME)
    assert (verdict.status, verdict.deduction_type) == ("nao_atendido", "sem_evidencia")


def test_missing_verdict_is_created_as_not_met():
    verdicts = sanitize_verdicts([_raw(1, evidence=["Excel e Word."])], [_req(1), _req(2)], RESUME)
    assert [v.requirement_id for v in verdicts] == ["R1", "R2"]
    assert (verdicts[1].status, verdicts[1].deduction_type) == ("nao_atendido", "sem_evidencia")


def test_verdicts_for_unknown_requirements_are_ignored_and_evidence_is_capped():
    raw = [_raw(9, evidence=["Excel e Word."]), _raw(1, evidence=["Atendente por 3 anos."] * 5)]
    verdicts = sanitize_verdicts(raw, [_req(1)], RESUME)
    assert [v.requirement_id for v in verdicts] == ["R1"]
    assert len(verdicts[0].evidence) <= 3


def _v(i, status, evidence, justification="j"):
    return Verdict(
        requirement_id=f"R{i}",
        status=status,
        evidence=evidence,
        deduction_type="sem_evidencia" if status == "nao_atendido" else "sinonimo",
        certainty="media",
        justification=justification,
    )


def test_merge_prefers_met_over_partial_over_not_met():
    chunks = [
        [_v(1, "parcial", ["a"]), _v(2, "nao_atendido", [])],
        [_v(1, "atendido", ["b"]), _v(2, "parcial", ["c"])],
    ]
    merged = {v.requirement_id: v for v in merge_chunk_verdicts(chunks, [_req(1), _req(2)])}
    assert merged["R1"].status == "atendido"
    assert merged["R2"].status == "parcial"


def test_merge_tie_keeps_earliest_chunk_and_unions_evidence():
    chunks = [
        [_v(1, "atendido", ["a"], justification="primeiro")],
        [_v(1, "atendido", ["b"], justification="segundo")],
    ]
    [merged] = merge_chunk_verdicts(chunks, [_req(1)])
    assert merged.justification == "primeiro"
    assert merged.evidence == ["a", "b"]
