import sqlite3

conn = sqlite3.connect('catering.db')
cursor = conn.cursor()

tables = [
    'cost_categories', 'events', 'orders', 'order_items',
    'nomenclatures', 'suppliers', 'supplier_prices', 'budget_controls'
]

for table in tables:
    print(f"\n=== {table} ===")
    cursor.execute(f"PRAGMA table_info({table});")
    columns = cursor.fetchall()
    for col in columns:
        print(f"{col[1]} ({col[2]}) {'PRIMARY KEY' if col[5] else ''}")