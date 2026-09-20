"""Cartão de um requisito: importância, status, evidência, dedução e justificativa (FR-007 a FR-011)."""

from __future__ import annotations

from collections.abc import Mapping
from html import escape

from ats.domain.models import Requirement, Verdict
from ats.i18n import t

STATUS_ICON = {"atendido": "✔", "parcial": "◐", "nao_atendido": "✖"}


def _pick(translations: Mapping[str, str] | None, key: str, original: str) -> str:
    return (translations or {}).get(key) or original


def render_requirement_card(
    requirement: Requirement,
    verdict: Verdict,
    lang: str = "pt_BR",
    translations: Mapping[str, str] | None = None,
) -> str:
    """HTML do cartão. Todo texto vindo do usuário ou do modelo é escapado."""
    use = translations if lang != "pt_BR" else None
    title = escape(_pick(use, f"{requirement.id}.text", requirement.text))
    status = verdict.status
    badges = [
        f'<span class="ats-badge">{escape(t(f"importance.{requirement.importance}", lang))}</span>',
        f'<span class="ats-badge status-{status}"><span aria-hidden="true">{STATUS_ICON[status]}</span> '
        f"{escape(t(f'status.{status}', lang))}</span>",
    ]
    if verdict.certainty == "baixa":
        badges.append(f'<span class="ats-badge">{escape(t("result.uncertain", lang))}</span>')

    parts = [f'<div class="ats-card"><h4>{title}</h4><div>{"".join(badges)}</div>']
    parts.append(
        f'<p class="ats-note"><b>{escape(t("result.deduction", lang))}:</b> '
        f"{escape(t(f'deduction.{verdict.deduction_type}', lang))} · "
        f"{escape(t(f'certainty.{verdict.certainty}', lang))}</p>"
    )
    if verdict.has_evidence:
        parts.append(f'<p class="ats-note"><b>{escape(t("result.evidence", lang))}:</b></p>')
        parts += [f'<div class="ats-quote">“{escape(e)}”</div>' for e in verdict.evidence]
    else:
        parts.append(f"<p><b>{escape(t('result.no_evidence', lang))}</b></p>")
    justification = _pick(use, f"{requirement.id}.justification", verdict.justification)
    if justification:
        parts.append(f"<p>{escape(justification)}</p>")
    parts.append("</div>")
    return "".join(parts)
