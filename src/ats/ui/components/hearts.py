"""Corações decorativos em SVG (FR-022). Sempre `aria-hidden`: nunca carregam informação (FR-026)."""

from __future__ import annotations

from urllib.parse import quote

from ats.ui import tokens

HEART_PATH = "M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"


def heart_svg(color: str = tokens.PINK_500, size: int = 20) -> str:
    return (
        f'<svg class="ats-heart" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        f'width="{size}" height="{size}" aria-hidden="true" focusable="false">'
        f'<path fill="{color}" d="{HEART_PATH}"/></svg>'
    )


def heart_data_uri(color: str = tokens.PINK_300) -> str:
    """Coração como imagem de fundo para o CSS (bordas e cantos de cartões)."""
    svg = (
        f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'>"
        f"<path fill='{color}' d='{HEART_PATH}'/></svg>"
    )
    return "data:image/svg+xml," + quote(svg, safe="/:=' ")


def hearts_row(count: int = 5) -> str:
    """Fileira de corações rosa e roxos para o cabeçalho."""
    palette = [tokens.PINK_500, tokens.PURPLE_500, tokens.PINK_300, tokens.PURPLE_300, tokens.PINK_700]
    sizes = [18, 24, 30, 24, 18]
    hearts = "".join(heart_svg(palette[i % len(palette)], sizes[i % len(sizes)]) for i in range(count))
    return f'<div class="ats-hearts" aria-hidden="true">{hearts}</div>'
