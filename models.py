from database import get_connection

# Class For The Categories
# Handles all the categories data into the database
class Categories:
    def __init__(self, id, name):
        # Stores the category name and id
        self.id   = id
        self.name = name

    def save(self):
        # saving a new category or to update an existing one
        connection = get_connection()
        # if no there is no id, a new category will be inserted
        if self.id is None:
            cursor = connection.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (self.name,))
            self.id = cursor.lastrowid
        else:
            # if id exists, it would update the existing category
            connection.execute('UPDATE categories SET name=? WHERE id=?', (self.name, self.id))
        connection.commit()
        connection.close()

    def delete(self):
        # Deletes the category from the database
        connection = get_connection()
        connection.execute('DELETE FROM categories WHERE id = ?', (self.id,))
        connection.commit()
        connection.close()

    @staticmethod
    def get_all_categories():
        # Returns a list of all the categories within the database
        connection = get_connection()
        rows = connection.execute('SELECT * FROM categories').fetchall()
        connection.close()
        return [Categories(row['id'], row['name']) for row in rows]

    @staticmethod
    def get_by_category_id(category_id):
        # returns a single category that matches the given id number
        connection = get_connection()
        rows = connection.execute('SELECT * FROM categories WHERE id = ?', (category_id,)).fetchone()
        connection.close()
        return Categories(rows['id'], rows['name']) if rows else None

    @staticmethod
    def get_by_name(name):
        # returns a single category that matches the given name
        connection = get_connection()
        rows = connection.execute('SELECT * FROM categories WHERE name = ?', (name,)).fetchone()
        connection.close()
        return Categories(rows['id'], rows['name']) if rows else None


# Class for Transactions
class Transactions:
    def __init__(self, id, amount, date, description,category_id, payment_method, type, recurring=0):
        # storing all the details for transaction
        self.id             = id
        self.amount         = float(amount)
        self.date           = date
        self.description    = description
        self.category_id    = category_id
        self.payment_method = payment_method
        self.type           = type
        self.recurring      = recurring

    def save(self):
        # saves a new or existing transaction
        connection = get_connection()
        if self.id is None:
            # If the transaction is new, we will insert it.
            cursor = connection.execute('''INSERT INTO transactions (amount, date, description, category_id, payment_method, type, recurring) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (self.amount, self.date, self.description, self.category_id, self.payment_method, self.type, self.recurring))
            self.id = cursor.lastrowid # saves the new id
        else:
            # If the transaction already exists, we would update the information.
            connection.execute('''UPDATE transactions SET amount=?, date=?, description=?, category_id=?, payment_method=?, type=?, recurring=? WHERE id=?''',
                (self.amount, self.date, self.description, self.category_id, self.payment_method,self.type, self.recurring, self.id))
        connection.commit()
        connection.close()

    def delete(self):
        # deletes the transaction from the databases
        connection = get_connection()
        connection.execute('DELETE FROM transactions WHERE id = ?', (self.id,))
        connection.commit()
        connection.close()

    @staticmethod
    def get_all_transactions():
        # Returns all the transaction by the newest date first.
        connection = get_connection()
        rows = connection.execute('SELECT * FROM transactions ORDER BY date DESC').fetchall()
        connection.close()
        return [Transactions( row['id'], row['amount'], row['date'], row['description'], row['category_id'], row['payment_method'], row['type'], row['recurring']) for row in rows]

    @staticmethod
    # Returns all the transaction information that matches the given type (Example: Rent)
    def get_by_type(transaction_type):
        connection = get_connection()
        rows = connection.execute('SELECT * FROM transactions WHERE type = ? ORDER BY date DESC',(transaction_type,)).fetchall()
        connection.close()
        return [Transactions(row['id'], row['amount'], row['date'], row['description'], row['category_id'], row['payment_method'], row['type'], row['recurring']) for row in rows]

    @staticmethod
    # Returns all the transaction information that belong to a specific category (Example: Rent)
    def get_by_category(category_id):
        connection = get_connection()
        rows = connection.execute('SELECT * FROM transactions WHERE category_id = ? ORDER BY date DESC',(category_id,)).fetchall()
        connection.close()
        return [Transactions(row['id'], row['amount'], row['date'], row['description'], row['category_id'], row['payment_method'], row['type'], row['recurring']) for row in rows]

    @staticmethod
    def get_by_month(year, month):
        #Returns all transaction for a specific month. Example(04/2026) it will return all the transaction from the month of April 2026.
        connection = get_connection()
        month_str = f"{year}-{month:02d}"
        rows = connection.execute('SELECT *  FROM transactions WHERE date LIKE ? ORDER BY date DESC', (f"{month_str}%",)).fetchall()
        connection.close()
        return [Transactions( row['id'], row['amount'], row['date'], row['description'], row['category_id'], row['payment_method'], row['type'], row['recurring']) for row in rows]

    @staticmethod
    # returns all the transaction information that are reoccurring.
    def get_recurring():
        connection = get_connection()
        rows = connection.execute('SELECT * FROM transactions WHERE recurring = 1').fetchall()
        connection.close()
        return [Transactions(row['id'], row['amount'], row['date'], row['description'],row['category_id'], row['payment_method'], row['type'], row['recurring']) for row in rows]


# Class For Budget
class Budget:
    def __init__(self, id, category_id, amount, time_period):
        # Stores all the budget details
        self.id          = id
        self.category_id = category_id
        self.amount      = amount
        self.time_period = time_period

    def save(self):
        # saves all budget information or it updates it.
        connection = get_connection()
        # If the id does not exist, a new udget is inserted.
        if self.id is None:
            cursor = connection.execute('''INSERT INTO budgets (category_id, amount, time_period)VALUES (?, ?, ?)''', (self.category_id, self.amount, self.time_period))
            self.id = cursor.lastrowid # saves the id that did not originally exist
        else:
            # if the id does exist, it will update the existing budget
            connection.execute('''UPDATE budgets SET category_id=?, amount=?, time_period=? WHERE id=?''', (self.category_id, self.amount, self.time_period, self.id))
        connection.commit()
        connection.close()

    def delete(self):
        # Deletes the budget from the database
        connection = get_connection()
        connection.execute('DELETE FROM budgets WHERE id = ?', (self.id,))
        connection.commit()
        connection.close()

    def get_spent(self):
        connection = get_connection()

        row = connection.execute(
            '''
            SELECT COALESCE(SUM(amount), 0)
            FROM transactions
            WHERE category_id = ? AND type = "expense"
            ''',
            (self.category_id,)
        ).fetchone()

        return abs(row[0])

    def get_the_percentage_used(self):
        # gets the percentage of how much the budget as been used.
        if self.amount == 0:
            return 0.0
        return self.get_spent() / self.amount

    def get_remaining_amount(self):
        # returns the remaining budget amount, if person goes over the budget limit, a negative number will appear
        return self.amount - self.get_spent()

    def is_over_the_limit(self):
        # Returns True if the user has gone over the budget limit
        return self.get_spent() > self.amount

    @staticmethod
    def get_all_budget():
        # Returns a list of all the budgets within the database
        connection = get_connection()
        rows = connection.execute('SELECT * FROM budgets').fetchall()
        connection.close()
        return [Budget(row['id'], row['category_id'],row['amount'], row['time_period']) for row in rows]

    @staticmethod
    def get_by_category(category_id):
        # Returns the budgets for a specific category, but if there is no budget for a specific category "None" will display
        connection = get_connection()
        row = connection.execute('SELECT * FROM budgets WHERE category_id = ?', (category_id,)).fetchone()
        connection.close()
        return Budget(row['id'], row['category_id'],row['amount'], row['time_period']) if row else None
