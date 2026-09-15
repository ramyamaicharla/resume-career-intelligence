"""Resume parsing service using PyMuPDF."""
from typing import Dict, Any
import pymupdf


def extract_text_from_pdf(file_bytes: bytes) -> Dict[str, Any]:
    """Extract text and page count from raw PDF bytes using PyMuPDF.

    Args:
        file_bytes: The binary content of the PDF file.

    Returns:
        Dict containing page count and extracted combined text.

    Raises:
        ValueError: If file is empty, corrupted, or not a valid PDF.
    """
    if not file_bytes or len(file_bytes) == 0:
        raise ValueError("Uploaded file is empty.")

    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise ValueError(f"Failed to parse PDF document: {str(exc)}") from exc

    try:
        page_count = doc.page_count
        if page_count == 0:
            raise ValueError("PDF document contains no pages.")

        page_texts = []
        for page_num in range(page_count):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text:
                page_texts.append(text.strip())

        combined_text = "\n\n".join(page_texts).strip()

        return {
            "pages": page_count,
            "text": combined_text,
        }
    finally:
        doc.close()
