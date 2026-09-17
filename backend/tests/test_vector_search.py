import pytest

from app.services.vectorstore.embeddings import EMBEDDING_DIM, embed_query, embed_texts


def test_embed_texts_returns_correct_shape():
    vectors = embed_texts(["hello world", "second document"])

    assert len(vectors) == 2
    assert all(len(v) == EMBEDDING_DIM for v in vectors)


def test_embed_query_returns_single_vector():
    vector = embed_query("how do I rotate an API key")

    assert len(vector) == EMBEDDING_DIM
    assert all(isinstance(value, float) for value in vector)


def test_embeddings_are_normalized():
    """normalize_embeddings=True is what makes the cosine distance metric
    configured on the Chroma collection behave predictably — if this
    breaks, ranking quality degrades silently rather than erroring."""
    vector = embed_query("test")
    magnitude = sum(value * value for value in vector) ** 0.5

    assert magnitude == pytest.approx(1.0, abs=1e-5)
