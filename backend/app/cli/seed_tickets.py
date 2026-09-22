# backend/app/cli/seed_tickets.py

from __future__ import annotations

import json
from pathlib import Path

from loguru import logger

from app.db.session import get_session
from app.models.enums import TicketStatus, UserRole
from app.models.ticket import Ticket
from app.models.user import User

TICKET_JSON_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "raw" / "tickets" / "tickets.json"
)

DEMO_USER_EMAIL = "demo@cobaltloop.com"


def _get_or_create_demo_user(db) -> User:
    user = db.query(User).filter(User.email == DEMO_USER_EMAIL).first()
    if user:
        return user
    # placeholder hash, auth will be introducted at a later date
    # exists only to satisy Ticket.user_id's NOT NULL FK for seeding.
    user = User(
        email=DEMO_USER_EMAIL,
        # password is intentionally hardcoded, as this a demo user and haven't implemented auth
        hashed_password="not-a-real-login",
        full_name="Demo User",
        role=UserRole.customer,
    )
    db.add(user)
    db.commit()
    return user


def seed_tickets() -> int:
    db = get_session()
    seeded = 0

    try:
        demo_user = _get_or_create_demo_user(db)

        with open(TICKET_JSON_PATH, "r", encoding="utf-8") as f:
            raw_tickets = json.load(f)

        for raw in raw_tickets:
            subject = raw.get("subject") or "Untitled Ticket"

            # idempotency vai subject match - good enough for this
            # synthetic dataset where subjects are unique in practice.
            if db.query(Ticket).filter_by(subject=subject).first():
                continue

            status_value = raw.get("status") or "open"
            try:
                status = TicketStatus(status_value)
            except ValueError:
                logger.warning(f"Unknown status '{status_value}', defaulting to open.")
                status = TicketStatus.open

            db.add(
                Ticket(
                    user_id=demo_user.id,
                    subject=subject,
                    description=raw.get("description") or "",
                    status=status,
                )
            )
            seeded += 1

        db.commit()
        logger.info(f"Seeded {seeded} new ticket(s).")
        return seeded
    except Exception:
        db.rollback()
        logger.exception("Ticket seeding failed.")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_tickets()
