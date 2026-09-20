"""Nota de Design (0 a 100): só existe para PDF, com base nas métricas do próprio arquivo."""

from __future__ import annotations

from ats.domain.models import CategoryScore, CriterionResult, PdfMeta

POINTS = {"pages": 25, "fonts": 20, "body_size": 20, "margins": 15, "selectable": 10, "density": 10}
BODY_SIZE_RANGE = (9.0, 12.0)
MIN_MARGIN_CM = 1.0
DENSITY_RANGE = (0.25, 0.75)


def _criterion(cid: str, earned: float, level: str, **params) -> CriterionResult:
    return CriterionResult(
        id=cid,
        points_earned=float(earned),
        points_max=float(POINTS[cid]),
        explanation_key=f"criterion.{cid}.{level}",
        explanation_params=params,
    )


def design_score(meta: PdfMeta | None) -> CategoryScore:
    if meta is None:
        return CategoryScore(
            category="design",
            evaluated=False,
            not_evaluated_key="category.design.not_evaluated_reason",
        )
    criteria: list[CriterionResult] = []

    if meta.pages <= 2:
        criteria.append(_criterion("pages", 25, "pass", pages=meta.pages))
    elif meta.pages == 3:
        criteria.append(_criterion("pages", 12, "partial", pages=meta.pages))
    else:
        criteria.append(_criterion("pages", 0, "fail", pages=meta.pages))

    if meta.font_families <= 3:
        criteria.append(_criterion("fonts", 20, "pass", fonts=meta.font_families))
    elif meta.font_families == 4:
        criteria.append(_criterion("fonts", 10, "partial", fonts=meta.font_families))
    else:
        criteria.append(_criterion("fonts", 0, "fail", fonts=meta.font_families))

    size = round(meta.body_font_size_median, 1)
    ok_size = BODY_SIZE_RANGE[0] <= meta.body_font_size_median <= BODY_SIZE_RANGE[1]
    criteria.append(_criterion("body_size", 20 if ok_size else 0, "pass" if ok_size else "fail", size=size))

    ok_margin = meta.min_margin_cm >= MIN_MARGIN_CM
    criteria.append(
        _criterion(
            "margins",
            15 if ok_margin else 0,
            "pass" if ok_margin else "fail",
            margin=round(meta.min_margin_cm, 1),
        )
    )

    ok_text = not meta.has_full_page_image
    criteria.append(_criterion("selectable", 10 if ok_text else 0, "pass" if ok_text else "fail"))

    ok_density = DENSITY_RANGE[0] <= meta.text_density <= DENSITY_RANGE[1]
    criteria.append(
        _criterion(
            "density",
            10 if ok_density else 0,
            "pass" if ok_density else "fail",
            density=round(100 * meta.text_density),
        )
    )

    score = int(sum(c.points_earned for c in criteria))
    return CategoryScore(category="design", evaluated=True, score=score, criteria=criteria)
