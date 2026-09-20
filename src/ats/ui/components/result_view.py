"""Tela de resultado: nota geral, categorias com barra e justificativa, rubrica, sugestões e requisitos."""

from __future__ import annotations

from collections.abc import Mapping
from html import escape

import streamlit as st

from ats.analysis.scoring import WEIGHTS_ALL, WEIGHTS_CONTENT_ONLY, WEIGHTS_NO_DESIGN, weights_for
from ats.domain.models import AnalysisResult, CategoryScore, CriterionResult, Hint
from ats.i18n import t
from ats.ui.components.hearts import hearts_row
from ats.ui.components.requirement_card import render_requirement_card
from ats.ui.components.score_bar import render_score_bar


def _number(value: float, lang: str) -> str:
    text = str(int(value)) if float(value).is_integer() else f"{value:.1f}"
    return text.replace(".", ",") if lang != "en" else text


def explain_criterion(criterion: CriterionResult, lang: str) -> str:
    """Frase que explica um critério, por chave de modelo de texto (nunca escrita pelo modelo de IA)."""
    params = dict(criterion.explanation_params)
    if criterion.explanation_key == "criterion.requirement":
        params["importance"] = t(f"importance.{params['importance']}", lang)
        params["status"] = t(f"status.{params['status']}", lang)
        params["earned"] = _number(criterion.points_earned, lang)
        params["max"] = _number(criterion.points_max, lang)
    return t(criterion.explanation_key, lang, **params)


def resolve_hint(
    hint: Hint, result: AnalysisResult, lang: str, translations: Mapping[str, str] | None
) -> str:
    """Monta a sugestão: parâmetros `i18n:` viram texto traduzido e `req:Rn` vira o texto do requisito."""
    params: dict[str, str | int | float] = {}
    for name, value in hint.params.items():
        if isinstance(value, str) and value.startswith("i18n:"):
            params[name] = t(value[5:], lang)
        elif isinstance(value, str) and value.startswith("req:"):
            requirement = next((r for r in result.requirements if r.id == value[4:]), None)
            original = requirement.text if requirement else value[4:]
            use = translations if lang != "pt_BR" else None
            params[name] = (use or {}).get(f"{value[4:]}.text") or original
        else:
            params[name] = value
    return t(hint.key, lang, **params)


def weights_text(result: AnalysisResult, lang: str) -> str:
    evaluated = [c.category for c in result.categories if c.evaluated]
    weights = weights_for(evaluated)
    if weights is WEIGHTS_ALL:
        return t("rubric.weights", lang, content=60, structure=25, design=15)
    if weights is WEIGHTS_NO_DESIGN:
        return t("rubric.weights_no_design", lang, content=70, structure=30)
    assert weights is WEIGHTS_CONTENT_ONLY
    return t("rubric.weights_content_only", lang, content=100)


def render_overall_html(result: AnalysisResult, lang: str) -> str:
    bar = render_score_bar(result.overall, t("result.overall", lang), show_head=False)
    return (
        f'<div class="ats-card ats-overall">{hearts_row(3)}'
        f'<div class="ats-display">{escape(t("result.overall", lang))}</div>'
        f'<div class="ats-score">{result.overall}/100</div>{bar}</div>'
    )


def render_category_html(category: CategoryScore, lang: str) -> str:
    name = t(f"category.{category.category}", lang)
    bar = render_score_bar(
        category.score if category.evaluated else None,
        name,
        not_evaluated_text=t("category.not_evaluated", lang),
    )
    text = escape(t(f"category.{category.category}.desc", lang))
    if not category.evaluated and category.not_evaluated_key:
        text += " " + escape(t(category.not_evaluated_key, lang))
    return f'<div class="ats-card">{bar}<p class="ats-note">{text}</p></div>'


def render_result(
    result: AnalysisResult, lang: str = "pt_BR", translations: Mapping[str, str] | None = None
) -> None:
    st.markdown(render_overall_html(result, lang), unsafe_allow_html=True)
    for note in result.language_notes:
        job = t(f"doclang.{result.job_language or 'other'}", lang)
        resume = t(f"doclang.{result.resume_language or 'other'}", lang)
        st.info(t(note, lang, job=job, resume=resume))

    st.markdown(f"### {t('result.category_scores', lang)}")
    for category in result.categories:
        st.markdown(render_category_html(category, lang), unsafe_allow_html=True)
        if category.evaluated and category.criteria:
            with st.expander(f"{t('rubric.breakdown', lang)}: {t(f'category.{category.category}', lang)}"):
                for criterion in category.criteria:
                    mark = "✔" if criterion.passed else ("◐" if criterion.points_earned else "✖")
                    points = t(
                        "rubric.points",
                        lang,
                        earned=_number(criterion.points_earned, lang),
                        max=_number(criterion.points_max, lang),
                    )
                    st.markdown(f"- {mark} **{points}**: {explain_criterion(criterion, lang)}")

    st.markdown(f"### {t('result.how_calculated', lang)}")
    st.markdown(t("rubric.formula", lang))
    st.markdown(weights_text(result, lang))
    st.markdown(f"- {t('rubric.content', lang)}\n- {t('rubric.structure', lang)}")
    if any(c.category == "design" and c.evaluated for c in result.categories):
        st.markdown(f"- {t('rubric.design', lang)}")

    st.markdown(f"### {t('result.hints', lang)}")
    if result.improvement_hints:
        st.markdown(
            "\n".join(f"- {resolve_hint(h, result, lang, translations)}" for h in result.improvement_hints)
        )
    else:
        st.markdown(t("result.hints_none", lang))

    st.markdown(f"### {t('result.requirements', lang)}")
    for requirement in result.requirements:
        verdict = result.verdict_for(requirement.id)
        if verdict is not None:
            st.markdown(
                render_requirement_card(requirement, verdict, lang, translations), unsafe_allow_html=True
            )
