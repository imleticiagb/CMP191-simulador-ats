"""Leitura de PDF: texto, ordem de colunas, erros e métricas de layout (FR-003, FR-004)."""

from __future__ import annotations

import pytest

from ats import config
from ats.domain.errors import InvalidFile, PdfTooLarge, UnreadablePdf
from ats.ingest.pdf_reader import read_pdf
from tests.pdf_factory import (
    encrypted_pdf,
    image_only_pdf,
    image_with_text_pdf,
    many_pages_pdf,
    multi_font_pdf,
    paragraphs_pdf,
    simple_pdf,
    two_column_pdf,
)

LINES = [
    "Maria Souza - maria@email.com",
    "Experiência: atendimento ao cliente por 3 anos.",
    "Formação: Licenciatura em Pedagogia, concluída em 2022.",
]


def test_reads_text_and_basic_metadata():
    content = read_pdf(simple_pdf(LINES), "cv.pdf")
    assert "Licenciatura em Pedagogia" in content.text
    assert content.meta.file_name == "cv.pdf"
    assert content.meta.pages == 1
    assert content.meta.size_bytes > 0
    assert content.meta.font_families == 1
    assert content.meta.column_count == 1
    assert content.meta.has_full_page_image is False


def test_two_columns_keep_reading_order():
    left = [f"Esquerda linha {i}" for i in range(1, 11)]
    right = [f"Direita linha {i}" for i in range(1, 11)]
    content = read_pdf(two_column_pdf(left, right), "cv.pdf")
    text = content.text
    assert text.index("Esquerda linha 10") < text.index("Direita linha 1")
    assert content.meta.column_count == 2


def test_password_protected_pdf_is_unreadable():
    with pytest.raises(UnreadablePdf):
        read_pdf(encrypted_pdf(LINES), "cv.pdf")


def test_image_only_pdf_is_unreadable_and_suggests_pasting():
    with pytest.raises(UnreadablePdf) as caught:
        read_pdf(image_only_pdf(), "scan.pdf")
    assert caught.value.message_key == "error.pdf.unreadable"


def test_corrupted_pdf_is_unreadable():
    with pytest.raises(UnreadablePdf):
        read_pdf(b"%PDF-1.7\nisto nao e um pdf de verdade", "cv.pdf")


@pytest.mark.parametrize("data", [b"", b"texto puro", b"PK\x03\x04conteudo de um docx"])
def test_files_that_are_not_pdf_are_refused(data):
    with pytest.raises(InvalidFile) as caught:
        read_pdf(data, "cv.docx")
    assert caught.value.message_key == "error.pdf.invalid_format"


def test_limits_are_10_pages_and_5_mb():
    assert config.MAX_PDF_PAGES == 10 and config.MAX_PDF_BYTES == 5 * 1024 * 1024
    assert read_pdf(many_pages_pdf(10), "cv.pdf").meta.pages == 10
    with pytest.raises(PdfTooLarge):
        read_pdf(many_pages_pdf(11), "cv.pdf")
    with pytest.raises(PdfTooLarge):
        read_pdf(b"%PDF-1.7\n" + b"0" * config.MAX_PDF_BYTES, "cv.pdf")


def test_font_families_are_counted_without_style_variants():
    assert read_pdf(multi_font_pdf(), "cv.pdf").meta.font_families == 3


def test_body_font_size_is_the_most_common_size():
    content = read_pdf(simple_pdf(LINES * 5, fontsize=10.5), "cv.pdf")
    assert content.meta.body_font_size_median == pytest.approx(10.5, abs=0.1)
    low, high = content.meta.body_font_size_range
    assert low <= 10.5 <= high


def test_margins_in_centimeters():
    wide = read_pdf(simple_pdf(LINES, margin=72), "cv.pdf").meta.min_margin_cm
    narrow = read_pdf(simple_pdf(LINES, margin=14), "cv.pdf").meta.min_margin_cm
    assert 1.5 < wide < 2.7
    assert narrow < 1.0 < wide


def test_full_page_image_is_detected_even_with_some_text():
    content = read_pdf(image_with_text_pdf(LINES * 4), "cv.pdf")
    assert content.meta.has_full_page_image is True


def test_text_density_is_a_fraction_of_the_page():
    sparse = read_pdf(simple_pdf(LINES), "cv.pdf").meta.text_density
    dense = read_pdf(paragraphs_pdf(["Texto denso de exemplo. " * 16] * 7), "cv.pdf").meta.text_density
    assert 0 <= sparse < dense <= 1
