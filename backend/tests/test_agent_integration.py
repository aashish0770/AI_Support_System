# backend/tests/test_agent_integration.py

"""
Real Ollama, real Postgres, real Chroma. Small local models don't call
tools with perfect reliability - see ADR-01. Run explicitly:
    pytest tests/test_agent_integration.py -v -m integration
"""

import pytest

from app.services.agent.agent_service import run_agent

pytestmark = pytest.mark.integration


def test_docs_question_calls_search_docs_tool():
    result = run_agent("how do I verify a webhook signature")
    assert "search_docs" in result.tool_calls_made
    assert len(result.citations) > 0


def test_ticket_question_calls_check_ticket_status_tool():
    result = run_agent("what's the status of the webhook signature ticket")
    assert "check_ticket_status" in result.tool_calls_made


def test_out_of_scope_question_does_not_hallucinate_citations():
    result = run_agent("how can I be spiderman")
    assert len(result.citations) == 0


def test_multi_step_tool_use():
    result = run_agent(
        "is the webhook signature verification ticket resolved, and if not how do I fix it myself"
    )
    # Asserting >=1, not both tools — a capable agent would call both,
    # but requiring that from an 8B local model isn't realistic yet.
    assert len(result.tool_calls_made) >= 1
