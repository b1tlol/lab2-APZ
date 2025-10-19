from .models import AccountORM, CategoryORM, TransactionORM, TxType as OrmTxType
from app.domain.entities import Account, Category, Transaction, TxType

def account_to_domain(a: AccountORM) -> Account:
    return Account(id=a.id, name=a.name, currency=a.currency, created_at=a.created_at)

def account_from_domain(a: Account) -> AccountORM:
    orm = AccountORM(id=a.id, name=a.name, currency=a.currency, created_at=a.created_at)
    return orm

def category_to_domain(c: CategoryORM) -> Category:
    return Category(id=c.id, name=c.name, is_income=c.is_income)

def category_from_domain(c: Category) -> CategoryORM:
    return CategoryORM(id=c.id, name=c.name, is_income=c.is_income)

def tx_to_domain(t: TransactionORM) -> Transaction:
    return Transaction(
        id=t.id,
        tx_type=TxType(t.tx_type.value),
        account_id=t.account_id,
        amount=t.amount,
        description=t.description,
        occurred_at=t.occurred_at,
        category_id=t.category_id,
        to_account_id=t.to_account_id,
    )

def tx_from_domain(t: Transaction) -> TransactionORM:
    return TransactionORM(
        id=t.id,
        tx_type=OrmTxType(t.tx_type.value),
        account_id=t.account_id,
        to_account_id=t.to_account_id,
        amount=t.amount,
        description=t.description,
        occurred_at=t.occurred_at,
        category_id=t.category_id,
    )
