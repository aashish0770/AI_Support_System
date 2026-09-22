# backend/tests/test_rag_service.py

from app.services.rag.rag_service import (
    OUT_OF_SCOPE_DISTANCE_THRESHOLD,
    _is_out_of_scope,
)


def test_is_out_of_scope_true_for_high_distance():
    results = [{"chunk_id": 1, "content": "x", "distance": 0.9}]
    assert _is_out_of_scope(results) is True


def test_is_out_of_scope_false_for_low_distance():
    results = [{"chunk_id": 1, "content": "x", "distance": 0.2}]
    assert _is_out_of_scope(results) is False


def test_is_out_of_scope_true_for_empty_results():
    assert _is_out_of_scope([]) is True


def test_uses_best_distance_among_multiple_results():
    # One good match among several bad ones should NOT be flagged out of
    # scope — this is what "best_distance = min(...)" is checking.
    results = [
        {"chunk_id": 1, "content": "x", "distance": 0.9},
        {"chunk_id": 2, "content": "y", "distance": 0.1},
    ]
    assert _is_out_of_scope(results) is False
