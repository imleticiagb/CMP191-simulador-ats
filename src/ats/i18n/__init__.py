"""Textos da interface em três idiomas. O português do Brasil é o original e o padrão (FR-027).

A função `t` recebe a chave e os parâmetros e devolve o texto no idioma ativo. Chave ausente em `pt_BR`
é erro. Em outro idioma, com `ATS_STRICT_I18N=1` (testes) também é erro; fora disso cai para o português,
para não quebrar a tela.
"""

from __future__ import annotations

import json
import logging
import os
from functools import cache
from pathlib import Path

from ats.config import DEFAULT_LANGUAGE, UI_LANGUAGES

_DIR = Path(__file__).parent
_log = logging.getLogger("ats")


class MissingTranslation(KeyError):
    """Texto ausente em um dos idiomas: tratado como defeito (FR-033)."""


@cache
def load(lang: str) -> dict[str, str]:
    if lang not in UI_LANGUAGES:
        raise ValueError(f"Idioma não suportado: {lang}")
    with open(_DIR / f"{lang}.json", encoding="utf-8") as f:
        return json.load(f)


def all_keys(lang: str) -> set[str]:
    return set(load(lang))


def current_language() -> str:
    """Idioma ativo na sessão do Streamlit; padrão `pt_BR` fora dele (por exemplo, nos testes)."""
    from ats.session import has_session

    if not has_session():
        return DEFAULT_LANGUAGE
    import streamlit as st

    value = st.session_state.get("ui_language", DEFAULT_LANGUAGE)
    return value if value in UI_LANGUAGES else DEFAULT_LANGUAGE


def t(key: str, lang: str | None = None, **params: object) -> str:
    lang = lang or current_language()
    table = load(lang)
    text = table.get(key)
    if text is None:
        if lang == DEFAULT_LANGUAGE or os.environ.get("ATS_STRICT_I18N") == "1":
            raise MissingTranslation(f"{key} ({lang})")
        _log.warning("texto ausente: %s (%s); usando português", key, lang)
        text = load(DEFAULT_LANGUAGE)[key]
    return text.format(**params) if params else text
