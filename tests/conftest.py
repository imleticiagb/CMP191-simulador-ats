"""Configuração comum dos testes: i18n estrito, sem chamadas reais ao modelo."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ["ATS_STRICT_I18N"] = "1"

FIXTURES = Path(__file__).parent / "fixtures"
ROOT = Path(__file__).parent.parent


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES


@pytest.fixture
def read_fixture():
    def _read(name: str) -> str:
        return (FIXTURES / name).read_text(encoding="utf-8")

    return _read


@pytest.fixture
def project_root() -> Path:
    return ROOT
