from dataclasses import dataclass
from typing import Optional
from app.domain.entities import Account, Category, Transaction, TxType

@dataclass
class FinanceService:
    uow: any  # UnitOfWork factory or instance supporting context manager

    # Accounts
    def create_account(self, name: str, currency: str = "UAH") -> Account:
        with self.uow as u:
            a = Account(name=name, currency=currency)
            return u.accounts.add(a)

    def list_accounts(self) -> list[Account]:
        with self.uow as u:
            return u.accounts.list()

    # Categories
    def create_category(self, name: str, is_income: bool) -> Category:
        with self.uow as u:
            c = Category(name=name, is_income=is_income)
            return u.categories.add(c)

    def list_categories(self, is_income: Optional[bool] = None) -> list[Category]:
        with self.uow as u:
            if is_income is None:
                return u.categories.list()
            return u.categories.income_categories() if is_income else u.categories.expense_categories()

    # Transactions
    def add_income(self, account_id: int, amount: float, category_id: int, description: str = "") -> Transaction:
        if amount <= 0:
            raise ValueError("Amount must be > 0")
        with self.uow as u:
            if not u.accounts.get(account_id):
                raise ValueError("Account not found")
            cat = u.categories.get(category_id)
            if not cat or not cat.is_income:
                raise ValueError("Category must be income type")
            tx = Transaction(tx_type=TxType.INCOME, account_id=account_id, amount=amount,
                             category_id=category_id, description=description)
            return u.transactions.add(tx)

    def add_expense(self, account_id: int, amount: float, category_id: int, description: str = "") -> Transaction:
        if amount <= 0:
            raise ValueError("Amount must be > 0")
        with self.uow as u:
            if not u.accounts.get(account_id):
                raise ValueError("Account not found")
            cat = u.categories.get(category_id)
            if not cat or cat.is_income:
                raise ValueError("Category must be expense type")
            tx = Transaction(tx_type=TxType.EXPENSE, account_id=account_id, amount=amount * -1.0,
                             category_id=category_id, description=description)
            return u.transactions.add(tx)

    def transfer(self, from_account_id: int, to_account_id: int, amount: float, description: str = "") -> tuple[Transaction, Transaction]:
        if amount <= 0:
            raise ValueError("Amount must be > 0")
        if from_account_id == to_account_id:
            raise ValueError("Use different accounts for transfer")
        with self.uow as u:
            if not u.accounts.get(from_account_id) or not u.accounts.get(to_account_id):
                raise ValueError("Account not found")
            out_tx = Transaction(tx_type=TxType.TRANSFER, account_id=from_account_id, to_account_id=to_account_id,
                                 amount=-amount, description=description)
            in_tx = Transaction(tx_type=TxType.TRANSFER, account_id=to_account_id, to_account_id=from_account_id,
                                amount=amount, description=description)
            out_tx = u.transactions.add(out_tx)
            in_tx = u.transactions.add(in_tx)
            return out_tx, in_tx

    # Queries / Reports
    def account_balance(self, account_id: int) -> float:
        with self.uow as u:
            txs = u.transactions.by_account(account_id)
            return round(sum(t.amount for t in txs), 2)

    def balances_by_account(self) -> list[tuple[int, float]]:
        with self.uow as u:
            res = []
            for a in u.accounts.list():
                bal = self.account_balance(a.id)
                res.append((a, bal))
            return res

    def expense_by_category(self) -> list[tuple[Category, float]]:
        with self.uow as u:
            cats = u.categories.expense_categories()
            result = []
            for c in cats:
                total = sum(t.amount for t in u.transactions.by_category(c.id) if t.tx_type == TxType.EXPENSE)
                result.append((c, round(total, 2)))
            # totals are negative for expenses; present absolute values
            return [(c, abs(t)) for c, t in result]

    def transactions_for_account(self, account_id: int) -> list[Transaction]:
        with self.uow as u:
            return u.transactions.by_account(account_id)
