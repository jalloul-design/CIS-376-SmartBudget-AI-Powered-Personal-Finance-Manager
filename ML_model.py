import pickle
import os
from collections import defaultdict

# Training data: (description, category) pairs
TRAINING_DATA = [
    ("grocery store walmart", "Food"),
    ("whole foods market", "Food"),
    ("restaurant dinner", "Food"),
    ("mcdonalds burger", "Food"),
    ("pizza hut order", "Food"),
    ("starbucks coffee", "Food"),
    ("uber eats delivery", "Food"),
    ("doordash food", "Food"),
    ("electric bill utility", "Bills"),
    ("water bill payment", "Bills"),
    ("internet service provider", "Bills"),
    ("phone bill att", "Bills"),
    ("rent payment apartment", "Bills"),
    ("gas utility bill", "Bills"),
    ("netflix subscription", "Entertainment"),
    ("spotify premium", "Entertainment"),
    ("movie theater ticket", "Entertainment"),
    ("amazon prime video", "Entertainment"),
    ("hulu subscription", "Entertainment"),
    ("concert ticket", "Entertainment"),
    ("uber ride", "Transport"),
    ("lyft trip", "Transport"),
    ("gas station fuel", "Transport"),
    ("parking fee", "Transport"),
    ("bus pass transit", "Transport"),
    ("car insurance payment", "Transport"),
    ("cvs pharmacy medicine", "Health"),
    ("doctor visit copay", "Health"),
    ("gym membership fitness", "Health"),
    ("hospital bill", "Health"),
    ("dentist appointment", "Health"),
    ("amazon purchase", "Shopping"),
    ("target store purchase", "Shopping"),
    ("clothing store fashion", "Shopping"),
    ("online shopping order", "Shopping"),
    ("best buy electronics", "Shopping"),
    ("tuition payment university", "Education"),
    ("textbook purchase", "Education"),
    ("online course udemy", "Education"),
    ("school supplies", "Education"),
]


class TransactionCategorizer:
    def __init__(self):
        self.word_category_counts = defaultdict(lambda: defaultdict(int))
        self.category_counts = defaultdict(int)
        self.categories = set()
        self.trained = False

    def _tokenize(self, text):
        return text.lower().split()

    def train(self, data=None):
        if data is None:
            data = TRAINING_DATA
        for description, category in data:
            tokens = self._tokenize(description)
            self.category_counts[category] += 1
            self.categories.add(category)
            for word in tokens:
                self.word_category_counts[word][category] += 1
        self.trained = True

    def predict(self, description):
        if not self.trained:
            self.train()
        tokens = self._tokenize(description)
        total_docs = sum(self.category_counts.values())
        scores = {}
        for category in self.categories:
            # Log probability: P(category) * product of P(word|category)
            score = self.category_counts[category] / total_docs
            for word in tokens:
                word_count = self.word_category_counts[word][category]
                # Laplace smoothing
                score *= (word_count + 1) / \
                    (self.category_counts[category] +
                     len(self.word_category_counts) + 1)
            scores[category] = score
        return max(scores, key=scores.get)

    def save(self, path="ml_model.pkl"):
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path="ml_model.pkl"):
        if os.path.exists(path):
            with open(path, "rb") as f:
                return pickle.load(f)
        model = TransactionCategorizer()
        model.train()
        return model


class SpendingPredictor:
    def __init__(self):
        self.slopes = {}
        self.intercepts = {}
        self.categories = []

    def fit(self, history):
        """
        history: dict of {category: [monthly_amounts]}
        e.g. {"Food": [300, 320, 290], "Bills": [150, 150, 160]}
        """
        self.categories = list(history.keys())
        for category, amounts in history.items():
            n = len(amounts)
            if n < 2:
                self.slopes[category] = 0
                self.intercepts[category] = amounts[0] if amounts else 0
                continue
            x = list(range(n))
            x_mean = sum(x) / n
            y_mean = sum(amounts) / n
            numerator = sum((x[i] - x_mean) * (amounts[i] - y_mean)
                            for i in range(n))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
            slope = numerator / denominator if denominator != 0 else 0
            intercept = y_mean - slope * x_mean
            self.slopes[category] = slope
            self.intercepts[category] = intercept

    def predict_next_month(self):
        """Returns predicted spending per category for next month."""
        predictions = {}
        for category in self.categories:
            n = len(self.slopes)
            predicted = self.slopes[category] * \
                (n + 1) + self.intercepts[category]
            predictions[category] = max(0, round(predicted, 2))
        return predictions
