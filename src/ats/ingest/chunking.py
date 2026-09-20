"""Divisão de currículos muito longos em blocos por parágrafo, com sobreposição (pesquisa D3).

Cada bloco é um trecho contíguo do texto original, então toda evidência de um bloco também é evidência
literal do currículo inteiro.
"""

from __future__ import annotations

import re

from ats import config
from ats.domain.errors import TextTooLong
from ats.domain.models import Chunk

_PARAGRAPH = re.compile(r"\S.*?(?=\n\s*\n|\Z)", re.DOTALL)


def needs_chunking(text: str) -> bool:
    return len(text) > config.CHUNK_THRESHOLD_CHARS


def _paragraph_spans(text: str) -> list[tuple[int, int]]:
    """Intervalos (início, fim) de cada parágrafo. Parágrafos longos demais são cortados em espaços."""
    limit = config.CHUNK_SIZE - config.CHUNK_OVERLAP
    spans: list[tuple[int, int]] = []
    for match in _PARAGRAPH.finditer(text):
        start, end = match.start(), match.end()
        while end - start > limit:
            cut = text.rfind(" ", start, start + limit)
            cut = cut if cut > start else start + limit
            spans.append((start, cut))
            start = cut + 1 if text[cut : cut + 1] == " " else cut
        spans.append((start, end))
    return spans


def chunk_text(text: str) -> list[Chunk]:
    """Blocos de até `CHUNK_SIZE` caracteres, cada um com a cauda do anterior (até `CHUNK_OVERLAP`)."""
    if len(text) > config.MAX_RESUME_CHARS:
        raise TextTooLong("error.resume.too_long")
    if not needs_chunking(text):
        return [Chunk(index=0, text=text)]

    spans = _paragraph_spans(text)
    chunks: list[Chunk] = []
    first = 0  # índice do primeiro parágrafo do bloco
    while first < len(spans):
        start = spans[first][0]
        last = first
        while last + 1 < len(spans) and spans[last + 1][1] - start <= config.CHUNK_SIZE:
            last += 1
        end = spans[last][1]
        chunks.append(Chunk(index=len(chunks), text=text[start:end]))
        if last + 1 >= len(spans):
            break
        # o próximo bloco recomeça no primeiro parágrafo que caiba na sobreposição (pode ser nenhum)
        next_first = last + 1
        for i in range(last, first, -1):
            if end - spans[i][0] <= config.CHUNK_OVERLAP:
                next_first = i
            else:
                break
        first = next_first
    return chunks
