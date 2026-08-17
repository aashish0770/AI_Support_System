from typing import Any, Dict, List, Optional

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNK_SIZE_TOKENS = 500
CHUNK_OVERLAP_TOKENS = 50

# Not using OpenAI for generation, but cl100k_base is still a reasonable,
# free, local proxy for token counting — the plan calls for ~500-token
# chunks, not 500 *characters*, and character length under- or over-counts
# depending on how token-dense the source text is (code blocks and JSON in
# the docs, for instance, tokenize very differently than prose).
_encoding = tiktoken.get_encoding("cl100k_base")


def _token_length(text: str) -> int:
    return len(_encoding.encode(text))


_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE_TOKENS,
    chunk_overlap=CHUNK_OVERLAP_TOKENS,
    length_function=_token_length,
)


def split_text(
    text: str,
    extra_metadata: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Split text into chunks with metadata.

    Returns a list of dicts shaped as:
        {"content": str, "chunk_index": int, "metadata": dict}
    This shape is what base_loader.create_document_with_chunks expects —
    if you change this return shape, update that consumer too.
    """
    if not text.strip():
        return []

    chunks = _splitter.split_text(text)

    return [
        {
            "content": chunk,
            "chunk_index": idx,
            "metadata": extra_metadata or {},
        }
        for idx, chunk in enumerate(chunks)
    ]
