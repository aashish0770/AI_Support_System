from app.services.retrieval.fusion import reciprocal_rank_fusion


def test_rrf_ranks_item_appearing_in_both_lists_highest():
    """Chunk 1 is #2 in list A and #1 in list B — it should outrank chunk 2,
    which only appears in one list at #1."""
    list_a = [
        {"chunk_id": 2, "content": "only in A"},
        {"chunk_id": 1, "content": "in both"},
    ]
    list_b = [
        {"chunk_id": 1, "content": "in both"},
        {"chunk_id": 3, "content": "only in B"},
    ]

    result = reciprocal_rank_fusion([list_a, list_b], k=60)

    assert result[0]["chunk_id"] == 1  # appears in both lists — should win
    assert {r["chunk_id"] for r in result} == {1, 2, 3}


def test_rrf_score_matches_hand_calculation():
    list_a = [{"chunk_id": 1, "content": "x"}]
    result = reciprocal_rank_fusion([list_a], k=60)

    # rank 1 in one list: 1 / (60 + 1)
    assert result[0]["score"] == 1 / 61


def test_rrf_handles_empty_list():
    result = reciprocal_rank_fusion([[], []], k=60)
    assert result == []
