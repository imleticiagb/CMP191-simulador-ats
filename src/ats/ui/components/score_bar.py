"""Barra de progresso segmentada em HTML/CSS (FR-017).

20 segmentos de 5 pontos, em gradiente de uma única cor de acento (do claro ao intenso). A nota sempre vem
com o valor numérico ao lado e com `role="progressbar"`: a informação nunca depende só da cor.
Esta é a única exceção de cor do Princípio III (escala de dados), usada só aqui.
"""

from __future__ import annotations

from html import escape

from ats.ui import tokens

SEGMENTS = tokens.BAR_SEGMENTS
POINTS_PER_SEGMENT = 100 // SEGMENTS


def filled_segments(value: int) -> int:
    """Segmentos preenchidos: nota dividida por 5, arredondada para cima no meio."""
    return max(0, min(SEGMENTS, (value + POINTS_PER_SEGMENT // 2) // POINTS_PER_SEGMENT))


def render_score_bar(
    value: int | None,
    label: str,
    *,
    not_evaluated_text: str = "",
    show_head: bool = True,
) -> str:
    safe_label = escape(label, quote=True)
    if value is None:
        text = escape(not_evaluated_text, quote=True)
        head = (
            f'<div class="ats-bar-head"><span class="ats-bar-label">{safe_label}</span>'
            f'<span class="ats-bar-value">{text}</span></div>'
            if show_head
            else ""
        )
        segments = '<span class="ats-seg"></span>' * SEGMENTS
        return (
            f'<div class="ats-bar-wrap">{head}'
            f'<div class="ats-bar empty" role="img" aria-label="{safe_label}: {text}">{segments}</div></div>'
        )

    filled = filled_segments(value)
    colors = tokens.accent_segment_colors()
    segments = "".join(
        f'<span class="ats-seg on" style="background:{colors[i]}"></span>'
        if i < filled
        else '<span class="ats-seg"></span>'
        for i in range(SEGMENTS)
    )
    head = (
        f'<div class="ats-bar-head"><span class="ats-bar-label">{safe_label}</span>'
        f'<span class="ats-bar-value">{value}/100</span></div>'
        if show_head
        else ""
    )
    return (
        f'<div class="ats-bar-wrap">{head}'
        f'<div class="ats-bar" role="progressbar" aria-valuenow="{value}" aria-valuemin="0" aria-valuemax="100" '
        f'aria-label="{safe_label}: {value}/100">{segments}</div></div>'
    )
