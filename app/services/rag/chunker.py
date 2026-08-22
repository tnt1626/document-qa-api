def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Split text into chunks
    Args:
        text (str): text input
        chunk_size (int): size of a chunk
        overlap (int): the size that two chunks overlap

    Returns:
        list[str]: list of chunks
    """
    if not text:
        return []

    chunks = []
    start = 0
    len_text = len(text)
    while start <= len_text:
        end = start + chunk_size
        chunks.append(text[start:end])
        if end >= len_text:
            break
        start += chunk_size - overlap
    return chunks