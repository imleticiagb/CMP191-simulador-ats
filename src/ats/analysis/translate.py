"""Tradução sob demanda dos textos explicativos (chamada 3). Nota, status, evidência e números não mudam."""

from __future__ import annotations

from collections.abc import MutableMapping

from ats.analysis.llm_client import LlmClient
from ats.domain.models import AnalysisResult, TranslationBundle


def collect_items(result: AnalysisResult) -> dict[str, str]:
    """Só os textos escritos pelo modelo em português: o requisito e a justificativa de cada veredito."""
    items: dict[str, str] = {}
    for requirement in result.requirements:
        items[f"{requirement.id}.text"] = requirement.text
        verdict = result.verdict_for(requirement.id)
        if verdict is not None and verdict.justification.strip():
            items[f"{requirement.id}.justification"] = verdict.justification
    return items


def translate_result(client: LlmClient, result: AnalysisResult, language: str) -> TranslationBundle:
    wanted = collect_items(result)
    output = client.translate(wanted, language)  # type: ignore[arg-type]
    translated = {item.key: item.text for item in output.items if item.key in wanted and item.text.strip()}
    return TranslationBundle(
        result_id=result.result_id,
        language=language,  # type: ignore[arg-type]
        items=translated,
    )


def get_translation(
    result: AnalysisResult,
    language: str,
    cache: MutableMapping[tuple[str, str], TranslationBundle],
    client: LlmClient,
) -> TranslationBundle | None:
    """Tradução guardada por (resultado, idioma). O português é o original e não tem tradução."""
    if language == "pt_BR":
        return None
    key = (result.result_id, language)
    if key not in cache:
        cache[key] = translate_result(client, result, language)
    return cache[key]


def missing_items(result: AnalysisResult, bundle: TranslationBundle | None) -> list[str]:
    """Textos que ficaram sem tradução (a tela mostra o original em português)."""
    if bundle is None:
        return []
    return [key for key in collect_items(result) if key not in bundle.items]
