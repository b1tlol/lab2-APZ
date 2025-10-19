from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Enum as SAEnum, ForeignKey, Float, Boolean
from datetime import datetime
from enum import Enum
from typing import List, Optional


class Base(DeclarativeBase):
    pass


class TxType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    TRANSFER = "TRANSFER"


class AccountORM(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="UAH", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    outgoing_transactions: Mapped[List["TransactionORM"]] = relationship(
        "TransactionORM",
        foreign_keys="[TransactionORM.account_id]",
        back_populates="account",
        cascade="all, delete-orphan"
    )

    incoming_transactions: Mapped[List["TransactionORM"]] = relationship(
        "TransactionORM",
        foreign_keys="[TransactionORM.to_account_id]",
        back_populates="to_account",
    )


class CategoryORM(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    is_income: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    transactions: Mapped[List["TransactionORM"]] = relationship(
        back_populates="category"
    )


class TransactionORM(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tx_type: Mapped[TxType] = mapped_column(SAEnum(TxType), nullable=False)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    to_account_id: Mapped[Optional[int]] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"), nullable=True)

    account: Mapped["AccountORM"] = relationship(
        "AccountORM",
        foreign_keys=[account_id],
        back_populates="outgoing_transactions"
    )

    to_account: Mapped[Optional["AccountORM"]] = relationship(
        "AccountORM",
        foreign_keys=[to_account_id],
        back_populates="incoming_transactions"
    )

    category: Mapped[Optional["CategoryORM"]] = relationship(
        back_populates="transactions"
    )