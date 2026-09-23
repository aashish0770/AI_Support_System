# backend/app/tests/test_agent_tools.py

import json

from app.services.agent.tools import (
    check_ticket_status,
    get_service_health,
    search_docs,
)


def test_check_ticket_status_finds_seeded_ticket():
    result = json.loads(
        check_ticket_status.invoke({"subject_keyword": "webhook signature"})
    )
    assert result["found"] is True


def test_check_ticket_status_reports_not_found():
    result = json.loads(
        check_ticket_status.invoke({"subject_keyword": "xyz-nonexistent-zzz"})
    )
    assert result["found"] is False


def test_search_docs_finds_relevant_content():
    result = json.loads(search_docs.invoke({"query": "how do I rotate an API key"}))
    assert result["found"] is True


def test_search_docs_reports_out_of_scope():
    result = json.loads(search_docs.invoke({"query": "how can I be spiderman"}))
    assert result["found"] is False


def test_get_service_health_returns_all_services():
    result = json.loads(get_service_health.invoke({}))
    assert "api" in result
