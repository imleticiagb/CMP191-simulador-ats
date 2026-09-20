"""CSS do tema rosa e roxo, gerado só a partir dos tokens (Princípio III). Injetado em cada página."""

from __future__ import annotations

from ats.ui import tokens as tk
from ats.ui.components.hearts import heart_data_uri

FONT_URLS = {
    tk.FONT_DISPLAY_NAME: "app/static/fonts/TropiLand-Demo.ttf",
    tk.FONT_BODY_NAME: "app/static/fonts/Lora.ttf",
}


def _font_faces() -> str:
    return "\n".join(
        f'@font-face {{ font-family: "{name}"; src: url("{url}") format("truetype"); font-display: swap; }}'
        for name, url in FONT_URLS.items()
    )


def _root_variables() -> str:
    lines = [f"  --{name.replace('_', '-')}: {value};" for name, value in tk.IDENTITY_COLORS.items()]
    lines += [f"  --accent-light: {tk.ACCENT_LIGHT};", f"  --accent-deep: {tk.ACCENT_DEEP};"]
    lines += [f"  --font-display: {tk.FONT_DISPLAY};", f"  --font-body: {tk.FONT_BODY};"]
    return ":root {\n" + "\n".join(lines) + "\n}"


def build_css() -> str:
    heart = heart_data_uri(tk.PINK_300)
    return f"""
{_font_faces()}
{_root_variables()}

.stApp {{
  background: linear-gradient(180deg, var(--pink-50) 0%, var(--purple-50) 100%);
  color: var(--ink);
  font-family: var(--font-body);
}}
.stApp p, .stApp li, .stApp label, .stApp textarea, .stApp input,
[data-testid="stMarkdownContainer"] {{
  font-family: var(--font-body);
}}
h1, h2, h3, h4, h1 *, h2 *, h3 *, h4 *, .ats-display, .ats-display *, [data-testid="stHeading"] {{
  font-family: var(--font-display) !important;
  color: var(--purple-700);
  letter-spacing: 0.02em;
}}
[data-testid="stHeaderActionElements"] {{ display: none; }}
.block-container {{ max-width: 860px; padding-top: 4.5rem; }}

/* Botões: cantos arredondados, roxo e rosa */
[data-testid^="stBaseButton"], [data-testid^="stBaseButton"] p {{
  font-family: var(--font-display);
}}
[data-testid^="stBaseButton"] {{
  border-radius: 999px;
  border: 2px solid var(--purple-500);
}}
[data-testid="stBaseButton-primary"] {{
  background: var(--purple-700);
  color: var(--white);
  border-color: var(--purple-700);
}}
[data-testid="stBaseButton-secondary"] {{
  background: var(--white);
  color: var(--purple-700);
}}
textarea, input {{
  border-radius: 16px !important;
  border: 2px solid var(--pink-300) !important;
  background: var(--white) !important;
  color: var(--ink) !important;
}}

/* Cabeçalho */
.ats-hero {{ text-align: center; margin-bottom: 0.5rem; }}
.ats-hero h1 {{ margin: 0.2rem 0; font-size: 2.6rem; }}
.ats-hero p {{ margin: 0 auto; max-width: 34rem; }}
.ats-hearts {{ display: flex; gap: 0.5rem; justify-content: center; align-items: center; }}
.ats-heart {{ display: inline-block; }}

/* Cartões: borda rosa, cantos arredondados e um coração no canto */
.ats-card {{
  position: relative;
  background: var(--white);
  border: 2px solid var(--pink-300);
  border-radius: 20px;
  padding: 1rem 1.25rem;
  margin: 0.75rem 0;
}}
.ats-card::after {{
  content: "";
  position: absolute; top: 10px; right: 12px; width: 22px; height: 22px;
  background: url("{heart}") no-repeat center / contain;
  pointer-events: none;
}}
.ats-card h4 {{ margin: 0 0 0.4rem 0; padding-right: 2rem; font-size: 1.05rem; }}
.ats-quote {{
  border-left: 4px solid var(--purple-300);
  background: var(--purple-50);
  border-radius: 8px;
  padding: 0.4rem 0.75rem;
  margin: 0.4rem 0;
  font-style: italic;
}}
.ats-badge {{
  display: inline-block; border-radius: 999px; padding: 0.05rem 0.6rem; margin-right: 0.35rem;
  font-size: 0.85rem; border: 2px solid var(--purple-300); background: var(--purple-100);
  color: var(--purple-900);
}}
.ats-badge.status-atendido {{ background: var(--purple-700); color: var(--white); border-color: var(--purple-700); }}
.ats-badge.status-parcial {{ background: var(--pink-100); color: var(--pink-700); border-color: var(--pink-500); }}
.ats-badge.status-nao_atendido {{ background: var(--white); color: var(--pink-700); border: 2px dashed var(--pink-500); }}
.ats-note {{ font-size: 0.9rem; color: var(--purple-700); }}

/* Destaque da pontuação */
.ats-overall {{ text-align: center; }}
.ats-overall .ats-score {{
  font-family: var(--font-display); font-size: 4rem; color: var(--purple-700); line-height: 1.1;
}}

/* Barra de progresso segmentada (escala de dados: única cor de acento) */
.ats-bar-wrap {{ margin: 0.5rem 0; }}
.ats-bar-head {{ display: flex; justify-content: space-between; align-items: baseline; gap: 0.5rem; }}
.ats-bar-label {{ font-family: var(--font-display); color: var(--purple-700); }}
.ats-bar-value {{ font-family: var(--font-display); font-size: 1.4rem; color: var(--purple-700); }}
.ats-bar {{ display: flex; gap: 2px; margin: 0.25rem 0; }}
.ats-seg {{ flex: 1 1 0; min-width: 0; height: 16px; border-radius: 4px; background: var(--purple-100); }}
.ats-bar.empty .ats-seg {{ background: var(--purple-100); opacity: 0.6; }}

/* Seletor de idioma: siglas legíveis em fonte serifada */
[class*="st-key-lang_"] button, [class*="st-key-lang_"] button p {{ font-family: var(--font-body) !important; font-weight: 700; }}
.ats-flag-wrap {{ display: flex; justify-content: center; align-items: flex-end; min-height: 26px; }}
.ats-flag {{ display: block; width: 32px; height: 22px; border-radius: 4px; border: 1px solid var(--purple-300); vertical-align: middle; }}

@media (max-width: 480px) {{
  .ats-hero h1 {{ font-size: 2rem; }}
  .ats-overall .ats-score {{ font-size: 3rem; }}
  .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
}}
""".strip()


def inject_base_css() -> None:
    """Injeta o CSS do tema. Chamar uma vez por execução do script."""
    import streamlit as st

    st.markdown(f"<style>{build_css()}</style>", unsafe_allow_html=True)
