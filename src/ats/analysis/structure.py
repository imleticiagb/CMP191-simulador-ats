"""Nota de Estrutura (0 a 100): regras simples e publicadas sobre o texto do currículo."""

from __future__ import annotations

import re
import unicodedata

from ats.domain.models import CategoryScore, CriterionResult

CRITERION_POINTS = {
    "email": 10,
    "phone": 10,
    "section_experience": 20,
    "section_education": 20,
    "section_skills": 15,
    "section_summary": 10,
    "dates": 10,
    "length": 5,
}
MIN_WORDS, MAX_WORDS = 250, 1200

SECTION_TERMS = {
    "experience": [
        "experiencia",
        "experiencia profissional",
        "historico profissional",
        "experience",
        "work experience",
        "employment",
        "experiencia laboral",
    ],
    "education": [
        "formacao",
        "formacao academica",
        "educacao",
        "escolaridade",
        "education",
        "academic background",
        "formacion",
        "educacion",
        "estudios",
    ],
    "skills": [
        "habilidades",
        "competencias",
        "conhecimentos",
        "skills",
        "technical skills",
        "conocimientos",
    ],
    "summary": [
        "resumo",
        "perfil",
        "objetivo",
        "sobre mim",
        "summary",
        "profile",
        "objective",
        "about",
        "resumen",
    ],
}
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_PHONE = re.compile(r"\+?\d[\d\s().-]{6,}\d")
_YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
_YEAR_RANGE = re.compile(r"^(?:19|20)\d{2}\D+(?:19|20)\d{2}$")
_HEADING_MAX_CHARS = 40


def _fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


def _heading_of(line: str) -> str | None:
    stripped = line.strip()
    if not stripped or len(stripped) > _HEADING_MAX_CHARS:
        return None
    folded = re.sub(r"[^\w\s]", "", _fold(stripped)).strip()
    for section, terms in SECTION_TERMS.items():
        if folded in terms:
            return section
    return None


def _has_phone(text: str) -> bool:
    for match in _PHONE.finditer(text):
        raw = match.group().strip()
        if _YEAR_RANGE.match(raw):
            continue
        if 8 <= len(re.sub(r"\D", "", raw)) <= 13:
            return True
    return False


def _sections(text: str) -> tuple[set[str], str]:
    """Seções encontradas e o texto da seção de experiência (até o próximo título)."""
    found: set[str] = set()
    experience: list[str] = []
    current: str | None = None
    for line in text.splitlines():
        heading = _heading_of(line)
        if heading:
            found.add(heading)
            current = heading
            continue
        if current == "experience":
            experience.append(line)
    return found, "\n".join(experience)


def structure_score(text: str) -> CategoryScore:
    sections, experience_text = _sections(text)
    words = len(text.split())
    checks: dict[str, tuple[bool, dict]] = {
        "email": (bool(_EMAIL.search(text)), {}),
        "phone": (_has_phone(text), {}),
        "section_experience": ("experience" in sections, {}),
        "section_education": ("education" in sections, {}),
        "section_skills": ("skills" in sections, {}),
        "section_summary": ("summary" in sections, {}),
        "dates": (len(_YEAR.findall(experience_text)) >= 2, {}),
        "length": (MIN_WORDS <= words <= MAX_WORDS, {"words": words}),
    }
    criteria = []
    for cid, maximum in CRITERION_POINTS.items():
        passed, params = checks[cid]
        criteria.append(
            CriterionResult(
                id=cid,
                points_earned=float(maximum if passed else 0),
                points_max=float(maximum),
                explanation_key=f"criterion.{cid}.{'pass' if passed else 'fail'}",
                explanation_params=params,
            )
        )
    score = int(sum(c.points_earned for c in criteria))
    return CategoryScore(category="estrutura", evaluated=True, score=score, criteria=criteria)
