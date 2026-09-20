"""Seletor de idioma com as bandeiras do Brasil, dos Estados Unidos e da Espanha (FR-028).

As bandeiras são imagens SVG do projeto (emoji de bandeira não aparece no Windows) e vêm sempre com o
texto PT, EN e ES. O idioma ativo usa o botão primário e uma marca, para a indicação não depender só da cor.
"""

from __future__ import annotations

import base64
from functools import cache
from html import escape
from pathlib import Path

import streamlit as st

from ats.config import UI_LANGUAGES
from ats.i18n import t

FLAGS_DIR = Path(__file__).resolve().parents[4] / "static" / "flags"
FLAGS = {"pt_BR": ("br.svg", "PT"), "en": ("us.svg", "EN"), "es": ("es.svg", "ES")}


@cache
def _data_uri(filename: str) -> str:
    raw = (FLAGS_DIR / filename).read_bytes()
    return "data:image/svg+xml;base64," + base64.b64encode(raw).decode("ascii")


def language_name(code: str) -> str:
    """Nome do idioma escrito no próprio idioma (Português (Brasil), English, Español)."""
    return t(f"lang.{code}", code)


def flag_html(code: str) -> str:
    filename, _short = FLAGS[code]
    return (
        f'<img class="ats-flag" src="{_data_uri(filename)}" alt="{escape(language_name(code), quote=True)}">'
    )


def set_language(code: str) -> None:
    st.session_state["ui_language"] = code


def render_language_picker() -> None:
    current = st.session_state.get("ui_language", "pt_BR")
    _, *columns = st.columns([6, 1, 1, 1])
    for column, code in zip(columns, UI_LANGUAGES, strict=True):
        _filename, short = FLAGS[code]
        active = code == current
        with column:
            st.markdown(f'<div class="ats-flag-wrap">{flag_html(code)}</div>', unsafe_allow_html=True)
            st.button(
                f"{short} ✓" if active else short,
                key=f"lang_{code}",
                on_click=set_language,
                args=(code,),
                type="primary" if active else "secondary",
                help=language_name(code),
                use_container_width=True,
            )
