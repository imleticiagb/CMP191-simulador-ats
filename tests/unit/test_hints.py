"""Sugestões de melhoria: só para nota abaixo de 70, até 3 por categoria, por chave de modelo i18n."""

from __future__ import annotations

from ats.analysis.scoring import HINT_THRESHOLD, build_hints
from ats.domain.models import CategoryScore, CriterionResult, Requirement, Verdict
from ats.i18n import t


def _req(i, importance="obrigatorio"):
    return Requirement(
        id=f"R{i}", text=f"requisito {i}", kind="outro", importance=importance, source_excerpt="x"
    )


def _ver(i, status):
    return Verdict(
        requirement_id=f"R{i}",
        status=status,
        evidence=[] if status == "nao_atendido" else ["e"],
        deduction_type="sem_evidencia" if status == "nao_atendido" else "sinonimo",
        certainty="alta",
        justification="",
    )


def _crit(cid, earned, maximum, key=None, **params):
    return CriterionResult(
        id=cid,
        points_earned=earned,
        points_max=maximum,
        explanation_key=key or f"criterion.{cid}.fail",
        explanation_params=params,
    )


def test_threshold_is_70():
    assert HINT_THRESHOLD == 70


def test_scores_of_70_or_more_generate_nothing():
    cats = [
        CategoryScore(category="conteudo", evaluated=True, score=70),
        CategoryScore(category="estrutura", evaluated=True, score=100),
    ]
    assert build_hints(cats, [_req(1)], [_ver(1, "nao_atendido")]) == []


def test_content_hints_are_up_to_3_required_first():
    reqs = [_req(1, "desejavel"), _req(2), _req(3), _req(4), _req(5)]
    verdicts = [_ver(i, "nao_atendido") for i in range(1, 6)]
    cats = [CategoryScore(category="conteudo", evaluated=True, score=0)]
    hints = build_hints(cats, reqs, verdicts)
    assert len(hints) == 3
    assert [h.key for h in hints] == ["hint.show_requirement"] * 3
    assert [h.params["requirement"] for h in hints] == ["req:R2", "req:R3", "req:R4"]
    assert all(h.category == "conteudo" for h in hints)


def test_structure_hints_follow_the_most_points_lost():
    criteria = [
        _crit("email", 0, 10),
        _crit("section_experience", 0, 20),
        _crit("section_education", 20, 20, "criterion.section_education.pass"),
        _crit("section_skills", 0, 15),
        _crit("dates", 0, 10),
    ]
    cats = [CategoryScore(category="estrutura", evaluated=True, score=40, criteria=criteria)]
    hints = build_hints(cats, [], [])
    assert [(h.key, h.params) for h in hints] == [
        ("hint.add_section", {"section": "i18n:section.experience"}),
        ("hint.add_section", {"section": "i18n:section.skills"}),
        ("hint.add_contact", {"item": "i18n:contact.email"}),
    ]


def test_design_hints_and_not_evaluated_design_gives_none():
    criteria = [_crit("pages", 0, 25, "criterion.pages.fail", pages=5), _crit("fonts", 0, 20)]
    cats = [CategoryScore(category="design", evaluated=True, score=10, criteria=criteria)]
    assert [h.key for h in build_hints(cats, [], [])] == ["hint.design_pages", "hint.design_fonts"]
    none = [CategoryScore(category="design", evaluated=False)]
    assert build_hints(none, [], []) == []


def test_every_hint_key_exists_in_all_languages_and_is_gentle():
    criteria = [_crit(c, 0, 10) for c in ("email", "phone", "dates", "length")]
    cats = [CategoryScore(category="estrutura", evaluated=True, score=0, criteria=criteria)]
    for hint in build_hints(cats, [], []):
        for lang in ("pt_BR", "en", "es"):
            params = {k: "x" for k in hint.params}
            assert t(hint.key, lang=lang, **params)
