"""Princípio III e SC-007: nenhuma cor fora dos tokens, e contraste legível nos pares de texto e fundo."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from urllib.parse import unquote

import pytest

from ats.analysis.llm_client import FakeLlmClient
from ats.ui import tokens
from ats.ui.components.hearts import heart_data_uri, heart_svg, hearts_row
from ats.ui.components.score_bar import render_score_bar
from ats.ui.theme import build_css

ROOT = Path(__file__).parent.parent.parent
HEX = re.compile(r"#[0-9A-Fa-f]{6}\b")
ALLOWED = tokens.allowed_colors()


def _colors(text: str) -> set[str]:
    return {c.upper() for c in HEX.findall(unquote(text))}


def test_generated_css_uses_only_token_colors():
    assert _colors(build_css()) <= ALLOWED


def test_generated_html_pieces_use_only_token_colors():
    pieces = [render_score_bar(60, "x"), heart_svg(), hearts_row(), heart_data_uri()]
    for piece in pieces:
        assert _colors(piece) <= ALLOWED


def test_config_toml_uses_only_token_colors():
    config = tomllib.loads((ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8"))
    assert _colors(str(config["theme"])) <= ALLOWED


def test_no_hex_colors_in_source_outside_tokens():
    files = [ROOT / "app.py", *(ROOT / "src" / "ats").rglob("*.py")]
    offenders = {
        str(f.relative_to(ROOT)): sorted(_colors(f.read_text(encoding="utf-8")))
        for f in files
        if f.name != "tokens.py" and _colors(f.read_text(encoding="utf-8"))
    }
    assert not offenders, offenders


def test_only_pink_and_purple_are_identity_colors():
    for name, value in tokens.IDENTITY_COLORS.items():
        r, g, b = tokens.hex_to_rgb(value)
        if name in ("white", "ink"):
            continue
        assert name.startswith(("pink_", "purple_")), name
        # rosa: vermelho domina o verde; roxo: azul domina o verde
        assert g < r or g < b, f"{name} não parece rosa ou roxo"
    assert set(tokens.IDENTITY_COLORS) >= {"pink_500", "purple_700", "ink"}


@pytest.mark.parametrize(("fg", "bg"), tokens.TEXT_BACKGROUND_PAIRS)
def test_text_and_background_pairs_have_contrast_of_at_least_4_5(fg, bg):
    assert tokens.contrast_ratio(fg, bg) >= 4.5, (fg, bg)


def test_accent_gradient_goes_from_light_to_deep():
    colors = tokens.accent_segment_colors()
    assert len(colors) == 20 == tokens.BAR_SEGMENTS
    lum = [tokens._luminance(c) for c in colors]
    assert lum == sorted(lum, reverse=True), "cada segmento é mais intenso que o anterior"
    assert FakeLlmClient  # importado só para garantir que os módulos carregam juntos
