import sqlite3

DB_PATH = "inventory.db"


def create_tables():
    """Create the products table if it does not exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if the 'products' table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products';")
    if cursor.fetchone() is None:
        cursor.execute("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_code TEXT,
                name TEXT,
                batch_number TEXT,
                quantity INTEGER,
                price REAL,
                total_price REAL,
                expiry_date TEXT,
                stored_location TEXT,
                supplier TEXT
            )
        """)
    else:
        # Check if the 'stored_location' column exists
        cursor.execute("PRAGMA table_info(products);")
        columns = [column[1] for column in cursor.fetchall()]

        if 'stored_location' not in columns:
            cursor.execute("""
                ALTER TABLE products
                ADD COLUMN stored_location TEXT
            """)

    conn.commit()
    conn.close()


def add_product(item_code, name, batch_number, quantity, price, expiry_date, stored_location, supplier):
    """Add a new product to the database."""
    total_price = float(quantity) * float(price)  # Ensure proper calculation
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (item_code, name, batch_number, quantity, price, total_price, expiry_date, stored_location, supplier) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (item_code, name, batch_number, quantity, price, total_price, expiry_date, stored_location, supplier))
    conn.commit()
    conn.close()


def get_products():
    """Retrieve all products from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return products


def update_product(id, item_code, name, batch_number, quantity, price, expiry_date, stored_location, supplier):
    """Update an existing product."""
    total_price = float(quantity) * float(price)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET item_code=?, name=?, batch_number=?, quantity=?, price=?, total_price=?, expiry_date=?, stored_location=?, supplier=? WHERE id=?",
        (item_code, name, batch_number, quantity, price, total_price, expiry_date, stored_location, supplier, id))
    conn.commit()
    conn.close()


def delete_product(id):
    """Delete a product from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (id,))
    conn.commit()
    conn.close()
