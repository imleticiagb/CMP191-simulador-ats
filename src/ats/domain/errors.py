"""Erros de entrada e de serviço, cada um com a chave de texto (i18n) da mensagem gentil."""

from __future__ import annotations


class AnalysisError(Exception):
    """Erro que a interface mostra à pessoa, sempre por uma chave de i18n."""

    message_key = "error.generic"

    def __init__(self, message_key: str | None = None, **params: object) -> None:
        self.message_key = message_key or type(self).message_key
        self.params = params
        super().__init__(self.message_key)


class InvalidFile(AnalysisError):
    message_key = "error.pdf.invalid_format"


class UnreadablePdf(AnalysisError):
    message_key = "error.pdf.unreadable"


class PdfTooLarge(AnalysisError):
    message_key = "error.pdf.too_large"


class TextTooShort(AnalysisError):
    message_key = "error.text.too_short"


class TextTooLong(AnalysisError):
    message_key = "error.text.too_long"


class NotAResume(AnalysisError):
    message_key = "error.not_a_resume"


class NotAJobPosting(AnalysisError):
    message_key = "error.not_a_job"


class NoRequirementsFound(AnalysisError):
    message_key = "error.no_requirements"


class UnsupportedLanguage(AnalysisError):
    message_key = "error.unsupported_language"


class ModelRefusal(AnalysisError):
    message_key = "error.refusal"


class ServiceUnavailable(AnalysisError):
    message_key = "error.service_unavailable"


class QuotaExceeded(AnalysisError):
    message_key = "error.quota_exceeded"


class MissingApiKey(AnalysisError):
    message_key = "error.missing_api_key"


ALL_ERROR_KEYS = (
    "error.generic",
    "error.pdf.invalid_format",
    "error.pdf.unreadable",
    "error.pdf.too_large",
    "error.text.too_short",
    "error.text.too_long",
    "error.job.too_short",
    "error.job.too_long",
    "error.resume.too_short",
    "error.resume.too_long",
    "error.not_a_resume",
    "error.not_a_job",
    "error.no_requirements",
    "error.unsupported_language",
    "error.refusal",
    "error.service_unavailable",
    "error.missing_api_key",
    "error.quota_exceeded",
)
