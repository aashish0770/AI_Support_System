# backend/tests/test_agent_service.py

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.services.agent.agent_service import extract_citations, extract_tool_names


def test_extract_citations_parses_search_docs_tool_message():
    messages = [
        HumanMessage(content="how do I rotate an API key"),
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "search_docs",
                    "args": {"query": "rotate api key"},
                    "id": "call_1",
                }
            ],
        ),
        ToolMessage(
            content='{"found": true, "results": [{"chunk_id": 5, "document_title": "Authentication & API Keys", "content": "...", "relevance_score": 0.03}]}',
            name="search_docs",
            tool_call_id="call_1",
        ),
        AIMessage(content="You can rotate your key from Settings."),
    ]
    citations = extract_citations(messages)
    assert len(citations) == 1
    assert citations[0].document_title == "Authentication & API Keys"


def test_extract_citations_ignores_not_found_results():
    messages = [
        ToolMessage(
            content='{"found": false, "message": "nothing relevant"}',
            name="search_docs",
            tool_call_id="1",
        )
    ]
    assert extract_citations(messages) == []


def test_extract_citations_ignores_other_tools():
    messages = [
        ToolMessage(
            content='{"found": true, "subject": "x", "status": "open"}',
            name="check_ticket_status",
            tool_call_id="1",
        )
    ]
    assert extract_citations(messages) == []


def test_extract_tool_names_collects_all_calls_and_skips_final_answer():
    messages = [
        AIMessage(
            content="", tool_calls=[{"name": "search_docs", "args": {}, "id": "1"}]
        ),
        AIMessage(
            content="",
            tool_calls=[{"name": "check_ticket_status", "args": {}, "id": "2"}],
        ),
        AIMessage(content="final answer"),  # no tool_calls — must not appear
    ]
    assert extract_tool_names(messages) == ["search_docs", "check_ticket_status"]
