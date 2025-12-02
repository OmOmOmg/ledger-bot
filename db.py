from sqlmodel import SQLModel, Field, create_engine, Session
import os
import db

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