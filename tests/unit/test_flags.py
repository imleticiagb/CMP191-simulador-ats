"""Bandeiras do seletor de idioma (FR-028): imagens SVG guardadas no projeto."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

FLAGS = Path(__file__).parent.parent.parent / "static" / "flags"


@pytest.mark.parametrize("name", ["br.svg", "us.svg", "es.svg"])
def test_flag_is_a_valid_small_svg(name):
    path = FLAGS / name
    assert path.exists() and path.stat().st_size < 5_000
    root = ET.parse(path).getroot()
    assert root.tag.endswith("svg") and root.get("viewBox") == "0 0 32 22"
