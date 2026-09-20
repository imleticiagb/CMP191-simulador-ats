"""Chunking: só acima de 20.000 caracteres, blocos de até 8.000 com 500 de sobreposição."""

from __future__ import annotations

import pytest

from ats import config
from ats.domain.errors import TextTooLong
from ats.ingest.chunking import chunk_text, needs_chunking


def _text(chars: int) -> str:
    paragraph = "Trabalhei em projetos de atendimento ao cliente e organização de rotinas. " * 4
    parts, total = [], 0
    while total < chars:
        parts.append(paragraph.strip())
        total += len(paragraph) + 2
    return "\n\n".join(parts)


def test_short_text_is_not_chunked():
    assert not needs_chunking(_text(19_000))
    assert not needs_chunking("a" * config.CHUNK_THRESHOLD_CHARS)


def test_long_text_is_chunked():
    assert needs_chunking("a" * (config.CHUNK_THRESHOLD_CHARS + 1))


def test_chunks_respect_size_and_overlap():
    text = _text(30_000)
    chunks = chunk_text(text)
    assert len(chunks) >= 4
    assert all(len(c.text) <= config.CHUNK_SIZE for c in chunks)
    assert [c.index for c in chunks] == list(range(len(chunks)))
    for previous, current in zip(chunks, chunks[1:], strict=False):
        tail = previous.text[-config.CHUNK_OVERLAP :].strip()
        assert tail[-100:] in current.text[: config.CHUNK_OVERLAP + 200], "falta a sobreposição"


def test_chunks_cut_on_paragraph_boundaries_when_possible():
    chunks = chunk_text(_text(30_000))
    for chunk in chunks[:-1]:
        assert chunk.text.rstrip().endswith("cliente e organização de rotinas.")


def test_every_paragraph_is_covered():
    text = _text(30_000)
    covered = "\n".join(c.text for c in chunk_text(text))
    for paragraph in text.split("\n\n"):
        assert paragraph in covered


def test_text_above_the_hard_limit_is_refused():
    with pytest.raises(TextTooLong):
        chunk_text("a" * (config.MAX_RESUME_CHARS + 1))
