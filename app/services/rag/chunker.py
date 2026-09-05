import re

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Split text into fixed-size character chunks.

    Args:
        text (str): Input text.
        chunk_size (int): Character length of each chunk.
        overlap (int): Number of overlapping characters between adjacent chunks.

    Returns:
        list[str]: List of text chunks.
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

def split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences for mixed Vietnamese/English content.

    Splits at sentence boundary punctuation (.!?) while preventing false
    splits on decimals, abbreviations, and ellipses.

    Args:
        text (str): Input text.

    Returns:
        list[str]: List of extracted sentences.
    """
    text = re.sub(r'(\d)\.(\d)', r'\1<DECIMAL>\2', text)
    text = re.sub(r'\.{2,}', '<ELLIPSIS>', text)
    
    abbreviations = ['Mr', 'Mrs', 'Ms', 'Dr', 'Prof', 'Sr', 'Jr',
                     'vs', 'etc', 'e.g', 'i.e', 'Fig', 'fig',
                     'No', 'Vol', 'Jan', 'Feb', 'Mar', 'Apr',
                     'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for abbr in abbreviations:
        text = re.sub(
            rf'\b{abbr}\.',
            f'{abbr}<ABBR>',
            text,
            flags=re.IGNORECASE
        )
    
    sentences = re.split(r'([.!?])\s+', text)
    
    result = []
    i = 0
    while i < len(sentences):
        if i + 1 < len(sentences) and sentences[i + 1] in '.!?':
            merged = sentences[i] + sentences[i + 1]
            result.append(merged.strip())
            i += 2
        else:
            if sentences[i].strip():
                result.append(sentences[i].strip())
            i += 1
    
    restored = []
    for s in result:
        s = s.replace('<DECIMAL>', '.')
        s = s.replace('<ELLIPSIS>', '...')
        s = s.replace('<ABBR>', '.')
        restored.append(s)
    
    return [s for s in restored if s.strip()]


def chunk_by_sentences(
    text: str,
    max_chars: int = 500,
    overlap_sentences: int = 1
) -> list[str]:
    """
    Chunk text along sentence boundaries.

    Args:
        text (str): Input text.
        max_chars (int): Soft character limit for each chunk.
        overlap_sentences (int): Number of overlapping sentences between chunks to preserve context.

    Returns:
        list[str]: List of sentence-aligned text chunks.
    """
    if not text:
        return []
    
    sentences = split_into_sentences(text)
    
    if not sentences:
        return []
    
    chunks = []
    current_sentences = []
    current_chars = 0
    
    for sentence in sentences:
        sentence_chars = len(sentence)
        
        if not current_sentences:
            current_sentences.append(sentence)
            current_chars += sentence_chars
            continue
        
        if current_chars + sentence_chars > max_chars:
            chunks.append(" ".join(current_sentences))
            
            num_overlap = min(overlap_sentences, max(0, len(current_sentences) - 1))
            if num_overlap > 0:
                current_sentences = current_sentences[-num_overlap:]
                current_chars = sum(len(s) for s in current_sentences)
            else:
                current_sentences = []
                current_chars = 0
        
        current_sentences.append(sentence)
        current_chars += sentence_chars
    
    if current_sentences:
        chunks.append(" ".join(current_sentences))
    
    return chunks