"""Acesso ao modelo de linguagem atrás de uma interface, para testar sem rede e trocar de provedor.

- `GeminiLlmClient`: SDK oficial `google-genai`, saída estruturada validada por esquema (pesquisa D4),
  com temperatura 0 e semente fixa para reduzir a variação entre execuções.
- `FakeLlmClient`: respostas gravadas ou um avaliador simples por palavras, só para testes e demonstração.
- `get_llm_client()`: escolhe entre eles (`ATS_LLM=fake` ou `st.session_state["llm_override"]`).
"""

from __future__ import annotations

import os
import re
import time
import tomllib
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any, Literal, Protocol, TypeVar

from pydantic import BaseModel, ValidationError

from ats import config
from ats.analysis import prompts
from ats.domain.errors import MissingApiKey, ModelRefusal, QuotaExceeded, ServiceUnavailable
from ats.domain.models import (
    ExtractedRequirement,
    ExtractionOutput,
    JobDocumentCheck,
    MatchOutput,
    RawVerdict,
    Requirement,
    ResumeDocumentCheck,
    TranslatedItem,
    TranslationOutput,
)
from ats.logging_setup import log_event, timed

T = TypeVar("T", bound=BaseModel)
TargetLanguage = Literal["en", "es"]


class LlmClient(Protocol):
    model_name: str

    def extract_requirements(self, job_text: str) -> ExtractionOutput: ...

    def match_requirements(
        self, resume_text: str, requirements: Sequence[Requirement], chunk: tuple[int, int] | None = None
    ) -> MatchOutput: ...

    def translate(self, items: Mapping[str, str], target: TargetLanguage) -> TranslationOutput: ...


# ---------------------------------------------------------------- chave de API
SECRETS_FILE = Path(__file__).resolve().parents[3] / ".streamlit" / "secrets.toml"
_REFUSAL_FINISH = {"SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST", "SPII", "RECITATION", "IMAGE_SAFETY"}


def resolve_api_key() -> str | None:
    """Chave do Gemini: variável de ambiente, `st.secrets` (no app) ou `.streamlit/secrets.toml` (fora dele)."""
    for name in config.API_KEY_ENV_VARS:
        if os.environ.get(name):
            return os.environ[name]
    from ats.session import has_session

    for name in config.API_KEY_ENV_VARS:
        if has_session():
            try:
                import streamlit as st

                value = st.secrets.get(name)
            except Exception:  # sem arquivo de segredos
                value = None
            if value:
                return str(value)
    if SECRETS_FILE.exists():
        try:
            data = tomllib.loads(SECRETS_FILE.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError):
            return None
        for name in config.API_KEY_ENV_VARS:
            if data.get(name):
                return str(data[name])
    return None


# ---------------------------------------------------------------- cliente real
class GeminiLlmClient:
    """Chama a API do Google Gemini. A chave vem de `GEMINI_API_KEY` (ou `GOOGLE_API_KEY`) ou dos segredos."""

    def __init__(self, model: str | None = None, client: Any = None) -> None:
        self.model_name = model or config.MODEL
        self._client = client
        self._contents = ""

    def _get_client(self) -> Any:
        if self._client is None:
            from google import genai

            api_key = resolve_api_key()
            if not api_key:
                raise MissingApiKey()
            self._client = genai.Client(api_key=api_key)
        return self._client

    def _call(self, system: str, user: str, output_model: type[T], thinking: str, stage: str) -> T:
        from google.genai import errors, types

        client = self._get_client()
        self._contents = user
        generation = types.GenerateContentConfig(
            system_instruction=system,
            temperature=config.TEMPERATURE,
            seed=config.SEED,
            max_output_tokens=config.MAX_OUTPUT_TOKENS,
            response_mime_type="application/json",
            response_json_schema=output_model.model_json_schema(),
            thinking_config=types.ThinkingConfig(thinking_level=thinking),
        )
        response = self._generate_with_retry(client, generation, stage, errors)

        usage = getattr(response, "usage_metadata", None)
        log_event(
            f"{stage}_usage",
            input_tokens=getattr(usage, "prompt_token_count", 0) or 0,
            output_tokens=getattr(usage, "candidates_token_count", 0) or 0,
        )
        # Sempre verificar bloqueio e motivo de término antes de usar o conteúdo
        feedback = getattr(response, "prompt_feedback", None)
        if feedback is not None and getattr(feedback, "block_reason", None):
            raise ModelRefusal()
        candidates = getattr(response, "candidates", None) or []
        if not candidates:
            raise ModelRefusal()
        finish = getattr(candidates[0].finish_reason, "name", str(candidates[0].finish_reason)).upper()
        if finish in _REFUSAL_FINISH:
            raise ModelRefusal()
        if finish not in ("STOP", "FINISH_REASON_UNSPECIFIED", "NONE"):
            raise ServiceUnavailable()
        text = getattr(response, "text", None)
        if not text:
            raise ServiceUnavailable()
        try:
            return output_model.model_validate_json(text)
        except ValidationError as exc:
            raise ServiceUnavailable() from exc

    def _generate_with_retry(self, client: Any, generation: Any, stage: str, errors: Any) -> Any:
        """Chama o modelo, repetindo com espera em picos de demanda (503, 429 e afins)."""
        delays = list(config.RETRY_DELAYS)
        while True:
            try:
                with timed(stage, model=self.model_name):
                    return client.models.generate_content(
                        model=self.model_name, contents=self._contents, config=generation
                    )
            except errors.APIError as exc:
                message = str(getattr(exc, "message", "") or exc).lower()
                if exc.code in (401, 403) or (exc.code == 400 and "api key" in message):
                    raise MissingApiKey() from exc
                if exc.code == 429 and ("perday" in message or "per day" in message or "daily" in message):
                    raise QuotaExceeded() from exc  # cota diária esgotada: repetir não adianta
                if exc.code in config.RETRYABLE_CODES and delays:
                    log_event(f"{stage}_retry", code=exc.code)
                    time.sleep(delays.pop(0))
                    continue
                raise ServiceUnavailable() from exc
            except (ConnectionError, TimeoutError, OSError) as exc:
                raise ServiceUnavailable() from exc
            except Exception as exc:  # falhas de rede da biblioteca HTTP
                if type(exc).__module__.startswith("httpx"):
                    raise ServiceUnavailable() from exc
                raise

    def extract_requirements(self, job_text: str) -> ExtractionOutput:
        system, user = prompts.extract_prompt(job_text)
        return self._call(system, user, ExtractionOutput, config.THINKING_EXTRACT, "extract")

    def match_requirements(
        self, resume_text: str, requirements: Sequence[Requirement], chunk: tuple[int, int] | None = None
    ) -> MatchOutput:
        system, user = prompts.match_prompt(resume_text, requirements, chunk)
        return self._call(system, user, MatchOutput, config.THINKING_MATCH, "match")

    def translate(self, items: Mapping[str, str], target: TargetLanguage) -> TranslationOutput:
        system, user = prompts.translate_prompt(items, target)
        return self._call(system, user, TranslationOutput, config.THINKING_TRANSLATE, "translate")


# ---------------------------------------------------------------- cliente falso
_STOPWORDS = {
    "pt": {"de", "da", "do", "para", "com", "uma", "em", "que", "os", "as", "experiência", "vaga"},
    "en": {"the", "and", "for", "with", "of", "to", "in", "experience", "job", "our"},
    "es": {"el", "los", "las", "para", "con", "una", "del", "experiencia", "vacante", "y"},
}
_DESIRABLE = re.compile(r"desej[aá]vel|diferencial|seria bom|nice to have|plus|deseable", re.IGNORECASE)
_RESUME_HINTS = re.compile(
    r"experi[êe]ncia|forma[çc][ãa]o|educa[çc][ãa]o|education|experience|skills|habilidades|@", re.I
)
_DEGREE = ("licenciatura", "graduação", "graduacao", "bacharel", "degree", "grado")


def detect_language(text: str) -> str:
    words = re.findall(r"[a-záéíóúâêôãõçñ]+", text.lower())
    scores = {lang: sum(w in sw for w in words) for lang, sw in _STOPWORDS.items()}
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] >= 2 else "other"


def _stems(text: str) -> set[str]:
    return {w[:5] for w in re.findall(r"[a-záéíóúâêôãõçñ]{4,}", text.lower())}


def _kind(line: str) -> str:
    low = line.lower()
    if any(d in low for d in _DEGREE) or "formação" in low:
        return "formacao"
    if "inglês" in low or "espanhol" in low or "english" in low or "spanish" in low:
        return "idioma"
    if "certifica" in low:
        return "certificacao"
    if "comunica" in low or "equipe" in low or "team" in low or "liderança" in low:
        return "habilidade_comportamental"
    if "experi" in low:
        return "experiencia"
    return "habilidade_tecnica"


class FakeLlmClient:
    """Cliente de teste. Com respostas gravadas, devolve exatamente elas; sem elas, usa um avaliador simples.

    O avaliador por palavras existe só para demonstração e testes sem chave. Ele não substitui o modelo real.
    """

    def __init__(
        self,
        extract: ExtractionOutput | Callable[[str], ExtractionOutput] | None = None,
        match: MatchOutput | Callable[..., MatchOutput] | None = None,
        translate: TranslationOutput | Callable[..., TranslationOutput] | None = None,
        model_name: str = "fake",
    ) -> None:
        self.model_name = model_name
        self._extract, self._match, self._translate = extract, match, translate
        self.calls: list[str] = []

    # -- interface
    def extract_requirements(self, job_text: str) -> ExtractionOutput:
        self.calls.append("extract")
        if callable(self._extract):
            return self._extract(job_text)
        return self._extract or self._heuristic_extract(job_text)

    def match_requirements(
        self, resume_text: str, requirements: Sequence[Requirement], chunk: tuple[int, int] | None = None
    ) -> MatchOutput:
        self.calls.append("match")
        if callable(self._match):
            return self._match(resume_text, requirements, chunk)
        return self._match or self._heuristic_match(resume_text, requirements)

    def translate(self, items: Mapping[str, str], target: TargetLanguage) -> TranslationOutput:
        self.calls.append("translate")
        if callable(self._translate):
            return self._translate(items, target)
        if self._translate is not None:
            return self._translate
        tag = target.upper()
        return TranslationOutput(
            target_language=target,
            items=[TranslatedItem(key=k, text=f"[{tag}] {v}") for k, v in items.items()],
        )

    # -- avaliador simples
    def _heuristic_extract(self, job_text: str) -> ExtractionOutput:
        lines = [re.sub(r"^[\s\-•*·\d.)]+", "", ln).strip() for ln in job_text.splitlines()]
        candidates = [ln for ln in lines if len(ln.split()) >= 3 and not ln.endswith(":")]
        reqs = [
            ExtractedRequirement(
                id=f"R{i}",
                text=ln.rstrip("."),
                kind=_kind(ln),  # type: ignore[arg-type]
                importance="desejavel" if _DESIRABLE.search(ln) else "obrigatorio",
                source_excerpt=ln,
            )
            for i, ln in enumerate(candidates[: config.MAX_REQUIREMENTS], start=1)
        ]
        return ExtractionOutput(
            document_check=JobDocumentCheck(
                looks_like_job_posting=bool(reqs),
                language=detect_language(job_text),  # type: ignore[arg-type]
            ),
            requirements=reqs,
        )

    def _heuristic_match(self, resume_text: str, requirements: Sequence[Requirement]) -> MatchOutput:
        sentences = [s.strip() for s in re.split(r"\n+|(?<=[.!?])\s+", resume_text) if len(s.strip()) > 3]
        verdicts: list[RawVerdict] = []
        for req in requirements:
            verdicts.append(self._judge(req, sentences))
        return MatchOutput(
            document_check=ResumeDocumentCheck(
                looks_like_resume=bool(_RESUME_HINTS.search(resume_text)),
                language=detect_language(resume_text),  # type: ignore[arg-type]
            ),
            verdicts=verdicts,
        )

    @staticmethod
    def _judge(req: Requirement, sentences: list[str]) -> RawVerdict:
        low_req = req.text.lower()
        req_stems = _stems(req.text)
        best, best_ratio = "", 0.0
        for sentence in sentences:
            ratio = len(req_stems & _stems(sentence)) / len(req_stems) if req_stems else 0.0
            if ratio > best_ratio:
                best, best_ratio = sentence, ratio
        # Regra de exemplo da spec: formação concluída cumpre formação "em curso"
        if "em curso" in low_req or "cursando" in low_req:
            for sentence in sentences:
                low = sentence.lower()
                if "conclu" in low and any(d in low for d in _DEGREE) and any(d in low_req for d in _DEGREE):
                    return RawVerdict(
                        requirement_id=req.id,
                        status="atendido",
                        evidence=[sentence],
                        deduction_type="nivel_superior",
                        certainty="alta",
                        justification="Você já concluiu a formação, o que cumpre o que se pede a quem a está cursando.",
                    )
        if best_ratio >= 0.6:
            exact = low_req.rstrip(".") in best.lower()
            return RawVerdict(
                requirement_id=req.id,
                status="atendido",
                evidence=[best],
                deduction_type="correspondencia_exata" if exact else "termo_relacionado",
                certainty="alta" if exact else "media",
                justification="O trecho do seu currículo trata do mesmo assunto que o requisito.",
            )
        if best_ratio >= 0.3:
            return RawVerdict(
                requirement_id=req.id,
                status="parcial",
                evidence=[best],
                deduction_type="termo_relacionado",
                certainty="media",
                justification="O trecho se aproxima do requisito, mas não o cobre por completo.",
            )
        return RawVerdict(
            requirement_id=req.id,
            status="nao_atendido",
            evidence=[],
            deduction_type="sem_evidencia",
            certainty="alta",
            justification="",
        )


# ---------------------------------------------------------------- fábrica
def get_llm_client() -> LlmClient:
    """Cliente usado pelo app: o da sessão (testes), o falso (`ATS_LLM=fake`) ou o real."""
    from ats.session import has_session

    override = None
    if has_session():
        import streamlit as st

        override = st.session_state.get("llm_override")
    if override is not None:
        return override
    if os.environ.get("ATS_LLM") == "fake":
        return FakeLlmClient()
    return GeminiLlmClient()
