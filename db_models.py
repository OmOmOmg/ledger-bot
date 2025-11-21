from sqlmodel import SQLModel, Field
from sqlalchemy import CheckConstraint, UniqueConstraint

# tg_user: canonical participant list (username PK)
class TgUser(SQLModel, table=True):
    __tablename__ = "tg_user"
    username: str = Field(primary_key=True)

# debt_ledger: append-only journal of debt events
class DebtLedger(SQLModel, table=True):
    __tablename__ = "debt_ledger"
    __table_args__ = (
        UniqueConstraint("message_id"),
        CheckConstraint("creditor <> debtor")
    )
    id: int | None = Field(default=None, primary_key=True)
    creditor: str = Field(foreign_key="tg_user.username", nullable=False)
    debtor: str = Field(foreign_key="tg_user.username", nullable=False)
    amount_din: int = Field(nullable=False)
    message_id: int = Field(nullable=False)
