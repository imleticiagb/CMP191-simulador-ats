"""SC-013: a Tropi Land mostra acentos, ñ, ¿, ¡, dígitos e pontuação, e os títulos dos três idiomas."""

from __future__ import annotations

from pathlib import Path

import pytest
from fontTools.ttLib import TTFont

from ats.config import UI_LANGUAGES
from ats.i18n import load

FONT = Path(__file__).parent.parent.parent / "static" / "fonts" / "TropiLand-Demo.ttf"
TITLE_KEYS = [
    "app.title",
    "result.overall",
    "result.category_scores",
    "result.requirements",
    "result.hints",
    "result.how_calculated",
    "input.resume.title",
    "category.conteudo",
    "category.estrutura",
    "category.design",
    "error.title",
]


@pytest.fixture(scope="module")
def cmap():
    return TTFont(FONT).getBestCmap()


def _missing(cmap, chars: str) -> str:
    return "".join(sorted({c for c in chars if not c.isspace() and ord(c) not in cmap}))


def test_accents_tilde_inverted_marks_digits_and_punctuation(cmap):
    chars = "áàâãäéèêíìîóòôõöúùûüçñÁÀÂÃÉÊÍÓÔÕÚÜÇÑ¿¡0123456789/.,:;-()%!?"
    assert not _missing(cmap, chars)


def test_score_format_is_covered(cmap):
    assert not _missing(cmap, "85/100")


@pytest.mark.parametrize("lang", UI_LANGUAGES)
def test_every_title_in_every_language_is_covered(cmap, lang):
    texts = load(lang)
    for key in TITLE_KEYS:
        assert not _missing(cmap, texts[key]), f"{lang}:{key}: {_missing(cmap, texts[key])}"
