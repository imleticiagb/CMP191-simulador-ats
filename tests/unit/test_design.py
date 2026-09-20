"""Nota de Design: critérios da rubrica sobre as métricas do PDF."""

from __future__ import annotations

from ats.analysis.design import design_score
from ats.domain.models import PdfMeta


def _meta(**over) -> PdfMeta:
    base = {
        "file_name": "cv.pdf",
        "pages": 1,
        "size_bytes": 1000,
        "font_families": 2,
        "body_font_size_range": (10.0, 16.0),
        "body_font_size_median": 10.5,
        "min_margin_cm": 1.8,
        "text_density": 0.4,
        "has_full_page_image": False,
        "column_count": 1,
    }
    base.update(over)
    return PdfMeta(**base)


def _points(meta) -> dict[str, float]:
    return {c.id: c.points_earned for c in design_score(meta).criteria}


def test_without_pdf_the_category_is_not_evaluated():
    score = design_score(None)
    assert score.category == "design" and not score.evaluated and score.score is None
    assert score.not_evaluated_key == "category.design.not_evaluated_reason"


def test_ideal_pdf_scores_100():
    score = design_score(_meta())
    assert score.evaluated and score.score == 100
    assert sum(c.points_max for c in score.criteria) == 100


def test_pages_25_12_0():
    assert _points(_meta(pages=1))["pages"] == 25
    assert _points(_meta(pages=2))["pages"] == 25
    assert _points(_meta(pages=3))["pages"] == 12
    assert _points(_meta(pages=4))["pages"] == 0


def test_fonts_20_10_0():
    assert _points(_meta(font_families=3))["fonts"] == 20
    assert _points(_meta(font_families=4))["fonts"] == 10
    assert _points(_meta(font_families=5))["fonts"] == 0


def test_body_size_between_9_and_12():
    assert _points(_meta(body_font_size_median=9.0))["body_size"] == 20
    assert _points(_meta(body_font_size_median=12.0))["body_size"] == 20
    assert _points(_meta(body_font_size_median=8.9))["body_size"] == 0
    assert _points(_meta(body_font_size_median=12.1))["body_size"] == 0


def test_margins_at_least_one_centimeter():
    assert _points(_meta(min_margin_cm=1.0))["margins"] == 15
    assert _points(_meta(min_margin_cm=0.9))["margins"] == 0


def test_selectable_text_and_density():
    assert _points(_meta(has_full_page_image=True))["selectable"] == 0
    assert _points(_meta(text_density=0.25))["density"] == 10
    assert _points(_meta(text_density=0.75))["density"] == 10
    assert _points(_meta(text_density=0.2))["density"] == 0
    assert _points(_meta(text_density=0.8))["density"] == 0


def test_partial_levels_use_the_partial_explanation_key():
    by_id = {c.id: c for c in design_score(_meta(pages=3, font_families=4)).criteria}
    assert by_id["pages"].explanation_key == "criterion.pages.partial"
    assert by_id["fonts"].explanation_key == "criterion.fonts.partial"
    assert by_id["pages"].explanation_params["pages"] == 3
