from tabulate import tabulate
from app.dal.db import build_session_factory
from app.dal.repositories import UnitOfWork
from app.bll.services import FinanceService
from app.domain.entities import TxType

def seed_once(svc: FinanceService):
    # seed accounts
    if not svc.list_accounts():
        a1 = svc.create_account("Монобанк", "UAH")
        a2 = svc.create_account("Revolut", "USD")
        # seed categories
        inc1 = svc.create_category("Зарплата", True)
        inc2 = svc.create_category("Подарунок", True)
        exp1 = svc.create_category("Продукти", False)
        exp2 = svc.create_category("Транспорт", False)
        # sample tx
        svc.add_income(a1.id, 45000, inc1.id, "жовтень")
        svc.add_expense(a1.id, 1200, exp1.id, "АТБ")
        svc.add_expense(a1.id, 280, exp2.id, "Метро")
        svc.transfer(a1.id, a2.id, 100, "купівля USD")

def main():
    session_factory = build_session_factory("sqlite:///fin.db")
    uow = UnitOfWork(session_factory)
    svc = FinanceService(uow)
    seed_once(svc)

    menu = {
        "1": "Показати рахунки та баланси",
        "2": "Додати дохід",
        "3": "Додати витрату",
        "4": "Переказ між рахунками",
        "5": "Витрати за категоріями",
        "6": "Транзакції по рахунку",
        "0": "Вихід",
    }

    def show_accounts():
        rows = []
        for a, bal in svc.balances_by_account():
            rows.append([a.id, a.name, a.currency, bal])
        print(tabulate(rows, headers=["ID", "Назва", "Валюта", "Баланс"], tablefmt="github"))

    while True:
        print("\n=== Фінансовий менеджер ===")
        for k in sorted(menu):
            print(f"{k}. {menu[k]}")
        choice = input("Оберіть дію: ").strip()
        try:
            if choice == "1":
                show_accounts()
            elif choice == "2":
                acc = int(input("ID рахунку: "))
                amt = float(input("Сума: "))
                cat = int(input("ID категорії доходу: "))
                desc = input("Опис: ")
                tx = svc.add_income(acc, amt, cat, desc)
                print("OK, дохід додано:", tx)
            elif choice == "3":
                acc = int(input("ID рахунку: "))
                amt = float(input("Сума: "))
                cat = int(input("ID категорії витрат: "))
                desc = input("Опис: ")
                tx = svc.add_expense(acc, amt, cat, desc)
                print("OK, витрату додано:", tx)
            elif choice == "4":
                a1 = int(input("ID рахунку-відправника: "))
                a2 = int(input("ID рахунку-отримувача: "))
                amt = float(input("Сума: "))
                desc = input("Опис: ")
                svc.transfer(a1, a2, amt, desc)
                print("OK, переказ виконано")
            elif choice == "5":
                rows = [(c.id, c.name, total) for c, total in svc.expense_by_category()]
                print(tabulate(rows, headers=["ID", "Категорія", "Витрати"], tablefmt="github"))
            elif choice == "6":
                acc = int(input("ID рахунку: "))
                txs = svc.transactions_for_account(acc)
                rows = [(t.id, t.tx_type.value, t.amount, t.description, t.occurred_at) for t in txs]
                print(tabulate(rows, headers=["ID", "Тип", "Сума", "Опис", "Дата"], tablefmt="github"))
            elif choice == "0":
                print("Бувай!")
                break
            else:
                print("Невірний вибір")
        except Exception as e:
            print("[ПОМИЛКА]", e)

if __name__ == "__main__":
    main()
