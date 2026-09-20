"""FR-033: os três idiomas têm as mesmas chaves, e toda chave usada no código existe nos três."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from ats.config import UI_LANGUAGES
from ats.domain.errors import ALL_ERROR_KEYS
from ats.domain.models import Certainty, DeductionType, Importance, Kind, Status
from ats.i18n import MissingTranslation, all_keys, load, t

ROOT = Path(__file__).parent.parent.parent
USED = re.compile(r"""\bt\(\s*["']([A-Za-z0-9_.]+)["']""")


def _code_files():
    yield ROOT / "app.py"
    yield from (ROOT / "src" / "ats").rglob("*.py")


def _used_keys() -> set[str]:
    found: set[str] = set()
    for path in _code_files():
        if path.exists():
            found |= set(USED.findall(path.read_text(encoding="utf-8")))
    return found


def _literals(tp) -> tuple[str, ...]:
    return tp.__args__


def test_same_keys_in_all_languages():
    base = all_keys("pt_BR")
    for lang in UI_LANGUAGES:
        assert all_keys(lang) == base, f"chaves diferentes em {lang}"


def test_no_empty_texts():
    for lang in UI_LANGUAGES:
        empty = [k for k, v in load(lang).items() if not v.strip()]
        assert not empty, f"{lang}: {empty}"


def test_keys_used_in_code_exist_in_all_languages():
    used = _used_keys()
    for lang in UI_LANGUAGES:
        missing = sorted(used - all_keys(lang))
        assert not missing, f"{lang}: faltam {missing}"


def test_enumerated_keys_exist():
    needed = {f"status.{v}" for v in _literals(Status)}
    needed |= {f"importance.{v}" for v in _literals(Importance)}
    needed |= {f"deduction.{v}" for v in _literals(DeductionType)}
    needed |= {f"certainty.{v}" for v in _literals(Certainty)}
    needed |= {f"kind.{v}" for v in _literals(Kind)}
    needed |= {f"category.{c}" for c in ("conteudo", "estrutura", "design")}
    needed |= set(ALL_ERROR_KEYS)
    needed |= {f"lang.{lang}" for lang in UI_LANGUAGES}
    for lang in UI_LANGUAGES:
        assert not needed - all_keys(lang), f"{lang}: {sorted(needed - all_keys(lang))}"


def test_missing_key_is_an_error():
    with pytest.raises(MissingTranslation):
        t("nao.existe", lang="en")


def test_params_are_formatted():
    assert "3" in t("input.pdf.received", lang="pt_BR", name="cv.pdf", pages=3)
    assert "cv.pdf" in t("input.pdf.received", lang="es", name="cv.pdf", pages=3)
