
import io
import zipfile
from pathlib import PurePath

from docx import Document as WordDocument
from openpyxl import load_workbook
from pptx import Presentation
from pypdf import PdfReader


MAX_EXTRACTED_TEXT = 2_000_000
MAX_ARCHIVE_ENTRIES = 2_000
MAX_ARCHIVE_UNCOMPRESSED_SIZE = 50 * 1024 * 1024

SUPPORTED_TYPES = {
    ".pdf": {
        "file_type": "pdf",
        "mime_type": "application/pdf",
    },
    ".docx": {
        "file_type": "docx",
        "mime_type": (
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
    },
    ".txt": {
        "file_type": "txt",
        "mime_type": "text/plain",
    },
    ".pptx": {
        "file_type": "pptx",
        "mime_type": (
            "application/vnd.openxmlformats-officedocument."
            "presentationml.presentation"
        ),
    },
    ".xlsx": {
        "file_type": "xlsx",
        "mime_type": (
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    },
}


class DocumentValidationError(Exception):
    """Raised when an uploaded document is invalid."""


def _check_text_limit(text: str) -> str:
    if len(text) > MAX_EXTRACTED_TEXT:
        raise DocumentValidationError(
            "Extracted document text exceeds the allowed limit."
        )

    return text


def _validate_archive(
    content: bytes,
    required_member: str,
) -> zipfile.ZipFile:
    try:
        archive = zipfile.ZipFile(io.BytesIO(content))

        entries = archive.infolist()

        if len(entries) > MAX_ARCHIVE_ENTRIES:
            raise DocumentValidationError(
                "Office document contains too many archive entries."
            )

        total_size = sum(entry.file_size for entry in entries)

        if total_size > MAX_ARCHIVE_UNCOMPRESSED_SIZE:
            raise DocumentValidationError(
                "Office document expands beyond the allowed limit."
            )

        if any(entry.flag_bits & 0x1 for entry in entries):
            raise DocumentValidationError(
                "Encrypted Office documents are not supported."
            )

        if required_member not in archive.namelist():
            raise DocumentValidationError(
                "Invalid Office document structure."
            )

        corrupt_member = archive.testzip()

        if corrupt_member is not None:
            raise DocumentValidationError(
                "Office document archive is corrupted."
            )

        return archive

    except DocumentValidationError:
        raise
    except (zipfile.BadZipFile, OSError, RuntimeError) as exc:
        raise DocumentValidationError(
            "Invalid or corrupted Office document."
        ) from exc


def validate_and_extract(
    filename: str,
    content: bytes,
) -> tuple[str, str, str]:
    """Validate document contents and extract searchable text."""

    if not filename or PurePath(filename).name != filename:
        raise DocumentValidationError("Invalid filename.")

    extension = PurePath(filename).suffix.lower()

    file_info = SUPPORTED_TYPES.get(extension)

    if file_info is None:
        raise DocumentValidationError(
            "Unsupported file format."
        )

    if not content:
        raise DocumentValidationError("Empty files are not allowed.")

    if extension == ".pdf":
        if not content.startswith(b"%PDF-"):
            raise DocumentValidationError(
                "File content does not match PDF format."
            )

        try:
            reader = PdfReader(io.BytesIO(content), strict=True)

            if reader.is_encrypted:
                raise DocumentValidationError(
                    "Encrypted PDF files are not supported."
                )

            if len(reader.pages) > 500:
                raise DocumentValidationError(
                    "PDF contains too many pages."
                )

            extracted = "\n".join(
                page.extract_text() or ""
                for page in reader.pages
            )

        except DocumentValidationError:
            raise
        except Exception as exc:
            raise DocumentValidationError(
                "Unable to read the PDF document."
            ) from exc

    elif extension == ".txt":
        try:
            extracted = content.decode("utf-8-sig")

            if "\x00" in extracted:
                raise DocumentValidationError(
                    "Invalid text file content."
                )

        except UnicodeDecodeError as exc:
            raise DocumentValidationError(
                "Text files must use UTF-8 encoding."
            ) from exc

    elif extension == ".docx":
        archive = _validate_archive(
            content,
            "word/document.xml",
        )
        archive.close()

        try:
            document = WordDocument(io.BytesIO(content))

            paragraphs = [
                paragraph.text
                for paragraph in document.paragraphs
            ]

            extracted = "\n".join(paragraphs)

            for table in document.tables:
                for row in table.rows:
                    extracted += "\n" + " | ".join(
                        cell.text for cell in row.cells
                    )

        except Exception as exc:
            raise DocumentValidationError(
                "Unable to read the Word document."
            ) from exc

    elif extension == ".pptx":
        archive = _validate_archive(
            content,
            "ppt/presentation.xml",
        )
        archive.close()

        try:
            presentation = Presentation(io.BytesIO(content))

            if len(presentation.slides) > 500:
                raise DocumentValidationError(
                    "Presentation contains too many slides."
                )

            slides = []

            for slide_number, slide in enumerate(
                presentation.slides,
                start=1,
            ):
                slide_text = [
                    shape.text
                    for shape in slide.shapes
                    if shape.has_text_frame and shape.text.strip()
                ]

                slides.append(
                    f"Slide {slide_number}\n"
                    + "\n".join(slide_text)
                )

            extracted = "\n\n".join(slides)

        except DocumentValidationError:
            raise
        except Exception as exc:
            raise DocumentValidationError(
                "Unable to read the PowerPoint presentation."
            ) from exc

    elif extension == ".xlsx":
        archive = _validate_archive(
            content,
            "xl/workbook.xml",
        )
        archive.close()

        try:
            workbook = load_workbook(
                io.BytesIO(content),
                read_only=True,
                data_only=True,
            )

            rows = []

            try:
                for worksheet in workbook.worksheets:
                    rows.append(
                        f"Worksheet: {worksheet.title}"
                    )

                    for row in worksheet.iter_rows(values_only=True):
                        values = [
                            str(value)
                            for value in row
                            if value is not None
                        ]

                        if values:
                            rows.append(" | ".join(values))

                        if sum(map(len, rows)) > MAX_EXTRACTED_TEXT:
                            raise DocumentValidationError(
                                "Extracted document text exceeds the allowed limit."
                            )
            finally:
                workbook.close()

            extracted = "\n".join(rows)

        except DocumentValidationError:
            raise
        except Exception as exc:
            raise DocumentValidationError(
                "Unable to read the Excel workbook."
            ) from exc

    return (
        file_info["file_type"],
        file_info["mime_type"],
        _check_text_limit(extracted),
    )
