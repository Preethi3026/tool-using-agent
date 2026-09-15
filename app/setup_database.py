import sqlite3

connection = sqlite3.connect("data/customers.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    city TEXT NOT NULL
)
""")

customers = [
    (1, "Alice", "alice@example.com", "Berlin"),
    (2, "Bob", "bob@example.com", "Munich"),
    (3, "Charlie", "charlie@example.com", "Berlin"),
    (4, "Diana", "diana@example.com", "Hamburg"),
    (5, "Ethan", "ethan@example.com", "Munich"),
]

cursor.executemany(
    "INSERT OR IGNORE INTO customers VALUES (?, ?, ?, ?)",
    customers
)

connection.commit()
connection.close()

print("Database created successfully!")