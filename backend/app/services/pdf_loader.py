from pypdf import PdfReader


# ==================================================
# EXTRACT PDF TEXT
# ==================================================

def extract_text_from_pdf(file_path):
    """
    Extract text from all pages of a PDF.
    """

    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            pages.append(page_text.strip())

    return "\n\n".join(pages)


# ==================================================
# SPLIT TEXT INTO CHUNKS
# ==================================================

def split_text_into_chunks(
    text,
    chunk_size=1000,
    chunk_overlap=200
):
    """
    Split extracted PDF text into overlapping chunks.
    """

    if not text:
        return []

    text = text.strip()

    if not text:
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size"
        )

    chunks = []

    start = 0

    text_length = len(text)

    while start < text_length:

        end = min(
            start + chunk_size,
            text_length
        )

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - chunk_overlap

    print()
    print("========== TEXT CHUNKING ==========")
    print("Text length:", text_length)
    print("Chunk size:", chunk_size)
    print("Chunk overlap:", chunk_overlap)
    print("Total chunks:", len(chunks))
    print("===================================")
    print()

    return chunks