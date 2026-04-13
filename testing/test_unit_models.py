import unittest
import os
from database import initialize_database, get_connection
from models import Transactions, Budget, Categories


class TestModels(unittest.TestCase):

    def setUp(self):
        try:
            self.conn.close()
        except:
            pass

        import gc
        gc.collect()

        if os.path.exists("SmartBudget.db"):
            os.remove("SmartBudget.db")

        initialize_database()
        self.conn = get_connection()

        # get sample category
        self.category = Categories.get_all_categories()[0]

    def tearDown(self):
        self.conn.close()



    #Category Unit Tests

    def test_category_get_all(self):
        categories = Categories.get_all_categories()
        self.assertIsInstance(categories, list)
        self.assertGreater(len(categories), 0)

    def test_category_get_by_id(self):
        category = Categories.get_by_category_id(self.category.id)
        self.assertIsNotNone(category)
        self.assertEqual(category.id, self.category.id)

    def test_category_save_update(self):
        self.category.name = "UpdatedName"
        self.category.save()

        updated = Categories.get_by_category_id(self.category.id)
        self.assertEqual(updated.name, "UpdatedName")


    #Transaction Unit Tests
    def test_transaction_save_and_fetch(self):
        t = Transactions(None, 100, "2026-04-01", "salary", self.category.id, "Cash", "income")
        t.save()

        transactions = Transactions.get_all_transactions()
        self.assertTrue(any(tx.id == t.id for tx in transactions))

    def test_transaction_get_by_type(self):
        t = Transactions(None, 200, "2026-04-02", "food", self.category.id, "Card", "expense")
        t.save()

        expenses = Transactions.get_by_type("expense")
        self.assertTrue(any(tx.id == t.id for tx in expenses))

    def test_transaction_get_by_category(self):
        t = Transactions(None, 300, "2026-04-03", "rent", self.category.id, "Cash", "expense")
        t.save()

        results = Transactions.get_by_category(self.category.id)
        self.assertTrue(any(tx.id == t.id for tx in results))

    def test_transaction_delete(self):
        t = Transactions(None, 150, "2026-04-04", "test", self.category.id, "Cash", "expense")
        t.save()
        t.delete()

        results = Transactions.get_all_transactions()
        self.assertFalse(any(tx.id == t.id for tx in results))


    #Budget Unit Tests

    def test_budget_save_and_fetch(self):
        b = Budget(None, self.category.id, 500, "Monthly")
        b.save()

        budgets = Budget.get_all_budget()
        self.assertTrue(any(bg.id == b.id for bg in budgets))

    def test_budget_spent_calculation(self):
        t = Transactions(None, 100, "2026-04-05", "groceries", self.category.id, "Card", "expense")
        t.save()

        b = Budget(None, self.category.id, 200, "Monthly")
        b.save()

        spent = b.get_spent()
        self.assertEqual(spent, 100)

    def test_budget_remaining_amount(self):
        t = Transactions(None, 50, "2026-04-06", "food", self.category.id, "Card", "expense")
        t.save()

        b = Budget(None, self.category.id, 200, "Monthly")
        b.save()

        self.assertEqual(b.get_remaining_amount(), 150)

    def test_budget_over_limit(self):
        t = Transactions(None, 300, "2026-04-07", "shopping", self.category.id, "Card", "expense")
        t.save()

        b = Budget(None, self.category.id, 200, "Monthly")
        b.save()

        self.assertTrue(b.is_over_the_limit())


if __name__ == "__main__":
    unittest.main()