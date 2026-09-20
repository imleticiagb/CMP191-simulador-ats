"""Leitura de PDF com PyMuPDF: texto em ordem de leitura e métricas de layout para a nota de Design.

PyMuPDF é AGPL-3.0: serve para este trabalho acadêmico não publicado (pesquisa D2). Se o projeto for
publicado, trocar por `pdfplumber` (MIT).
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from statistics import median

import pymupdf

from ats import config
from ats.domain.errors import InvalidFile, PdfTooLarge, UnreadablePdf
from ats.domain.models import PdfMeta

MIN_TEXT_CHARS = 50
PT_TO_CM = 2.54 / 72
FULL_PAGE_IMAGE_RATIO = 0.9


@dataclass(frozen=True)
class PdfContent:
    text: str
    meta: PdfMeta


def _family(font_name: str) -> str:
    """Família da fonte, sem prefixo de subconjunto e sem variação de estilo (Helvetica-Bold = Helvetica)."""
    name = re.sub(r"^[A-Z]{6}\+", "", font_name)
    return re.split(r"[-,]", name)[0].replace(" ", "").lower()


def _text_blocks(page: pymupdf.Page) -> list[tuple[float, float, float, float, str]]:
    blocks = page.get_text("blocks")
    return [(b[0], b[1], b[2], b[3], b[4]) for b in blocks if b[6] == 0 and b[4].strip()]


def _split_columns(blocks: list[tuple[float, float, float, float, str]], width: float):
    """Devolve (blocos em ordem de leitura, número de colunas).

    Duas colunas: nenhum bloco atravessa o meio da página e há texto relevante de cada lado. Então a coluna
    esquerda é lida inteira antes da direita. Caso contrário, a ordem é de cima para baixo.
    """
    mid = width / 2
    left = [b for b in blocks if b[2] <= mid + 5]
    right = [b for b in blocks if b[0] >= mid - 5]
    substantial = all(sum(len(b[4]) for b in side) >= 30 for side in (left, right))
    if left and right and len(left) + len(right) == len(blocks) and substantial:
        ordered = sorted(left, key=lambda b: (b[1], b[0])) + sorted(right, key=lambda b: (b[1], b[0]))
        return ordered, 2
    return sorted(blocks, key=lambda b: (round(b[1]), b[0])), 1


def _page_metrics(page: pymupdf.Page, blocks) -> dict:
    width, height = page.rect.width, page.rect.height
    area = width * height
    text_area = sum(max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1]) for b in blocks)
    images = [pymupdf.Rect(i["bbox"]) for i in page.get_image_info()]
    full_image = any((r & page.rect).get_area() / area >= FULL_PAGE_IMAGE_RATIO for r in images)
    if blocks:
        margins = [
            min(b[0] for b in blocks),
            width - max(b[2] for b in blocks),
            min(b[1] for b in blocks),
            height - max(b[3] for b in blocks),
        ]
        min_margin = max(0.0, min(margins)) * PT_TO_CM
    else:
        min_margin = 0.0
    return {"density": min(1.0, text_area / area), "full_image": full_image, "margin": min_margin}


def read_pdf(data: bytes, file_name: str) -> PdfContent:
    """Extrai texto e métricas. Levanta erros com mensagem gentil por chave de i18n."""
    if len(data) > config.MAX_PDF_BYTES:
        raise PdfTooLarge()
    if not data.startswith(b"%PDF-"):
        raise InvalidFile()
    try:
        doc = pymupdf.open(stream=data, filetype="pdf")
    except Exception as exc:
        raise UnreadablePdf() from exc

    with doc:
        if doc.needs_pass or doc.is_encrypted:
            raise UnreadablePdf()
        if doc.page_count > config.MAX_PDF_PAGES:
            raise PdfTooLarge()
        if doc.page_count == 0:
            raise UnreadablePdf()

        texts: list[str] = []
        columns = 1
        page_metrics: list[dict] = []
        sizes: Counter[float] = Counter()
        all_sizes: list[float] = []
        families: set[str] = set()
        try:
            for page in doc:
                blocks = _text_blocks(page)
                ordered, cols = _split_columns(blocks, page.rect.width)
                columns = max(columns, cols)
                texts.append("\n".join(b[4].strip() for b in ordered))
                page_metrics.append(_page_metrics(page, blocks))
                for block in page.get_text("dict")["blocks"]:
                    for line in block.get("lines", []):
                        for span in line["spans"]:
                            chars = len(span["text"].strip())
                            if chars:
                                size = round(span["size"], 1)
                                sizes[size] += chars
                                all_sizes.append(size)
                                families.add(_family(span["font"]))
        except Exception as exc:
            raise UnreadablePdf() from exc
        pages = doc.page_count

    text = "\n\n".join(t for t in texts if t)
    if len(text.strip()) < MIN_TEXT_CHARS:
        raise UnreadablePdf()

    expanded = [s for s, n in sizes.items() for _ in range(n)]
    meta = PdfMeta(
        file_name=file_name,
        pages=pages,
        size_bytes=len(data),
        font_families=len(families),
        body_font_size_range=(min(all_sizes), max(all_sizes)),
        body_font_size_median=float(median(expanded)),
        min_margin_cm=round(min(m["margin"] for m in page_metrics), 2),
        text_density=round(sum(m["density"] for m in page_metrics) / len(page_metrics), 3),
        has_full_page_image=any(m["full_image"] for m in page_metrics),
        column_count=columns,
    )
    return PdfContent(text=text, meta=meta)
