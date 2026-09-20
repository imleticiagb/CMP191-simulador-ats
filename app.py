"""Simulador de ATS: ponto de entrada do Streamlit.

Estágios: `input` (vaga e currículo) e `result` (nota, categorias e requisitos). Erros aparecem na própria
tela de entrada, para que a pessoa não perca o que digitou.
"""

from __future__ import annotations

import streamlit as st

from ats import config
from ats.analysis.llm_client import get_llm_client
from ats.analysis.pipeline import analyze
from ats.analysis.translate import get_translation, missing_items
from ats.domain.errors import AnalysisError, TextTooShort
from ats.i18n import t
from ats.ingest.pdf_reader import PdfContent, read_pdf
from ats.ui.components.hearts import hearts_row
from ats.ui.components.language_picker import render_language_picker
from ats.ui.components.result_view import render_result
from ats.ui.theme import inject_base_css

st.set_page_config(page_title="Simulador de ATS", page_icon="💗", layout="centered")


def init_state() -> None:
    defaults = {
        "stage": "input",
        "ui_language": "pt_BR",
        "active_input": "pasted",
        "uploader_nonce": 0,
        "results": {},
        "translations": {},
        "current_result": None,
        "last_error": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def keep_input_state() -> None:
    """Widgets não exibidos perdem o valor; guardar os textos evita perder o que foi digitado."""
    for key in ("job_text", "resume_text"):
        st.session_state[key] = st.session_state.get(key, "")


def reset_analysis() -> None:
    """Nova análise (FR-020): limpa entradas, arquivo, resultados e traduções."""
    for key in ("job_text", "resume_text"):
        st.session_state[key] = ""
    st.session_state.update(
        {
            "stage": "input",
            "results": {},
            "translations": {},
            "current_result": None,
            "last_error": None,
            "uploader_nonce": st.session_state.get("uploader_nonce", 0) + 1,
        }
    )


def uploader_key() -> str:
    return f"pdf_file_{st.session_state.get('uploader_nonce', 0)}"


def load_pdf(uploaded) -> PdfContent:
    """Lê o PDF enviado (com cache por nome e tamanho, para não reler a cada interação)."""
    cache = st.session_state.setdefault("pdf_cache", {})
    key = (uploaded.name, uploaded.size)
    if key not in cache:
        try:
            cache[key] = read_pdf(uploaded.getvalue(), uploaded.name)
        except AnalysisError as error:
            cache[key] = error
    outcome = cache[key]
    if isinstance(outcome, AnalysisError):
        raise outcome
    return outcome


def header() -> None:
    st.markdown(
        f'<div class="ats-hero">{hearts_row()}<h1>{t("app.title")}</h1><p>{t("app.subtitle")}</p></div>',
        unsafe_allow_html=True,
    )


def run_analysis() -> None:
    st.session_state["last_error"] = None
    try:
        client = get_llm_client()
        with st.status(t("progress.reading"), expanded=True) as status:

            def progress(key: str) -> None:
                status.update(label=t(key))

            if st.session_state["active_input"] == "pdf":
                uploaded = st.session_state.get(uploader_key())
                if uploaded is None:
                    raise TextTooShort("error.resume.too_short")
                content = load_pdf(uploaded)
                resume_text, source, pdf_meta = content.text, "pdf", content.meta
            else:
                resume_text, source, pdf_meta = st.session_state.get("resume_text", ""), "pasted", None
            result = analyze(
                st.session_state.get("job_text", ""),
                resume_text,
                client,
                source=source,
                pdf_meta=pdf_meta,
                cache=st.session_state["results"],
                on_progress=progress,
            )
            status.update(label=t("progress.done"), state="complete")
    except AnalysisError as error:
        st.session_state["last_error"] = (error.message_key, dict(error.params))
        return
    st.session_state["current_result"] = result.result_id
    st.session_state["stage"] = "result"
    st.rerun()


def show_error(box) -> None:
    if st.session_state["last_error"]:
        key, params = st.session_state["last_error"]
        box.error(f"**{t('error.title')}**  \n{t(key, **params)}")


def set_mode(mode: str) -> None:
    st.session_state["active_input"] = mode


def mode_picker() -> None:
    """Escolha entre colar o texto e enviar um PDF. O modo ativo tem botão primário e uma marca."""
    st.markdown(f"**{t('input.resume.mode')}**")
    columns = st.columns(2)
    for column, mode in zip(columns, ("pasted", "pdf"), strict=True):
        active = st.session_state["active_input"] == mode
        label = t(f"input.resume.mode.{mode}")
        column.button(
            f"✓ {label}" if active else label,
            key=f"mode_{mode}",
            on_click=set_mode,
            args=(mode,),
            type="primary" if active else "secondary",
            use_container_width=True,
        )


def resume_pdf_input() -> None:
    uploaded = st.file_uploader(
        t("input.pdf.label"),
        key=uploader_key(),
        help=t("input.pdf.hint", pages=config.MAX_PDF_PAGES, mb=config.MAX_PDF_BYTES // (1024 * 1024)),
    )
    if uploaded is None:
        return
    try:
        content = load_pdf(uploaded)
    except AnalysisError as error:
        st.error(t(error.message_key, **error.params))
        return
    pages = content.meta.pages
    key = "input.pdf.received_one" if pages == 1 else "input.pdf.received"
    st.success(t(key, name=uploaded.name, pages=pages))


def input_stage() -> None:
    error_box = st.container()
    st.text_area(
        t("input.job.label"),
        key="job_text",
        height=180,
        help=t("input.job.help"),
        placeholder=t("input.job.placeholder"),
    )
    st.markdown(f"### {t('input.resume.title')}")
    mode_picker()
    if st.session_state["active_input"] == "pdf":
        resume_pdf_input()
    else:
        st.text_area(
            t("input.resume.label"),
            key="resume_text",
            height=240,
            placeholder=t("input.resume.placeholder"),
        )
    st.caption(t("input.only_selected"))
    st.caption(t("privacy.notice"))
    if st.button(t("input.submit"), key="submit", type="primary"):
        run_analysis()
    show_error(error_box)


def result_stage() -> None:
    result = st.session_state["results"].get(st.session_state["current_result"])
    if result is None:
        st.session_state["stage"] = "input"
        st.rerun()
    lang = st.session_state["ui_language"]
    bundle = None
    if lang != "pt_BR":
        try:
            with st.spinner(t("result.translating")):
                bundle = get_translation(result, lang, st.session_state["translations"], get_llm_client())
        except AnalysisError as error:
            st.warning(t(error.message_key, **error.params))
    render_result(result, lang, bundle.items if bundle else None)
    if lang != "pt_BR" and (bundle is None or missing_items(result, bundle)):
        st.caption(t("result.translation_missing"))
    st.button(t("app.new_analysis"), key="new_analysis", on_click=reset_analysis)


init_state()
keep_input_state()
inject_base_css()
render_language_picker()
header()
if st.session_state["stage"] == "result":
    result_stage()
else:
    input_stage()
st.caption(t("app.disclaimer"))
