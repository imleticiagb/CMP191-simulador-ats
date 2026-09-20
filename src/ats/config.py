"""Constantes do simulador. Ponto único para limites, modelo e versões da rubrica e dos prompts."""

from __future__ import annotations

import os

# --- Limites de entrada (spec, Assumptions; pesquisa D3) ---
MAX_PDF_PAGES = 10
MAX_PDF_BYTES = 5 * 1024 * 1024
MIN_JOB_CHARS = 100
MAX_JOB_CHARS = 20_000
MIN_RESUME_CHARS = 200
MAX_RESUME_CHARS = 60_000

# --- Chunking (pesquisa D3) ---
CHUNK_THRESHOLD_CHARS = 20_000
CHUNK_SIZE = 8_000
CHUNK_OVERLAP = 500

# --- Modelo de linguagem: Google Gemini (pesquisa D4) ---
DEFAULT_MODEL = "gemini-3.1-flash-lite"  # rápido e com cota gratuita maior; ver README para trocar
MODEL = os.environ.get("ATS_MODEL", DEFAULT_MODEL)
API_KEY_ENV_VARS = ("GEMINI_API_KEY", "GOOGLE_API_KEY")
MAX_OUTPUT_TOKENS = 16_384
TEMPERATURE = 0.0  # reduz a variação dos vereditos entre execuções (Princípio I, regra 3)
SEED = 7
THINKING_EXTRACT = "low"
THINKING_MATCH = "medium"
THINKING_TRANSLATE = "low"
MAX_REQUIREMENTS = 30
RETRY_DELAYS = (2.0, 6.0, 15.0)  # espera, em segundos, entre novas tentativas em picos de demanda
RETRYABLE_CODES = (429, 500, 502, 503, 504)

# --- Versões (entram no result_id) ---
PROMPT_VERSION = "prompts-1"
RUBRIC_VERSION = "rubric-1"

# --- Idiomas ---
DEFAULT_LANGUAGE = "pt_BR"
UI_LANGUAGES = ("pt_BR", "en", "es")
