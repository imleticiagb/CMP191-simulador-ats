"""Configuração do Streamlit: arquivos estáticos e fontes declaradas existem e seguem os tokens."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from ats.ui import tokens
from ats.ui.theme import FONT_URLS, build_css

ROOT = Path(__file__).parent.parent.parent
CONFIG = ROOT / ".streamlit" / "config.toml"


@pytest.fixture(scope="module")
def config():
    return tomllib.loads(CONFIG.read_text(encoding="utf-8"))


def test_static_serving_is_enabled(config):
    assert config["server"]["enableStaticServing"] is True


def test_declared_font_files_exist(config):
    faces = config["theme"]["fontFaces"]
    assert {f["family"] for f in faces} == {tokens.FONT_DISPLAY_NAME, tokens.FONT_BODY_NAME}
    for face in faces:
        assert face["url"].startswith("app/static/")
        assert (ROOT / "static" / face["url"].removeprefix("app/static/")).exists(), face["url"]


def test_theme_fonts_and_colors_come_from_tokens(config):
    theme = config["theme"]
    assert theme["headingFont"] == tokens.FONT_DISPLAY_NAME
    assert theme["font"] == tokens.FONT_BODY_NAME
    assert theme["primaryColor"].upper() == tokens.PURPLE_700
    assert theme["textColor"].upper() == tokens.INK


def test_config_is_in_sync_with_the_sync_script():
    import importlib.util

    spec = importlib.util.spec_from_file_location("sync_theme", ROOT / "scripts" / "sync_theme.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert CONFIG.read_text(encoding="utf-8") == module.build_config()


def test_injected_css_declares_both_fonts_with_fallbacks():
    css = build_css()
    for name, url in FONT_URLS.items():
        assert f'font-family: "{name}"' in css and url in css
    assert "Tropi Land" in tokens.FONT_DISPLAY and "sans-serif" in tokens.FONT_DISPLAY
    assert "serif" in tokens.FONT_BODY and "Georgia" in tokens.FONT_BODY
    assert "var(--font-display)" in css and "var(--font-body)" in css
