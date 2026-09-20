"""Nota geral: pesos 60/25/15 com Design e 70/30 sem, arredondamento único e decomposição."""

from __future__ import annotations

from ats.analysis.scoring import compute_overall
from ats.domain.models import CategoryScore


def _cat(name, score, evaluated=True):
    return CategoryScore(category=name, evaluated=evaluated, score=score if evaluated else None)


def test_weights_with_design_are_60_25_15():
    cats = [_cat("conteudo", 80), _cat("estrutura", 60), _cat("design", 40)]
    assert compute_overall(cats) == 69  # 48 + 15 + 6


def test_weights_without_design_are_70_30():
    cats = [_cat("conteudo", 80), _cat("estrutura", 60), _cat("design", None, evaluated=False)]
    assert compute_overall(cats) == 74  # 56 + 18


def test_rounding_happens_once_at_the_end():
    cats = [_cat("conteudo", 85), _cat("estrutura", 70), _cat("design", 55)]
    assert compute_overall(cats) == 77  # 76,75 arredonda para 77


def test_extremes():
    assert compute_overall([_cat("conteudo", 100), _cat("estrutura", 100), _cat("design", 100)]) == 100
    assert compute_overall([_cat("conteudo", 0), _cat("estrutura", 0), _cat("design", 0)]) == 0


def test_build_categories_sets_the_published_weights():
    from ats.analysis.scoring import build_categories
    from ats.domain.models import Requirement, Verdict

    reqs = [Requirement(id="R1", text="x", kind="outro", importance="obrigatorio", source_excerpt="x")]
    verdicts = [
        Verdict(
            requirement_id="R1",
            status="atendido",
            evidence=["e"],
            deduction_type="sinonimo",
            certainty="alta",
            justification="j",
        )
    ]
    without = {c.category: c.weight for c in build_categories(reqs, verdicts, "Texto do currículo", None)}
    assert without == {"conteudo": 70.0, "estrutura": 30.0, "design": 0.0}
