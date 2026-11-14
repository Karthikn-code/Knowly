
import io

import pytest
from docx import Document as WordDocument
from openpyxl import Workbook
from pptx import Presentation
from pypdf import PdfWriter

from app.services import document_validation
from app.services.document_validation import (
    DocumentValidationError,
    validate_and_extract,
)


def make_txt():
    return "Knowly document assistant test content.".encode("utf-8")


def make_pdf():
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)

    output = io.BytesIO()
    writer.write(output)

    return output.getvalue()


def make_docx():
    document = WordDocument()
    document.add_paragraph("Knowly Word document content.")

    table = document.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "Document"
    table.cell(0, 1).text = "Assistant"

    output = io.BytesIO()
    document.save(output)

    return output.getvalue()


def make_pptx():
    presentation = Presentation()
    slide = presentation.slides.add_slide(
        presentation.slide_layouts[5]
    )

    textbox = slide.shapes.add_textbox(
        100000,
        100000,
        5000000,
        1000000,
    )
    textbox.text = "Knowly presentation content."

    output = io.BytesIO()
    presentation.save(output)

    return output.getvalue()


def make_xlsx():
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Knowly Data"

    worksheet.append(["Document", "Assistant"])
    worksheet.append(["Knowly", "AI"])

    output = io.BytesIO()
    workbook.save(output)

    return output.getvalue()


@pytest.mark.parametrize(
    ("filename", "content_factory", "expected_type", "expected_text"),
    [
        (
            "notes.txt",
            make_txt,
            "txt",
            "Knowly document assistant test content.",
        ),
        (
            "report.pdf",
            make_pdf,
            "pdf",
            "",
        ),
        (
            "report.docx",
            make_docx,
            "docx",
            "Knowly Word document content.",
        ),
        (
            "slides.pptx",
            make_pptx,
            "pptx",
            "Knowly presentation content.",
        ),
        (
            "data.xlsx",
            make_xlsx,
            "xlsx",
            "Knowly Data",
        ),
    ],
)
def test_supported_formats_are_validated_and_extracted(
    filename,
    content_factory,
    expected_type,
    expected_text,
):
    file_type, mime_type, extracted = validate_and_extract(
        filename,
        content_factory(),
    )

    assert file_type == expected_type
    assert mime_type == document_validation.SUPPORTED_TYPES[
        f".{expected_type}"
    ]["mime_type"]

    if expected_text:
        assert expected_text in extracted


def test_docx_table_content_is_extracted():
    _, _, extracted = validate_and_extract(
        "table.docx",
        make_docx(),
    )

    assert "Document | Assistant" in extracted


def test_pptx_slide_number_is_preserved():
    _, _, extracted = validate_and_extract(
        "slides.pptx",
        make_pptx(),
    )

    assert "Slide 1" in extracted


def test_xlsx_cell_values_are_extracted():
    _, _, extracted = validate_and_extract(
        "data.xlsx",
        make_xlsx(),
    )

    assert "Document | Assistant" in extracted
    assert "Knowly | AI" in extracted


def test_empty_file_is_rejected():
    with pytest.raises(
        DocumentValidationError,
        match="Empty files",
    ):
        validate_and_extract("notes.txt", b"")


def test_unsupported_extension_is_rejected():
    with pytest.raises(
        DocumentValidationError,
        match="Unsupported file format",
    ):
        validate_and_extract("notes.csv", b"some,data")


def test_invalid_filename_is_rejected():
    with pytest.raises(
        DocumentValidationError,
        match="Invalid filename",
    ):
        validate_and_extract("../notes.txt", make_txt())


def test_invalid_utf8_text_is_rejected():
    with pytest.raises(
        DocumentValidationError,
        match="UTF-8",
    ):
        validate_and_extract("notes.txt", b"\xff\xfe\xfa")


def test_null_bytes_in_text_are_rejected():
    with pytest.raises(
        DocumentValidationError,
        match="Invalid text file content",
    ):
        validate_and_extract("notes.txt", b"hello\x00world")


def test_invalid_pdf_signature_is_rejected():
    with pytest.raises(
        DocumentValidationError,
        match="does not match PDF",
    ):
        validate_and_extract("report.pdf", b"not a PDF")


def test_corrupted_pdf_is_rejected():
    with pytest.raises(
        DocumentValidationError,
        match="Unable to read the PDF",
    ):
        validate_and_extract(
            "report.pdf",
            b"%PDF-1.7\ninvalid document data",
        )


@pytest.mark.parametrize(
    "filename",
    ["report.docx", "slides.pptx", "data.xlsx"],
)
def test_corrupted_office_archive_is_rejected(filename):
    with pytest.raises(
        DocumentValidationError,
        match="Invalid or corrupted Office",
    ):
        validate_and_extract(
            filename,
            b"not a valid ZIP archive",
        )


def test_extracted_text_limit_is_enforced(monkeypatch):
    monkeypatch.setattr(
        document_validation,
        "MAX_EXTRACTED_TEXT",
        10,
    )

    with pytest.raises(
        DocumentValidationError,
        match="exceeds the allowed limit",
    ):
        validate_and_extract(
            "notes.txt",
            b"This text is longer than ten characters.",
        )


def test_encrypted_pdf_is_rejected():
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)
    writer.encrypt("test-password")

    output = io.BytesIO()
    writer.write(output)

    with pytest.raises(
        DocumentValidationError,
        match="Encrypted PDF",
    ):
        validate_and_extract(
            "private.pdf",
            output.getvalue(),
        )
