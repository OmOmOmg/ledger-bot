from sqlmodel import SQLModel, Field, create_engine, Session
import os
import db

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)

#DB Models

# tg_user: canonical participant list (username PK)
class TgUser(SQLModel, table=True):
    __tablename__ = "tg_user"
    username: str = Field(primary_key=True)

# pool_entry: append-only journal of "paid"/"share" events
class PoolEntry(SQLModel, table=True):
    __tablename__ = "pool_entry"
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(foreign_key="tg_user.username", nullable=False)
    kind: str = Field(nullable=False) # "paid" or "share"
    amount_din: int = Field(nullable=False)

def record_debt(bot, message, creditor: str, debtor: str, amount: int, msg_id: int):
    with db.get_session() as session:
        # ensure users exist
        for u in {creditor, debtor}:
            if session.get(db.TgUser, u) is None:
                session.add(db.TgUser(username=u))
