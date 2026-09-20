"""Nota de Conteúdo (rubrica rubric-1) e cálculo da nota geral."""

from __future__ import annotations

from ats.analysis.scoring import compute_overall, content_score, round_half_up
from ats.domain.models import CategoryScore, Requirement, Verdict


def _req(i, importance):
    return Requirement(id=f"R{i}", text=f"r{i}", kind="outro", importance=importance, source_excerpt="x")


def _ver(i, status):
    return Verdict(
        requirement_id=f"R{i}",
        status=status,
        evidence=[] if status == "nao_atendido" else ["e"],
        deduction_type="sem_evidencia" if status == "nao_atendido" else "sinonimo",
        certainty="alta",
        justification="j",
    )


def test_round_half_up():
    assert [round_half_up(x) for x in (0.5, 1.5, 84.5, 85.49, 100)] == [1, 2, 85, 85, 100]


def test_weights_and_credits():
    reqs = [_req(1, "obrigatorio"), _req(2, "obrigatorio"), _req(3, "obrigatorio"), _req(4, "desejavel")]
    verdicts = [_ver(1, "atendido"), _ver(2, "atendido"), _ver(3, "atendido"), _ver(4, "nao_atendido")]
    score = content_score(reqs, verdicts)
    assert score.category == "conteudo" and score.evaluated
    assert score.score == 86  # 6 de 7 pontos = 85,71
    assert len(score.criteria) == 4
    assert sum(c.points_earned for c in score.criteria) == 6
    assert sum(c.points_max for c in score.criteria) == 7


def test_partial_counts_half_and_required_counts_double():
    reqs = [_req(1, "obrigatorio"), _req(2, "desejavel")]
    verdicts = [_ver(1, "parcial"), _ver(2, "atendido")]
    # (2*0,5 + 1*1) / 3 = 66,67
    assert content_score(reqs, verdicts).score == 67


def test_all_met_is_100_and_none_met_is_0():
    reqs = [_req(1, "obrigatorio"), _req(2, "desejavel")]
    assert content_score(reqs, [_ver(1, "atendido"), _ver(2, "atendido")]).score == 100
    assert content_score(reqs, [_ver(1, "nao_atendido"), _ver(2, "nao_atendido")]).score == 0


def test_overall_equals_content_when_only_content_is_evaluated():
    only = [CategoryScore(category="conteudo", evaluated=True, score=86)]
    assert compute_overall(only) == 86


def test_score_is_recomputable_from_verdicts_only():
    reqs = [_req(1, "obrigatorio"), _req(2, "desejavel")]
    verdicts = [_ver(1, "atendido"), _ver(2, "parcial")]
    first = content_score(reqs, verdicts)
    second = content_score(list(reversed(reqs)), list(reversed(verdicts)))
    assert first.score == second.score == 83
