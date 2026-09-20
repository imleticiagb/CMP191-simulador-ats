"""Entidades do simulador (data-model.md). Nada é persistido: tudo vive na memória da sessão."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# --- Enumerações fechadas (reduzem a variação do modelo de linguagem; pesquisa D4) ---
Language = Literal["pt", "en", "es", "other"]
UiLanguage = Literal["pt_BR", "en", "es"]
Importance = Literal["obrigatorio", "desejavel"]
Kind = Literal[
    "formacao",
    "experiencia",
    "habilidade_tecnica",
    "habilidade_comportamental",
    "idioma",
    "certificacao",
    "outro",
]
Status = Literal["atendido", "parcial", "nao_atendido"]
DeductionType = Literal[
    "correspondencia_exata",
    "sinonimo",
    "termo_relacionado",
    "nivel_superior",
    "equivalencia_contextual",
    "sem_evidencia",
]
Certainty = Literal["alta", "media", "baixa"]
CategoryName = Literal["conteudo", "estrutura", "design"]
InputSource = Literal["pasted", "pdf"]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


# --- Entrada ---
class JobPosting(_Strict):
    # obrigatório; 100 a 20.000 caracteres depois de normalizar
    text: str = Field(min_length=100, max_length=20_000)
    language: Language | None = None


class PdfMeta(_Strict):
    file_name: str
    pages: int = Field(ge=1, le=10)  # ≤ 10
    size_bytes: int = Field(ge=0, le=5 * 1024 * 1024)  # ≤ 5 MB
    font_families: int = Field(ge=0)
    body_font_size_range: tuple[float, float]  # (min, max) em pt
    body_font_size_median: float
    min_margin_cm: float
    text_density: float
    has_full_page_image: bool
    column_count: int = Field(ge=1)


class Resume(_Strict):
    source: InputSource
    # 200 a 60.000 caracteres depois de normalizar (espaços e hifenização)
    text: str = Field(min_length=200, max_length=60_000)
    language: Language | None = None
    pdf_meta: PdfMeta | None = None


class Chunk(_Strict):
    index: int = Field(ge=0)
    text: str = Field(max_length=8_000)  # até 8.000 caracteres, com 500 de sobreposição


# --- Análise ---
class Requirement(_Strict):
    id: str  # `R1`, `R2`, ... únicos na análise
    text: str
    kind: Kind
    importance: Importance
    source_excerpt: str


class Verdict(_Strict):
    requirement_id: str
    status: Status
    evidence: list[str] = Field(default_factory=list, max_length=3)  # 0 a 3 trechos literais
    deduction_type: DeductionType
    certainty: Certainty
    justification: str

    @property
    def has_evidence(self) -> bool:
        return bool(self.evidence)


class CriterionResult(_Strict):
    id: str
    points_earned: float
    points_max: float
    explanation_key: str
    explanation_params: dict[str, str | int | float] = Field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.points_earned >= self.points_max


class CategoryScore(_Strict):
    category: CategoryName
    evaluated: bool
    score: int | None = Field(default=None, ge=0, le=100)  # inteiro 0 a 100
    weight: float = 0.0
    criteria: list[CriterionResult] = Field(default_factory=list)
    not_evaluated_key: str | None = None


class Hint(_Strict):
    key: str
    params: dict[str, str | int | float] = Field(default_factory=dict)
    category: CategoryName


class AnalysisResult(_Strict):
    result_id: str
    requirements: list[Requirement]
    verdicts: list[Verdict]
    categories: list[CategoryScore]
    overall: int = Field(ge=0, le=100)
    language_notes: list[str] = Field(default_factory=list)
    improvement_hints: list[Hint] = Field(default_factory=list)
    rubric_version: str
    prompt_version: str
    model: str
    source: InputSource = "pasted"
    job_language: Language | None = None
    resume_language: Language | None = None

    def verdict_for(self, requirement_id: str) -> Verdict | None:
        return next((v for v in self.verdicts if v.requirement_id == requirement_id), None)

    def category(self, name: CategoryName) -> CategoryScore | None:
        return next((c for c in self.categories if c.category == name), None)


class TranslationBundle(_Strict):
    result_id: str
    language: Literal["en", "es"]
    items: dict[str, str] = Field(default_factory=dict)


# --- Respostas do modelo de linguagem (contracts/llm-*.schema.json) ---
class JobDocumentCheck(_Strict):
    looks_like_job_posting: bool
    language: Language


class ResumeDocumentCheck(_Strict):
    looks_like_resume: bool
    language: Language


class ExtractedRequirement(_Strict):
    id: str
    text: str
    kind: Kind
    importance: Importance
    source_excerpt: str


class ExtractionOutput(_Strict):
    document_check: JobDocumentCheck
    requirements: list[ExtractedRequirement]


class RawVerdict(_Strict):
    requirement_id: str
    status: Status
    evidence: list[str]
    deduction_type: DeductionType
    certainty: Certainty
    justification: str


class MatchOutput(_Strict):
    document_check: ResumeDocumentCheck
    verdicts: list[RawVerdict]


class TranslatedItem(_Strict):
    key: str
    text: str


class TranslationOutput(_Strict):
    target_language: Literal["en", "es"]
    items: list[TranslatedItem]
