"""Fonte única de cores e fontes (Princípio III). Nenhuma cor hexadecimal pode aparecer fora deste arquivo.

Rosa e roxo são as únicas cores de identidade. `ACCENT_*` é a escala de dados da barra de progresso
(exceção 1 do Princípio III) e nunca é usada em outro elemento. As bandeiras são imagens (exceção 2).
"""

from __future__ import annotations

# --- Rosa ---
PINK_50 = "#FFF0F6"
PINK_100 = "#FFE0EE"
PINK_300 = "#F9A8D4"
PINK_500 = "#EC4899"
PINK_700 = "#BE185D"

# --- Roxo ---
PURPLE_50 = "#F5F0FF"
PURPLE_100 = "#EBDDFF"
PURPLE_300 = "#C4A7F5"
PURPLE_500 = "#8B5CF6"
PURPLE_700 = "#6D28D9"
PURPLE_900 = "#3B0F70"

# --- Neutros de apoio ---
WHITE = "#FFFFFF"
INK = "#2D0B55"  # texto principal (roxo muito escuro)

# --- Escala de dados da barra de progresso: turquesa/verde-água, do claro ao intenso ---
ACCENT_LIGHT = "#CDF3EC"
ACCENT_DEEP = "#0B6B62"

# --- Fontes, com alternativas legíveis (FR-023, FR-024) ---
FONT_DISPLAY = '"Tropi Land", "Trebuchet MS", "Segoe UI", sans-serif'
FONT_BODY = 'Lora, Georgia, "Times New Roman", serif'
FONT_DISPLAY_NAME = "Tropi Land"
FONT_BODY_NAME = "Lora"

BAR_SEGMENTS = 20


def hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def rgb_to_hex(rgb: tuple[float, float, float]) -> str:
    r, g, b = (max(0, min(255, round(c))) for c in rgb)
    return f"#{r:02X}{g:02X}{b:02X}"


def lerp_color(start: str, end: str, t: float) -> str:
    a, b = hex_to_rgb(start), hex_to_rgb(end)
    return rgb_to_hex(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))  # type: ignore[arg-type]


def accent_segment_colors(n: int = BAR_SEGMENTS) -> list[str]:
    """Cor de cada segmento da barra, do tom claro (primeiro) ao intenso (último)."""
    return [lerp_color(ACCENT_LIGHT, ACCENT_DEEP, i / (n - 1)) for i in range(n)]


IDENTITY_COLORS = {
    "pink_50": PINK_50,
    "pink_100": PINK_100,
    "pink_300": PINK_300,
    "pink_500": PINK_500,
    "pink_700": PINK_700,
    "purple_50": PURPLE_50,
    "purple_100": PURPLE_100,
    "purple_300": PURPLE_300,
    "purple_500": PURPLE_500,
    "purple_700": PURPLE_700,
    "purple_900": PURPLE_900,
    "white": WHITE,
    "ink": INK,
}


def allowed_colors() -> set[str]:
    """Todas as cores que podem aparecer no CSS e no HTML gerados (em maiúsculas)."""
    colors = set(IDENTITY_COLORS.values()) | {ACCENT_LIGHT, ACCENT_DEEP} | set(accent_segment_colors())
    return {c.upper() for c in colors}


def _luminance(color: str) -> float:
    def channel(v: int) -> float:
        s = v / 255
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(v) for v in hex_to_rgb(color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(foreground: str, background: str) -> float:
    """Razão de contraste WCAG entre duas cores."""
    a, b = _luminance(foreground), _luminance(background)
    lighter, darker = max(a, b), min(a, b)
    return (lighter + 0.05) / (darker + 0.05)


# Pares de texto e fundo usados na interface (SC-007: contraste mínimo de 4,5:1)
TEXT_BACKGROUND_PAIRS = [
    (INK, PINK_50),
    (INK, WHITE),
    (INK, PURPLE_50),
    (INK, PINK_100),
    (WHITE, PURPLE_700),
    (PURPLE_700, WHITE),
    (PURPLE_700, PINK_50),
    (PINK_700, WHITE),
    (PINK_700, PINK_50),
    (PURPLE_900, PURPLE_100),
]
