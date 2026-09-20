"""FR-022 e FR-026: corações decorativos, ignorados por leitores de tela e independentes da fonte."""

from __future__ import annotations

import re

from ats.config import UI_LANGUAGES
from ats.i18n import load
from ats.ui.components.hearts import heart_data_uri, heart_svg, hearts_row
from ats.ui.components.result_view import render_category_html, render_overall_html
from ats.ui.theme import build_css

HEART_GLYPHS = "♥❤💗💖💕♡"


def test_every_heart_svg_is_aria_hidden():
    for html in (heart_svg(), hearts_row(5)):
        svgs = re.findall(r"<svg[^>]*>", html)
        assert svgs and all('aria-hidden="true"' in s and 'focusable="false"' in s for s in svgs)
    assert 'aria-hidden="true"' in hearts_row()


def test_header_row_has_five_hearts_and_no_text():
    row = hearts_row(5)
    assert row.count("<svg") == 5
    assert re.sub(r"<[^>]+>", "", row).strip() == ""


def test_hearts_do_not_depend_on_the_font():
    """A Tropi Land não tem ♥: nenhum texto da interface usa símbolo de coração."""
    for lang in UI_LANGUAGES:
        for key, text in load(lang).items():
            assert not any(g in text for g in HEART_GLYPHS), f"{lang}:{key}"


def test_card_corner_heart_is_a_css_background_image():
    css = build_css()
    assert ".ats-card::after" in css and "data:image/svg+xml" in css
    assert heart_data_uri().startswith("data:image/svg+xml,")


def test_result_blocks_carry_decorative_hearts_only_as_hidden_svg(read_fixture):
    from ats.analysis.llm_client import FakeLlmClient
    from ats.analysis.pipeline import analyze
    from ats.domain.models import ExtractionOutput, MatchOutput

    client = FakeLlmClient(
        extract=ExtractionOutput.model_validate_json(read_fixture("extract_ok.json")),
        match=MatchOutput.model_validate_json(read_fixture("match_ok.json")),
    )
    result = analyze(read_fixture("job_licenciatura.txt"), read_fixture("resume_licenciatura.txt"), client)
    overall = render_overall_html(result, "pt_BR")
    assert "ats-hearts" in overall and 'aria-hidden="true"' in overall
    for svg in re.findall(r"<svg[^>]*>", overall):
        assert 'aria-hidden="true"' in svg
    assert render_category_html(result.categories[0], "pt_BR").count("<svg") == 0
