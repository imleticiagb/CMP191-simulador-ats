"""Orquestra a análise: valida, consulta o cache da sessão, extrai, julga e pontua.

Não depende do Streamlit. O cache é um mapeamento recebido por parâmetro (na sessão do app, o
`st.session_state["results"]`), e nunca vai para o disco (Princípio I, regra 3).
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable, MutableMapping

from ats import config
from ats.analysis import scoring
from ats.analysis.llm_client import LlmClient
from ats.analysis.matcher import judge
from ats.analysis.requirements import extract_requirements
from ats.domain.errors import NotAResume, UnsupportedLanguage
from ats.domain.models import AnalysisResult, InputSource, PdfMeta
from ats.ingest.text_input import validate_job, validate_resume
from ats.logging_setup import log_event, short_hash

ProgressCallback = Callable[[str], None]


def make_result_id(job_text: str, resume_text: str, model: str) -> str:
    raw = "\x00".join([job_text, resume_text, config.PROMPT_VERSION, model])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def analyze(
    job_text: str,
    resume_text: str,
    client: LlmClient,
    *,
    source: InputSource = "pasted",
    pdf_meta: PdfMeta | None = None,
    cache: MutableMapping[str, AnalysisResult] | None = None,
    on_progress: ProgressCallback | None = None,
) -> AnalysisResult:
    progress = on_progress or (lambda _key: None)

    progress("progress.reading")
    job = validate_job(job_text)
    resume = validate_resume(resume_text, source, pdf_meta)

    result_id = make_result_id(job.text, resume.text, client.model_name)
    if cache is not None and result_id in cache:
        log_event("analysis_cached", result=short_hash(result_id))
        return cache[result_id]

    progress("progress.job")
    extraction = extract_requirements(client, job)

    progress("progress.comparing")
    judged = judge(client, resume, extraction.requirements)
    if not judged.looks_like_resume:
        raise NotAResume()

    # FR-031 e FR-032: só pt, en e es; idiomas diferentes entre si geram um aviso, não um erro
    if extraction.language == "other" or judged.language == "other":
        raise UnsupportedLanguage()
    language_notes = ["result.language_note.mixed"] if extraction.language != judged.language else []

    progress("progress.scoring")
    categories = scoring.build_categories(extraction.requirements, judged.verdicts, resume.text, pdf_meta)
    result = AnalysisResult(
        result_id=result_id,
        requirements=extraction.requirements,
        verdicts=judged.verdicts,
        categories=categories,
        overall=scoring.compute_overall(categories),
        language_notes=language_notes,
        improvement_hints=scoring.build_hints(categories, extraction.requirements, judged.verdicts),
        rubric_version=config.RUBRIC_VERSION,
        prompt_version=config.PROMPT_VERSION,
        model=client.model_name,
        source=source,
        job_language=extraction.language,
        resume_language=judged.language,
    )
    if cache is not None:
        cache[result_id] = result
    log_event(
        "analysis_done",
        result=short_hash(result_id),
        requirements=len(result.requirements),
        overall=result.overall,
    )
    return result
