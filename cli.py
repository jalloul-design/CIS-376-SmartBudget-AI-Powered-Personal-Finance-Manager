# Hussein
# CLI interface for quick data entry and basic operations

from database import initialize_database
from models import Transactions, Budget, Categories

def run_cli():
    initialize_database()
    while True:
        print("\n--- SmartBudget CLI ---")
        print("1. Add Transaction")
        print("2. View All Transactions")
        print("3. View Budget Status")
        print("4. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            amount = float(input("Amount: "))
            date = input("Date (YYYY-MM-DD): ")
            desc = input("Description: ")
            t_type = input("Type (expense/income): ")
            pay = input("Payment Method (Cash/Credit Card/Debit Card): ")

            cats = Categories.get_all_categories()
            print("Categories:")
            for c in cats:
                print(f"  {c.id}. {c.name}")
            cat_id = int(input("Category ID: "))

            t = Transactions(None, amount, date, desc, cat_id, pay, t_type)
            t.save()
            print("Transaction added!")

        elif choice == "2":
            transactions = Transactions.get_all_transactions()
            if not transactions:
                print("No transactions found.")
            for t in transactions:
                cat = Categories.get_by_category_id(t.category_id)
                print(f"[{t.date}] {t.type.upper()} ${t.amount:.2f} - {cat.name if cat else '?'} - {t.description}")

        elif choice == "3":
            budgets = Budget.get_all_budget()
            if not budgets:
                print("No budgets set.")
            for b in budgets:
                cat = Categories.get_by_category_id(b.category_id)
                print(f"{cat.name if cat else '?'}: ${b.get_spent():.2f} / ${b.amount:.2f} ({b.get_the_percentage_used()*100:.0f}%)")

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print("Invalid option, try again.")

if __name__ == "__main__":
    run_cli()