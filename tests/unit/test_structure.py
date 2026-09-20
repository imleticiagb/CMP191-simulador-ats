"""Nota de Estrutura: critérios e pontos da rubrica (contracts/scoring-rubric.md)."""

from __future__ import annotations

import pytest

from ats.analysis.structure import CRITERION_POINTS, structure_score

PT = """Maria Souza
maria.souza@email.com | (11) 99999-0000

Resumo
Profissional dedicada ao atendimento.

Experiência Profissional
Atendente de loja (2019 a 2022)
Suporte a clientes.

Formação
Licenciatura em Pedagogia, 2022.

Habilidades
Comunicação e organização.
""" + ("palavra " * 260)

EN = """John Smith
john.smith@mail.com  +1 415 555 0100

Summary
Customer-focused professional.

Work Experience
Support agent, 2018 - 2021

Education
Bachelor of Arts, 2017

Skills
Communication
""" + ("word " * 260)

ES = """Ana Pérez
ana.perez@correo.es / 600 123 456

Resumen
Profesional dedicada.

Experiencia laboral
Recepcionista (2015 y 2020)

Formación
Grado en Turismo, 2014

Habilidades
Organización
""" + ("palabra " * 260)


def _points(score):
    return {c.id: c.points_earned for c in score.criteria}


def test_criteria_points_add_up_to_100():
    assert CRITERION_POINTS == {
        "email": 10,
        "phone": 10,
        "section_experience": 20,
        "section_education": 20,
        "section_skills": 15,
        "section_summary": 10,
        "dates": 10,
        "length": 5,
    }
    assert sum(CRITERION_POINTS.values()) == 100


@pytest.mark.parametrize("text", [PT, EN, ES], ids=["pt", "en", "es"])
def test_complete_resume_in_each_language_scores_100(text):
    score = structure_score(text)
    assert score.category == "estrutura" and score.evaluated
    assert score.score == 100, _points(score)
    assert all(c.passed for c in score.criteria)


def test_missing_items_lose_exactly_their_points():
    text = "Maria Souza\n\nExperiência\nAtendente por muito tempo.\n"
    score = structure_score(text)
    points = _points(score)
    assert points["email"] == 0 and points["phone"] == 0
    assert points["section_experience"] == 20
    assert points["section_education"] == 0 and points["section_skills"] == 0
    assert points["dates"] == 0, "sem dois anos na experiência"
    assert points["length"] == 0
    assert score.score == 20


def test_phone_needs_8_to_13_digits():
    base = "Nome\nemail@x.com\n"
    assert _points(structure_score(base + "Tel: 1234567"))["phone"] == 0
    assert _points(structure_score(base + "Tel: (11) 98765-4321"))["phone"] == 10
    assert _points(structure_score(base + "Tel: +55 11 98765-4321"))["phone"] == 10
    assert _points(structure_score(base + "Tel: 12345678901234"))["phone"] == 0


def test_dates_must_be_inside_the_experience_section():
    outside = "Experiência\nAtendente\n\nFormação\nCurso 2010 a 2014\n"
    inside = "Experiência\nAtendente 2010 a 2014\n\nFormação\nCurso\n"
    assert _points(structure_score(outside))["dates"] == 0
    assert _points(structure_score(inside))["dates"] == 10


def test_length_window_is_250_to_1200_words():
    assert _points(structure_score("palavra " * 249))["length"] == 0
    assert _points(structure_score("palavra " * 250))["length"] == 5
    assert _points(structure_score("palavra " * 1200))["length"] == 5
    assert _points(structure_score("palavra " * 1201))["length"] == 0


def test_explanations_use_pass_and_fail_keys_with_params():
    score = structure_score("Maria\n" + "palavra " * 10)
    by_id = {c.id: c for c in score.criteria}
    assert by_id["email"].explanation_key == "criterion.email.fail"
    assert by_id["length"].explanation_params["words"] == 11


def test_section_words_inside_sentences_do_not_count_as_headings():
    text = "Tenho experiência e formação em várias áreas, e habilidades diversas ao longo da carreira toda."
    points = _points(structure_score(text))
    assert points["section_experience"] == points["section_education"] == points["section_skills"] == 0
