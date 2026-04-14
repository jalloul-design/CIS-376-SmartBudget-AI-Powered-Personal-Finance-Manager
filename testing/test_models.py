from ML_model import TransactionCategorizer, SpendingPredictor
import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


class TestTransactionCategorizer(unittest.TestCase):

    def setUp(self):
        self.model = TransactionCategorizer()
        self.model.train()

    def test_food_category(self):
        self.assertEqual(self.model.predict("mcdonalds burger"), "Food")

    def test_bills_category(self):
        self.assertEqual(self.model.predict("electric bill utility"), "Bills")

    def test_entertainment_category(self):
        self.assertEqual(self.model.predict(
            "netflix subscription"), "Entertainment")

    def test_transport_category(self):
        self.assertEqual(self.model.predict("uber ride"), "Transport")

    def test_health_category(self):
        self.assertEqual(self.model.predict(
            "gym membership fitness"), "Health")

    def test_shopping_category(self):
        self.assertEqual(self.model.predict("amazon purchase"), "Shopping")

    def test_education_category(self):
        self.assertEqual(self.model.predict(
            "tuition payment university"), "Education")

    def test_unknown_description_returns_string(self):
        result = self.model.predict("random unknown transaction")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_empty_description(self):
        result = self.model.predict("")
        self.assertIsInstance(result, str)

    def test_save_and_load(self):
        self.model.save("test_model.pkl")
        loaded = TransactionCategorizer.load("test_model.pkl")
        self.assertEqual(loaded.predict("starbucks coffee"), "Food")
        os.remove("test_model.pkl")


class TestSpendingPredictor(unittest.TestCase):

    def setUp(self):
        self.predictor = SpendingPredictor()
        self.history = {
            "Food": [200, 220, 210, 230],
            "Bills": [150, 150, 155, 150],
            "Entertainment": [50, 60, 55, 70],
        }
        self.predictor.fit(self.history)

    def test_predict_returns_all_categories(self):
        predictions = self.predictor.predict_next_month()
        for category in self.history:
            self.assertIn(category, predictions)

    def test_predictions_are_non_negative(self):
        predictions = self.predictor.predict_next_month()
        for category, amount in predictions.items():
            self.assertGreaterEqual(amount, 0)

    def test_stable_category_predicts_consistently(self):
        predictions = self.predictor.predict_next_month()
        # Bills are very stable around 150, prediction should be in a reasonable range
        self.assertGreater(predictions["Bills"], 100)
        self.assertLess(predictions["Bills"], 250)

    def test_single_month_history(self):
        self.predictor.fit({"Food": [300]})
        predictions = self.predictor.predict_next_month()
        self.assertIn("Food", predictions)

    def test_prediction_values_are_floats(self):
        predictions = self.predictor.predict_next_month()
        for val in predictions.values():
            self.assertIsInstance(val, float)


if __name__ == "__main__":
    unittest.main()
