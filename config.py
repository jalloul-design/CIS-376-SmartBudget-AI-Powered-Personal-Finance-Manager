# Mira
# Stores all constants and settings. Things like the database filename, budget alert thresholds (e.g. 80% = warning, 100% = over limit), and any app-wide variables everyone else imports from.

import os

database_name = "SmartBudget.db"

warning_threshold = 0.80
danger_threshold = 1.00

# Transactional Types
income = "Income"
expense = "Expense"

#Bugets Time Periods
weekly = "Weekly"
monthly = "Monthly"
yearly = "Yearly"

# Categories
DEFAULT_CATEGORIES =\
[
    'Food', 'Transportation', 'Entertainment', 'Rent', 'Utilities',
    'Car Payment', 'Phone Bill', 'Health Care', 'Shopping', 'Miscellaneous', 'Others'
]
