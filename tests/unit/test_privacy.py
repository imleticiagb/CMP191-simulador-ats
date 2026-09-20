"""Privacidade (FR-034, CHK029): nada de currículo ou vaga em logs ou em disco."""

from __future__ import annotations

import logging
from pathlib import Path

from ats.analysis.llm_client import FakeLlmClient
from ats.analysis.pipeline import analyze
from ats.domain.models import ExtractionOutput, MatchOutput
from ats.logging_setup import log_event, short_hash

ROOT = Path(__file__).parent.parent.parent


def test_logs_contain_only_metadata_never_the_texts(read_fixture, caplog):
    job, resume = read_fixture("job_licenciatura.txt"), read_fixture("resume_licenciatura.txt")
    client = FakeLlmClient(
        extract=ExtractionOutput.model_validate_json(read_fixture("extract_ok.json")),
        match=MatchOutput.model_validate_json(read_fixture("match_ok.json")),
    )
    logging.getLogger("ats").propagate = True
    with caplog.at_level(logging.INFO, logger="ats"):
        analyze(job, resume, client)
    logged = "\n".join(r.getMessage() for r in caplog.records)
    assert "stage=analysis_done" in logged
    for fragment in (
        "Maria Souza",
        "maria.souza@email.com",
        "Licenciatura em Pedagogia",
        "Assistente Administrativo",
    ):
        assert fragment not in logged


def test_short_hash_is_short_and_irreversible():
    assert len(short_hash("Maria Souza")) == 10 and "Maria" not in short_hash("Maria Souza")
    log_event("x", size=3)  # só valores simples


def test_source_never_writes_files():
    """Nenhum módulo do app grava em disco (o resultado só existe na sessão)."""
    forbidden = ("write_text(", "write_bytes(", ".write(", "open(", "pickle", "sqlite", "shelve")
    allowed_reads = {"i18n/__init__.py", "ui/components/language_picker.py"}
    for path in (ROOT / "src" / "ats").rglob("*.py"):
        rel = str(path.relative_to(ROOT / "src" / "ats"))
        text = path.read_text(encoding="utf-8").replace("pymupdf.open(stream=", "")  # leitura em memória
        for word in forbidden:
            if word in text and rel not in allowed_reads:
                raise AssertionError(f"{rel} usa {word}")
    for rel in allowed_reads:
        text = (ROOT / "src" / "ats" / rel).read_text(encoding="utf-8")
        assert "write" not in text.replace("read_bytes", ""), f"{rel} não deve escrever"


def test_secrets_are_not_in_the_repository_files():
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".env" in gitignore and ".streamlit/secrets.toml" in gitignore
    for path in [ROOT / "app.py", *(ROOT / "src" / "ats").rglob("*.py")]:
        assert "sk-ant-" not in path.read_text(encoding="utf-8"), path
