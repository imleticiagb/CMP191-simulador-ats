"""Detecta se o código está rodando dentro de uma sessão do Streamlit (ou de um AppTest)."""

from __future__ import annotations


def has_session() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        return get_script_run_ctx() is not None
    except Exception:
        return False
