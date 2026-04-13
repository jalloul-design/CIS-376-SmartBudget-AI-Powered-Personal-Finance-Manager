# Aakifah
# End-to-end workflow tests. Simulates a full user flow: add a transaction → check analytics update → check budget alert triggers → generate a report. Also tests edge cases like empty database, invalid inputs, and budget overflow.

import unittest
import os
import sqlite3
from database import initialize_database, get_connection
from models import Transactions, Budget, Categories
from analytics import AnalyticsEngine, ReportGenerator

class TestEndToEndWorkflow(unittest.TestCase):
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

        self.analytics = AnalyticsEngine(self.conn)
        self.report_gen = ReportGenerator(self.analytics)

        self.category = Categories.get_all_categories()[0]

    def tearDown(self):
        self.conn.close()



    def test_full_workflow(self):

        #Add income
        t1 = Transactions(None, 1000, "2026-04-01", "salary", self.category.id, "Bank", "income")
        t1.save()
        # Add expense
        t2 = Transactions(None, -200, "2026-04-02", "groceries", self.category.id, "Card", "expense")
        t2.save()

        #Analytics
        income = self.analytics.total_income(4, 2026)
        expenses = self.analytics.total_expenses(4, 2026)
        savings_rate = self.analytics.savings_rate(4, 2026)
        self.assertEqual(income, 1000)
        self.assertEqual(expenses, 200)
        self.assertAlmostEqual(savings_rate, 80.0)

        #Budget
        budget = Budget(None, self.category.id, 150, "Monthly")
        budget.save()

        spent = budget.get_spent()
        self.assertEqual(abs(spent), 200)
        # stored negative
        self.assertTrue(budget.is_over_the_limit())

        #Report
        report = self.report_gen.generate_monthly_report(4, 2026)
        self.assertEqual(report["total_income"], 1000)
        self.assertEqual(report["total_expenses"], 200)
        self.assertIn("recommendations",report)



    #Edge Case: Checking empty database

    def test_empty_database(self):
        income = self.analytics.total_income(4, 2026)
        expenses = self.analytics.total_expenses(4, 2026)
        savings_rate = self.analytics.savings_rate(4, 2026)
        self.assertEqual(income, 0)
        self.assertEqual(expenses, 0)
        self.assertEqual(savings_rate, 0.0)


    #Edge Case: invalid input
    def test_invalid_transaction(self):

        with self.assertRaises(ValueError):
            Transactions(None, "invalid_amount", "bad-date",
                         "test", self.category.id, "Cash", "expense")


    #Edge Case: Budget overflow test
    def test_budget_overflow(self):

        # Budget = 100
        budget = Budget(None, self.category.id, 100, "Monthly")
        budget.save()

        # Spend 150
        t = Transactions(None, -150, "2026-04-03", "shopping", self.category.id, "Card", "expense")
        t.save()
        self.assertTrue(budget.is_over_the_limit())
        self.assertLess(budget.get_remaining_amount(), 0)


    #Analytics
    def test_no_expenses(self):

        t = Transactions(None, 500, "2026-04-01", "salary", self.category.id, "Bank", "income")
        t.save()
        avg = self.analytics.average_daily_spending(4, 2026)
        self.assertEqual(avg, 0.0)

#Report generation
    def test_report_no_data(self):

        report = self.report_gen.generate_monthly_report(4, 2026)
        self.assertEqual(report["total_income"], 0)
        self.assertEqual(report["total_expenses"], 0)
        self.assertIn("recommendations", report)

if __name__ == "__main__":
    unittest.main()