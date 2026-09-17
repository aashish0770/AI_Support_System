from app.services.retrieval import hybrid_search as hybrid_search_module


def test_hybrid_search_merges_and_truncates(monkeypatch):
    def fake_vector_search(query, top_k):
        return [
            {"chunk_id": 1, "content": "vector result 1", "distance": 0.1},
            {"chunk_id": 2, "content": "vector result 2", "distance": 0.2},
        ]

    def fake_keyword_search(db, query, top_k):
        return [
            {"chunk_id": 1, "content": "vector result 1", "rank": 0.9},
        ]

    monkeypatch.setattr(hybrid_search_module, "vector_search", fake_vector_search)
    monkeypatch.setattr(hybrid_search_module, "keyword_search", fake_keyword_search)

    result = hybrid_search_module.hybrid_search(db=None, query="anything", top_k=1)

    assert len(result) == 1
    # chunk_id 1 appears in both fake lists, so it should win the fusion
    assert result[0]["chunk_id"] == 1
