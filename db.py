import os
import db
from sqlmodel import SQLModel, create_engine, Session, Field, select

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)

#DB Model
class PoolEntry(SQLModel, table=True):
    __tablename__ = "pool_entry"
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(foreign_key="tg_user.username", nullable=False)
    kind: str = Field(nullable=False) # "paid" or "share"
    amount_din: int = Field(nullable=False)

def record_debt(bot, message, id: int, username: str, kind: str, amount_din: int, ):
    with db.get_session() as session: # ensure users exist
        entry = PoolEntry(
            id=id,
            username=username,
            kind=kind,
            amount_din=amount_din
        )

        session.add(entry)
        session.commit()

def my_balance(username: str):
    with db.get_session() as session:
        entries = session.exec(
            select(db.PoolEntry).where(db.PoolEntry.username == username)
        ).all()

    net = 0
    for e in entries:
        if e.kind == "paid":
            net += e.amount_din
        elif e.kind == "share":
            net -= e.amount_din
    return net

