"""Barra de progresso segmentada (HTML/CSS): 20 segmentos, acessível e sem depender só da cor."""

from __future__ import annotations

import re

import pytest

from ats.ui import tokens
from ats.ui.components.score_bar import filled_segments, render_score_bar


@pytest.mark.parametrize(
    ("value", "expected"), [(0, 0), (2, 0), (3, 1), (50, 10), (85, 17), (88, 18), (98, 20), (100, 20)]
)
def test_filled_segments_is_value_over_5_rounded(value, expected):
    assert filled_segments(value) == expected


def test_renders_20_segments_with_the_right_number_filled():
    html = render_score_bar(85, "Conteúdo")
    assert html.count('class="ats-seg') == 20
    assert html.count('class="ats-seg on"') == 17


def test_is_an_accessible_progressbar_with_the_number_beside_it():
    html = render_score_bar(85, "Conteúdo")
    assert 'role="progressbar"' in html
    assert 'aria-valuenow="85"' in html and 'aria-valuemin="0"' in html and 'aria-valuemax="100"' in html
    assert 'aria-label="Conteúdo: 85/100"' in html
    assert "85/100" in html


def test_filled_segments_go_from_light_to_deep_accent():
    html = render_score_bar(100, "Geral")
    colors = re.findall(r"background:(#[0-9A-Fa-f]{6})", html)
    assert colors == tokens.accent_segment_colors()
    assert colors[0].upper() == tokens.ACCENT_LIGHT and colors[-1].upper() == tokens.ACCENT_DEEP


def test_only_allowed_colors_appear():
    found = {c.upper() for c in re.findall(r"#[0-9A-Fa-f]{6}", render_score_bar(60, "x"))}
    assert found <= tokens.allowed_colors()


def test_not_evaluated_category_is_an_empty_bar_with_text():
    html = render_score_bar(None, "Design", not_evaluated_text="não avaliada")
    assert 'class="ats-seg on"' not in html
    assert "não avaliada" in html
    assert 'role="progressbar"' not in html, "sem nota não há barra de progresso"
    assert 'aria-label="Design: não avaliada"' in html


def test_label_is_escaped():
    assert "<script>" not in render_score_bar(10, "<script>alert(1)</script>")


def test_head_can_be_hidden_for_the_overall_bar():
    html = render_score_bar(85, "Nota geral", show_head=False)
    assert 'class="ats-bar-head"' not in html and 'role="progressbar"' in html
