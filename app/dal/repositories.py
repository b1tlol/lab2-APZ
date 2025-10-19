from typing import Generic, TypeVar, Iterable, Optional, Callable
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from .models import Base, AccountORM, CategoryORM, TransactionORM, TxType as OrmTxType
from .mappers import account_to_domain, category_to_domain, tx_to_domain, account_from_domain, category_from_domain, tx_from_domain
from app.domain.entities import Account, Category, Transaction, TxType

TDomain = TypeVar("TDomain")
TOrm = TypeVar("TOrm")

class GenericRepository(Generic[TDomain, TOrm]):
    def __init__(self, session: Session, orm_cls, to_domain, from_domain):
        self.session = session
        self.orm_cls = orm_cls
        self.to_domain = to_domain
        self.from_domain = from_domain

    def add(self, entity: TDomain) -> TDomain:
        orm = self.from_domain(entity)
        self.session.add(orm)
        self.session.flush()
        return self.to_domain(orm)

    def get(self, id_: int) -> Optional[TDomain]:
        orm = self.session.get(self.orm_cls, id_)
        return self.to_domain(orm) if orm else None

    def list(self, where: Optional[Callable] = None) -> list[TDomain]:
        stmt = select(self.orm_cls)
        if where:
            stmt = where(stmt)
        rows = self.session.execute(stmt).scalars().all()
        return [self.to_domain(r) for r in rows]

    def update(self, id_: int, **fields) -> Optional[TDomain]:
        orm = self.session.get(self.orm_cls, id_)
        if not orm:
            return None
        for k, v in fields.items():
            setattr(orm, k, v)
        self.session.flush()
        return self.to_domain(orm)

    def delete(self, id_: int) -> bool:
        orm = self.session.get(self.orm_cls, id_)
        if not orm:
            return False
        self.session.delete(orm)
        return True

class AccountsRepository(GenericRepository[Account, AccountORM]):
    def __init__(self, session: Session):
        super().__init__(session, AccountORM, account_to_domain, lambda a: account_from_domain(a))

class CategoriesRepository(GenericRepository[Category, CategoryORM]):
    def __init__(self, session: Session):
        super().__init__(session, CategoryORM, category_to_domain, lambda c: category_from_domain(c))

    def income_categories(self) -> list[Category]:
        return self.list(lambda s: s.where(CategoryORM.is_income.is_(True)))

    def expense_categories(self) -> list[Category]:
        return self.list(lambda s: s.where(CategoryORM.is_income.is_(False)))

class TransactionsRepository(GenericRepository[Transaction, TransactionORM]):
    def __init__(self, session: Session):
        super().__init__(session, TransactionORM, tx_to_domain, lambda t: tx_from_domain(t))

    def by_account(self, account_id: int) -> list[Transaction]:
        return self.list(lambda s: s.where(TransactionORM.account_id == account_id))

    def by_category(self, category_id: int) -> list[Transaction]:
        return self.list(lambda s: s.where(TransactionORM.category_id == category_id))

    def totals_by_account(self) -> list[tuple[int, float]]:
        stmt = select(TransactionORM.account_id, func.sum(TransactionORM.amount)).group_by(TransactionORM.account_id)
        return [(aid, total or 0.0) for aid, total in self.session.execute(stmt).all()]

class UnitOfWork:
    def __init__(self, session_factory):
        self._session_factory = session_factory
        self.session: Session | None = None
        self.accounts: AccountsRepository | None = None
        self.categories: CategoriesRepository | None = None
        self.transactions: TransactionsRepository | None = None

    def __enter__(self):
        self.session = self._session_factory()
        self.accounts = AccountsRepository(self.session)
        self.categories = CategoriesRepository(self.session)
        self.transactions = TransactionsRepository(self.session)
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.session.commit()
        else:
            self.session.rollback()
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
