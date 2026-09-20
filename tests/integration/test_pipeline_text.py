"""Pipeline completa com cliente falso: dedução semântica, sem evidência, repetição, chunks e erros."""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest
from google.genai import errors as google_errors

from ats import config
from ats.analysis.llm_client import FakeLlmClient, GeminiLlmClient
from ats.analysis.pipeline import analyze
from ats.domain.errors import (
    MissingApiKey,
    ModelRefusal,
    NoRequirementsFound,
    NotAJobPosting,
    NotAResume,
    QuotaExceeded,
    ServiceUnavailable,
    TextTooShort,
)
from ats.domain.models import ExtractionOutput, MatchOutput


def _client(read_fixture, match="match_ok.json") -> FakeLlmClient:
    return FakeLlmClient(
        extract=ExtractionOutput.model_validate_json(read_fixture("extract_ok.json")),
        match=MatchOutput.model_validate_json(read_fixture(match)),
    )


@pytest.fixture
def texts(read_fixture):
    return read_fixture("job_licenciatura.txt"), read_fixture("resume_licenciatura.txt")


def test_degree_completed_meets_degree_in_progress_with_explained_deduction(read_fixture, texts):
    job, resume = texts
    result = analyze(job, resume, _client(read_fixture))
    first = result.verdict_for("R1")
    assert first.status == "atendido"
    assert first.deduction_type == "nivel_superior"
    assert first.certainty == "alta"
    assert "concluiu" in first.justification and first.evidence
    assert [r.id for r in result.requirements] == ["R1", "R2", "R3", "R4"]
    assert result.requirements[3].importance == "desejavel"


def test_every_requirement_has_a_verdict_and_content_score(read_fixture, texts):
    job, resume = texts
    result = analyze(job, resume, _client(read_fixture))
    assert {v.requirement_id for v in result.verdicts} == {r.id for r in result.requirements}
    content = result.category("conteudo")
    assert content.score == 86 and content.evaluated
    assert 0 <= result.overall <= 100
    assert result.rubric_version == config.RUBRIC_VERSION and result.prompt_version == config.PROMPT_VERSION


def test_requirement_without_evidence_is_reported_as_such(read_fixture, texts):
    job, resume = texts
    result = analyze(job, resume, _client(read_fixture, "match_sem_evidencia.json"))
    for rid in ("R3", "R4"):
        verdict = result.verdict_for(rid)
        assert verdict.status == "nao_atendido"
        assert verdict.deduction_type == "sem_evidencia"
        assert verdict.evidence == []


def test_repeating_the_analysis_in_the_same_session_reuses_the_result(read_fixture, texts):
    job, resume = texts
    client, cache = _client(read_fixture), {}
    first = analyze(job, resume, client, cache=cache)
    calls = list(client.calls)
    second = analyze(job, resume, client, cache=cache)
    assert client.calls == calls, "não pode chamar o modelo de novo"
    assert second == first
    assert first.result_id in cache


def test_different_texts_produce_different_result_ids(read_fixture, texts):
    job, resume = texts
    a = analyze(job, resume, _client(read_fixture))
    b = analyze(job + "\n- Mais um requisito de exemplo", resume, _client(read_fixture))
    assert a.result_id != b.result_id


def test_long_resume_is_analyzed_in_chunks(read_fixture, texts):
    job, resume = texts
    filler = "\n\n".join(
        f"Projeto {i}: organização de rotinas administrativas e apoio à equipe." * 3 for i in range(200)
    )
    long_resume = filler + "\n\n" + resume
    assert len(long_resume) > config.CHUNK_THRESHOLD_CHARS
    seen: list[tuple[int, int] | None] = []
    base = MatchOutput.model_validate_json(read_fixture("match_ok.json"))

    def match(text, requirements, chunk):
        seen.append(chunk)
        return (
            base
            if "Licenciatura em Pedagogia" in text
            else MatchOutput.model_validate(
                {
                    "document_check": {"looks_like_resume": True, "language": "pt"},
                    "verdicts": [
                        {
                            "requirement_id": r.id,
                            "status": "nao_atendido",
                            "evidence": [],
                            "deduction_type": "sem_evidencia",
                            "certainty": "alta",
                            "justification": "",
                        }
                        for r in requirements
                    ],
                }
            )
        )

    client = FakeLlmClient(
        extract=ExtractionOutput.model_validate_json(read_fixture("extract_ok.json")), match=match
    )
    result = analyze(job, long_resume, client)
    assert len(seen) >= 2 and all(c is not None for c in seen)
    assert result.verdict_for("R1").status == "atendido"
    assert result.category("conteudo").score == 86


def test_progress_callback_reports_the_steps(read_fixture, texts):
    job, resume = texts
    steps: list[str] = []
    analyze(job, resume, _client(read_fixture), on_progress=steps.append)
    assert steps[:3] == ["progress.reading", "progress.job", "progress.comparing"]
    assert "progress.scoring" in steps


def test_short_inputs_are_rejected_before_calling_the_model(read_fixture, texts):
    job, resume = texts
    client = _client(read_fixture)
    with pytest.raises(TextTooShort):
        analyze("curta", resume, client)
    with pytest.raises(TextTooShort):
        analyze(job, "curto", client)
    assert client.calls == []


def test_not_a_job_and_not_a_resume_and_no_requirements(read_fixture, texts):
    job, resume = texts
    extraction = json.loads(read_fixture("extract_ok.json"))
    not_job = {**extraction, "document_check": {"looks_like_job_posting": False, "language": "pt"}}
    with pytest.raises(NotAJobPosting):
        analyze(job, resume, FakeLlmClient(extract=ExtractionOutput.model_validate(not_job)))
    empty = {**extraction, "requirements": []}
    with pytest.raises(NoRequirementsFound):
        analyze(job, resume, FakeLlmClient(extract=ExtractionOutput.model_validate(empty)))
    match = json.loads(read_fixture("match_ok.json"))
    match["document_check"]["looks_like_resume"] = False
    with pytest.raises(NotAResume):
        analyze(
            job,
            resume,
            FakeLlmClient(
                extract=ExtractionOutput.model_validate(extraction), match=MatchOutput.model_validate(match)
            ),
        )


class _Raising:
    model_name = "x"

    def __init__(self, exc):
        self.exc = exc

    def extract_requirements(self, job_text):
        raise self.exc

    def match_requirements(self, *a, **k):
        raise self.exc

    def translate(self, *a, **k):
        raise self.exc


@pytest.mark.parametrize("exc", [ModelRefusal(), MissingApiKey(), ServiceUnavailable()])
def test_model_errors_carry_a_gentle_message_key(texts, exc):
    job, resume = texts
    with pytest.raises(type(exc)) as caught:
        analyze(job, resume, _Raising(exc))
    assert caught.value.message_key.startswith("error.")


# ---- cliente real (Gemini) com o SDK simulado, sem rede
class _StubModels:
    def __init__(self, response=None, error=None):
        self.response, self.error, self.kwargs = response, error, None

    def generate_content(self, **kwargs):
        self.kwargs = kwargs
        if self.error:
            raise self.error
        return self.response


def _stub_client(finish="STOP", text="{}", block=None, candidates=True, error=None):
    response = SimpleNamespace(
        text=text,
        candidates=[SimpleNamespace(finish_reason=SimpleNamespace(name=finish))] if candidates else [],
        prompt_feedback=SimpleNamespace(block_reason=block),
        usage_metadata=SimpleNamespace(prompt_token_count=10, candidates_token_count=5),
    )
    models = _StubModels(response, error)
    return SimpleNamespace(models=models), models


def _extract(sdk):
    return GeminiLlmClient(model="gemini-3.6-flash", client=sdk).extract_requirements("x" * 120)


def test_gemini_client_requests_structured_json_with_fixed_sampling(read_fixture):
    sdk, models = _stub_client(text=read_fixture("extract_ok.json"))
    out = _extract(sdk)
    assert len(out.requirements) == 4
    cfg = models.kwargs["config"]
    assert models.kwargs["model"] == "gemini-3.6-flash"
    assert cfg.temperature == config.TEMPERATURE == 0.0 and cfg.seed == config.SEED
    assert cfg.response_mime_type == "application/json"
    assert "requirements" in cfg.response_json_schema["properties"]
    assert cfg.thinking_config.thinking_level.value.lower() == config.THINKING_EXTRACT
    assert cfg.max_output_tokens == config.MAX_OUTPUT_TOKENS
    assert "vaga" in cfg.system_instruction and "<vaga>" in models.kwargs["contents"]


def test_gemini_client_translation_and_match_use_their_own_thinking_level(read_fixture):
    sdk, models = _stub_client(text=read_fixture("match_ok.json"))
    client = GeminiLlmClient(client=sdk)
    client.match_requirements("texto", [])
    assert models.kwargs["config"].thinking_config.thinking_level.value.lower() == config.THINKING_MATCH
    sdk, models = _stub_client(text=read_fixture("translate_en.json"))
    GeminiLlmClient(client=sdk).translate({"R1.text": "x"}, "en")
    assert models.kwargs["config"].thinking_config.thinking_level.value.lower() == config.THINKING_TRANSLATE


@pytest.mark.parametrize(
    "kwargs",
    [{"finish": "SAFETY"}, {"finish": "PROHIBITED_CONTENT"}, {"block": "SAFETY"}, {"candidates": False}],
)
def test_gemini_client_turns_blocks_into_a_gentle_refusal(kwargs):
    sdk, _ = _stub_client(text="", **kwargs)
    with pytest.raises(ModelRefusal):
        _extract(sdk)


def test_gemini_client_checks_finish_reason_and_json_before_using_content():
    for kwargs in ({"finish": "MAX_TOKENS", "text": "{}"}, {"text": "isto não é JSON"}, {"text": ""}):
        sdk, _ = _stub_client(**kwargs)
        with pytest.raises(ServiceUnavailable):
            _extract(sdk)


@pytest.mark.parametrize(
    ("code", "message", "expected"),
    [
        (401, "unauthorized", MissingApiKey),
        (403, "forbidden", MissingApiKey),
        (400, "API key not valid. Please pass a valid API key.", MissingApiKey),
        (429, "quota", ServiceUnavailable),
        (500, "boom", ServiceUnavailable),
        (400, "outro problema de requisição", ServiceUnavailable),
    ],
)
def test_gemini_api_errors_map_to_gentle_errors(code, message, expected, monkeypatch):
    monkeypatch.setattr("ats.analysis.llm_client.time.sleep", lambda _s: None)
    error = google_errors.APIError(code, {"error": {"code": code, "message": message}})
    sdk, _ = _stub_client(error=error)
    with pytest.raises(expected):
        _extract(sdk)


def test_transient_overload_is_retried_before_giving_up(monkeypatch, read_fixture):
    sleeps: list[float] = []
    monkeypatch.setattr("ats.analysis.llm_client.time.sleep", sleeps.append)
    overload = google_errors.APIError(503, {"error": {"code": 503, "message": "high demand"}})
    sdk, models = _stub_client(text=read_fixture("extract_ok.json"))
    outcomes = [overload, overload]

    def flaky(**kwargs):
        models.kwargs = kwargs
        if outcomes:
            raise outcomes.pop(0)
        return models.response

    models.generate_content = flaky
    assert len(_extract(sdk).requirements) == 4
    assert sleeps == [2.0, 6.0]


def test_daily_quota_is_reported_without_retrying(monkeypatch):
    sleeps: list[float] = []
    monkeypatch.setattr("ats.analysis.llm_client.time.sleep", sleeps.append)
    message = "Quota exceeded: GenerateRequestsPerDayPerProjectPerModel-FreeTier, limit: 20"
    sdk, _ = _stub_client(error=google_errors.APIError(429, {"error": {"code": 429, "message": message}}))
    with pytest.raises(QuotaExceeded) as caught:
        _extract(sdk)
    assert caught.value.message_key == "error.quota_exceeded" and sleeps == []


def test_persistent_overload_ends_as_service_unavailable(monkeypatch):
    monkeypatch.setattr("ats.analysis.llm_client.time.sleep", lambda _s: None)
    error = google_errors.APIError(503, {"error": {"code": 503, "message": "high demand"}})
    sdk, _ = _stub_client(error=error)
    with pytest.raises(ServiceUnavailable):
        _extract(sdk)


def test_missing_key_is_reported_only_when_calling_the_model(monkeypatch):
    monkeypatch.setattr("ats.analysis.llm_client.resolve_api_key", lambda: None)
    client = GeminiLlmClient()  # criar o cliente não exige a chave
    with pytest.raises(MissingApiKey):
        client.extract_requirements("x" * 120)


def test_api_key_lookup_order(monkeypatch, tmp_path):
    from ats.analysis import llm_client

    secrets = tmp_path / "secrets.toml"
    secrets.write_text('GEMINI_API_KEY = "do-arquivo"\n', encoding="utf-8")
    monkeypatch.setattr(llm_client, "SECRETS_FILE", secrets)
    for name in config.API_KEY_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    assert llm_client.resolve_api_key() == "do-arquivo"
    monkeypatch.setenv("GOOGLE_API_KEY", "da-google")
    assert llm_client.resolve_api_key() == "da-google"
    monkeypatch.setenv("GEMINI_API_KEY", "da-gemini")
    assert llm_client.resolve_api_key() == "da-gemini"
    monkeypatch.setattr(llm_client, "SECRETS_FILE", tmp_path / "nao-existe.toml")
    for name in config.API_KEY_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    assert llm_client.resolve_api_key() is None
