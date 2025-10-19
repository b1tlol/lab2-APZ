from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Optional
from uuid import uuid4

class TxType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    TRANSFER = "TRANSFER"

@dataclass(slots=True)
class Account:
    id: Optional[int] = None
    name: str = ""
    currency: str = "UAH"
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass(slots=True)
class Category:
    id: Optional[int] = None
    name: str = ""
    is_income: bool = False  # True=income category, False=expense

@dataclass(slots=True)
class Transaction:
    id: Optional[int] = None
    tx_type: TxType = TxType.EXPENSE
    account_id: int = 0
    amount: float = 0.0
    description: str = ""
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    # Optional fields
    category_id: Optional[int] = None
    # For transfer
    to_account_id: Optional[int] = None
