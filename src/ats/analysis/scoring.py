"""Rubrica `rubric-1`: toda a pontuação é calculada aqui, em código, a partir dos vereditos (Princípio I)."""

from __future__ import annotations

from collections.abc import Sequence
from fractions import Fraction

from ats.analysis.design import design_score
from ats.analysis.structure import structure_score
from ats.domain.models import (
    CategoryName,
    CategoryScore,
    CriterionResult,
    Hint,
    PdfMeta,
    Requirement,
    Verdict,
)

IMPORTANCE_WEIGHT = {"obrigatorio": 2, "desejavel": 1}
STATUS_CREDIT = {"atendido": Fraction(1), "parcial": Fraction(1, 2), "nao_atendido": Fraction(0)}

WEIGHTS_ALL = {"conteudo": 60, "estrutura": 25, "design": 15}
WEIGHTS_NO_DESIGN = {"conteudo": 70, "estrutura": 30}
WEIGHTS_CONTENT_ONLY = {"conteudo": 100}


def round_half_up(value: float | Fraction) -> int:
    """Arredonda meio para cima, sem erro de ponto flutuante."""
    exact = Fraction(value).limit_denominator(10**9)
    return int((exact + Fraction(1, 2)).__floor__())


def content_score(requirements: Sequence[Requirement], verdicts: Sequence[Verdict]) -> CategoryScore:
    """Conteúdo: soma ponderada dos créditos por requisito (obrigatório vale 2, desejável vale 1)."""
    by_id = {v.requirement_id: v for v in verdicts}
    criteria: list[CriterionResult] = []
    earned_total, max_total = Fraction(0), Fraction(0)
    for requirement in requirements:
        verdict = by_id[requirement.id]
        weight = IMPORTANCE_WEIGHT[requirement.importance]
        earned = STATUS_CREDIT[verdict.status] * weight
        earned_total += earned
        max_total += weight
        criteria.append(
            CriterionResult(
                id=requirement.id,
                points_earned=float(earned),
                points_max=float(weight),
                explanation_key="criterion.requirement",
                explanation_params={
                    "id": requirement.id,
                    "importance": requirement.importance,
                    "status": verdict.status,
                },
            )
        )
    score = round_half_up(100 * earned_total / max_total) if max_total else 0
    return CategoryScore(
        category="conteudo",
        evaluated=True,
        score=score,
        criteria=criteria,
    )


def weights_for(categories: Sequence[CategoryName]) -> dict[str, int]:
    present = set(categories)
    if {"conteudo", "estrutura", "design"} <= present:
        return WEIGHTS_ALL
    if {"conteudo", "estrutura"} <= present:
        return WEIGHTS_NO_DESIGN
    return WEIGHTS_CONTENT_ONLY


def compute_overall(categories: Sequence[CategoryScore]) -> int:
    """Média ponderada das categorias avaliadas, arredondada uma única vez."""
    evaluated = [c for c in categories if c.evaluated and c.score is not None]
    weights = weights_for([c.category for c in evaluated])
    total = sum(weights[c.category] for c in evaluated)
    return round_half_up(Fraction(sum(weights[c.category] * c.score for c in evaluated), total))


def build_categories(
    requirements: Sequence[Requirement],
    verdicts: Sequence[Verdict],
    resume_text: str,
    pdf_meta: PdfMeta | None,
) -> list[CategoryScore]:
    """Conteúdo, Estrutura e Design, já com os pesos publicados (60/25/15, ou 70/30 sem Design)."""
    categories = [
        content_score(requirements, verdicts),
        structure_score(resume_text),
        design_score(pdf_meta),
    ]
    weights = weights_for([c.category for c in categories if c.evaluated])
    return [
        c.model_copy(update={"weight": float(weights[c.category]) if c.evaluated else 0.0})
        for c in categories
    ]


# --- Sugestões de melhoria (FR-018): só para nota abaixo do limiar, por modelo de texto do i18n ---
HINT_THRESHOLD = 70
MAX_HINTS_PER_CATEGORY = 3

_STRUCTURE_HINTS = {
    "email": ("hint.add_contact", {"item": "i18n:contact.email"}),
    "phone": ("hint.add_contact", {"item": "i18n:contact.phone"}),
    "section_experience": ("hint.add_section", {"section": "i18n:section.experience"}),
    "section_education": ("hint.add_section", {"section": "i18n:section.education"}),
    "section_skills": ("hint.add_section", {"section": "i18n:section.skills"}),
    "section_summary": ("hint.add_section", {"section": "i18n:section.summary"}),
    "dates": ("hint.add_dates", {}),
    "length": ("hint.length", {}),
}
_DESIGN_HINTS = {
    "pages": "hint.design_pages",
    "fonts": "hint.design_fonts",
    "body_size": "hint.design_size",
    "margins": "hint.design_margins",
    "selectable": "hint.design_selectable",
    "density": "hint.design_density",
}


def _lost(criterion: CriterionResult) -> float:
    return criterion.points_max - criterion.points_earned


def build_hints(
    categories: Sequence[CategoryScore], requirements: Sequence[Requirement], verdicts: Sequence[Verdict]
) -> list[Hint]:
    by_id = {v.requirement_id: v for v in verdicts}
    hints: list[Hint] = []
    for category in categories:
        if not category.evaluated or category.score is None or category.score >= HINT_THRESHOLD:
            continue
        if category.category == "conteudo":
            unmet = [r for r in requirements if by_id[r.id].status != "atendido"]
            unmet.sort(key=lambda r: 0 if r.importance == "obrigatorio" else 1)
            for requirement in unmet[:MAX_HINTS_PER_CATEGORY]:
                hints.append(
                    Hint(
                        key="hint.show_requirement",
                        params={"requirement": f"req:{requirement.id}"},
                        category="conteudo",
                    )
                )
        else:
            failed = sorted((c for c in category.criteria if _lost(c) > 0), key=_lost, reverse=True)
            for criterion in failed[:MAX_HINTS_PER_CATEGORY]:
                if category.category == "estrutura":
                    key, params = _STRUCTURE_HINTS[criterion.id]
                else:
                    key, params = _DESIGN_HINTS[criterion.id], {}
                hints.append(Hint(key=key, params=dict(params), category=category.category))
    return hints
