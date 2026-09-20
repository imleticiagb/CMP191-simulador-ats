"""Gera PDFs de teste na hora com PyMuPDF (sem arquivos binários no repositório)."""

from __future__ import annotations

import pymupdf

A4 = (595, 842)


def _new_doc() -> pymupdf.Document:
    return pymupdf.open()


def _bytes(doc: pymupdf.Document, **save_kwargs) -> bytes:
    data = doc.tobytes(**save_kwargs)
    doc.close()
    return data


def simple_pdf(
    lines: list[str], *, fontname: str = "helv", fontsize: float = 11, margin: float = 72
) -> bytes:
    doc = _new_doc()
    page = doc.new_page(width=A4[0], height=A4[1])
    y = margin
    for line in lines:
        page.insert_text((margin, y), line, fontname=fontname, fontsize=fontsize)
        y += fontsize * 1.6
    return _bytes(doc)


def paragraphs_pdf(
    paragraphs: list[str], *, pages: int = 1, fontname: str = "helv", fontsize: float = 11
) -> bytes:
    """Cada página recebe todos os parágrafos, cada um em uma caixa de texto (um bloco por parágrafo)."""
    doc = _new_doc()
    for _ in range(pages):
        page = doc.new_page(width=A4[0], height=A4[1])
        y = 72.0
        for text in paragraphs:
            rect = pymupdf.Rect(72, y, A4[0] - 72, y + 100)
            page.insert_textbox(rect, text, fontname=fontname, fontsize=fontsize)
            y += 102
    return _bytes(doc)


def two_column_pdf(left: list[str], right: list[str]) -> bytes:
    doc = _new_doc()
    page = doc.new_page(width=A4[0], height=A4[1])
    page.insert_textbox(pymupdf.Rect(50, 72, 280, 700), "\n".join(left), fontname="helv", fontsize=11)
    page.insert_textbox(pymupdf.Rect(320, 72, 545, 700), "\n".join(right), fontname="helv", fontsize=11)
    return _bytes(doc)


def multi_font_pdf() -> bytes:
    doc = _new_doc()
    page = doc.new_page(width=A4[0], height=A4[1])
    for i, font in enumerate(["helv", "tiro", "cour"]):
        page.insert_text(
            (72, 100 + i * 30), f"Texto em {font} para medir famílias de fonte", fontname=font, fontsize=11
        )
    return _bytes(doc)


def image_only_pdf() -> bytes:
    doc = _new_doc()
    page = doc.new_page(width=A4[0], height=A4[1])
    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 60, 80), False)
    pix.set_rect(pix.irect, (200, 200, 200))
    page.insert_image(page.rect, pixmap=pix)
    return _bytes(doc)


def image_with_text_pdf(lines: list[str]) -> bytes:
    doc = _new_doc()
    page = doc.new_page(width=A4[0], height=A4[1])
    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 60, 80), False)
    pix.set_rect(pix.irect, (240, 240, 240))
    page.insert_image(page.rect, pixmap=pix)
    y = 72.0
    for line in lines:
        page.insert_text((72, y), line, fontname="helv", fontsize=11)
        y += 18
    return _bytes(doc)


def encrypted_pdf(lines: list[str]) -> bytes:
    doc = _new_doc()
    page = doc.new_page(width=A4[0], height=A4[1])
    page.insert_text((72, 72), "\n".join(lines), fontname="helv", fontsize=11)
    return _bytes(doc, encryption=pymupdf.PDF_ENCRYPT_AES_256, user_pw="segredo", owner_pw="dono")


def many_pages_pdf(pages: int) -> bytes:
    doc = _new_doc()
    for i in range(pages):
        page = doc.new_page(width=A4[0], height=A4[1])
        page.insert_text(
            (72, 72), f"Página {i + 1}: currículo com texto suficiente para leitura.", fontname="helv"
        )
    return _bytes(doc)
