# backend/app/api/chat.py

from __future__ import annotations

# this block of code for the direct RAG call:
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse, CitationOut
from app.services.rag.rag_service import answer_question

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    result = answer_question(db, request.message)
    return ChatResponse(
        answer=result.answer,
        citations=[
            CitationOut(
                chunk_id=c.chunk_id,
                document_title=c.document_title,
                relevance_score=c.relevance_score,
            )
            for c in result.citations
        ],
        in_scope=result.in_scope,
        suggested_topics=result.suggested_topics,
    )
"""

# wiring the agent call replace the above code direct RAG call

from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse, CitationOut
from app.services.agent.agent_service import run_agent

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    result = run_agent(request.message)
    return ChatResponse(
        answer=result.answer,
        citations=[
            CitationOut(
                chunk_id=c.chunk_id,
                document_title=c.document_title,
                relevance_score=c.relevance_score,
            )
            for c in result.citations
        ],
    )
