import os
from sqlmodel import SQLModel, create_engine, Session, Field, select
from datetime import datetime, timezone

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True  # verify & reconnect before use
)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)


# DB Model
class PoolEntry(SQLModel, table=True):
    __tablename__ = "pool_entry"
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(nullable=False)
    kind: str = Field(nullable=False)  # "paid" or "share"
    amount_din: int = Field(nullable=False)
    telegram_message_id: int | None = Field(default=None, index=True)
    counterparty: str | None = Field(default=None)
    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# def record_debt(username: str, kind: str, amount_din: int, counterparty: str | None) -> bool:
#     try:
#         with get_session() as session:
#             session.exec(select(1))
#             entry = PoolEntry(
#                 username=username,
#                 kind=kind,
#                 amount_din=amount_din,
#                 counterparty=counterparty,
#             )
#             session.add(entry)
#             session.commit()
#
#         return True
#
#     except Exception as e:
#         print("DB ERROR:", e)
#         return False


def record_transfer(
        debtor: str,
        kind: str,
        amount_din: int,
        creditor: str,
        message_id: int,
) -> str:
    try:
        with get_session() as session:

            existing = session.exec(
                select(PoolEntry).where(
                    PoolEntry.telegram_message_id == message_id
                )
            ).first()

            if existing:
                print(f"Duplicate Telegram message ignored: {message_id}")
                return "duplicate"

            opposite_kind = "share" if kind == "paid" else "paid"

            session.add(PoolEntry(
                username=debtor,
                kind=kind,
                amount_din=amount_din,
                counterparty=creditor,
                telegram_message_id=message_id,
            ))

            session.add(PoolEntry(
                username=creditor,
                kind=opposite_kind,
                amount_din=amount_din,
                counterparty=debtor,
                telegram_message_id=message_id,
            ))

            session.commit()
            return "created"

    except Exception as e:
        print("DB ERROR:", e)
        return "error"


def my_balance(username: str):
    with get_session() as session:
        entries = session.exec(
            select(PoolEntry).where(PoolEntry.username == username)
        ).all()

    net = 0
    for e in entries:
        if e.kind == "paid":
            net += e.amount_din
        elif e.kind == "share":
            net -= e.amount_din
    return net


def all_usernames() -> list[str]:
    with get_session() as session:
        rows = session.exec(select(PoolEntry.username).distinct()).all()
    return [r for r in rows]


def transactions_with_running_balance(username: str):
    with get_session() as session:
        rows = session.exec(
            select(PoolEntry)
            .where(PoolEntry.username == username)
            .order_by(PoolEntry.id)
        ).all()

    running = 0
    result = []
    for r in rows:
        if r.kind == "paid":
            running += r.amount_din
        else:
            running -= r.amount_din

        result.append((r, running))

    return result
