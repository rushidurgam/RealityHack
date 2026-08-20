"""Safe PDF text extraction with magic-byte pre-flight check and page bounds."""

from io import BytesIO
from pypdf import PdfReader

from app.config import settings
from app.core.security import InputSanitizer, validate_pdf_bytes


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Validate PDF format and return concatenated sanitized text from pages."""
    is_valid, err_msg = validate_pdf_bytes(file_bytes, max_bytes=settings.max_upload_bytes)
    if not is_valid:
        raise ValueError(err_msg)

    pages: list[str] = []
    try:
        reader = PdfReader(BytesIO(file_bytes), strict=False)
        for page in reader.pages[: settings.max_pdf_pages]:
            try:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    pages.append(page_text.strip())
            except Exception:
                continue
    except Exception:
        # If reader fails to parse specific malformed objects, proceed gracefully
        pass

    text = "\n\n".join(pages)
    return InputSanitizer.sanitize_text(text, max_chars=settings.max_text_chars)
