"""Escreve o .streamlit/config.toml a partir de src/ats/ui/tokens.py, mantendo os tokens como única fonte.

Uso: uv run python scripts/sync_theme.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from ats.ui import tokens as tk  # noqa: E402
from ats.ui.theme import FONT_URLS  # noqa: E402

CONFIG_PATH = ROOT / ".streamlit" / "config.toml"


def build_config() -> str:
    faces = "\n".join(
        f'[[theme.fontFaces]]\nfamily = "{name}"\nurl = "{url}"\n' for name, url in FONT_URLS.items()
    )
    return f"""[server]
enableStaticServing = true

[client]
toolbarMode = "minimal"

[theme]
primaryColor = "{tk.PURPLE_700}"
backgroundColor = "{tk.PINK_50}"
secondaryBackgroundColor = "{tk.PURPLE_50}"
textColor = "{tk.INK}"
font = "{tk.FONT_BODY_NAME}"
headingFont = "{tk.FONT_DISPLAY_NAME}"

{faces}"""


def main() -> None:
    CONFIG_PATH.parent.mkdir(exist_ok=True)
    CONFIG_PATH.write_text(build_config(), encoding="utf-8")
    print(f"Escrito {CONFIG_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
