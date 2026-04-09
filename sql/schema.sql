---Categories Table---
CREATE TABLE IF NOT EXISTS categories (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

---Transactions Table--
CREATE TABLE IF NOT EXISTS transactions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    amount         REAL    NOT NULL,
    date           TEXT    NOT NULL,
    description    TEXT,
    category_id    INTEGER,
    payment_method TEXT,
    type           TEXT    NOT NULL,
    recurring      INTEGER DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

---Budgets Table---
CREATE TABLE IF NOT EXISTS budgets (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    amount      REAL    NOT NULL,
    time_period TEXT    NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);