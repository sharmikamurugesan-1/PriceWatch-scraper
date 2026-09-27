"""
PriceWatch — SQLite Price History & Alert Database
Persists products, historical price observations, price drop alerts, and scraper telemetry.
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "pricewatch.db")

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = DB_PATH):
    conn = get_connection(db_path)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        currency TEXT DEFAULT 'USD',
        target_price REAL NOT NULL,
        current_price REAL NOT NULL,
        lowest_price REAL NOT NULL,
        highest_price REAL NOT NULL,
        in_stock INTEGER DEFAULT 1,
        last_checked TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        price REAL NOT NULL,
        recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        price REAL NOT NULL,
        target_price REAL NOT NULL,
        message TEXT NOT NULL,
        dispatched_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()

def record_price_observation(url: str, title: str, price: float, currency: str = "USD",
                             target_price: float = 0.0, in_stock: bool = True, db_path: str = DB_PATH) -> Dict[str, Any]:
    """Records a new scraped price point and updates historical min/max bounds."""
    init_db(db_path)
    conn = get_connection(db_path)
    cur = conn.cursor()

    cur.execute("SELECT * FROM products WHERE url = ?", (url,))
    row = cur.fetchone()

    alert_triggered = False
    alert_msg = ""

    if row:
        prod_id = row["id"]
        lowest = min(row["lowest_price"], price) if price > 0 else row["lowest_price"]
        highest = max(row["highest_price"], price)
        curr_target = row["target_price"] if target_price <= 0 else target_price

        cur.execute("""
        UPDATE products 
        SET current_price = ?, lowest_price = ?, highest_price = ?, in_stock = ?, last_checked = CURRENT_TIMESTAMP
        WHERE id = ?
        """, (price, lowest, highest, 1 if in_stock else 0, prod_id))

        if price > 0 and price <= curr_target:
            alert_triggered = True
            alert_msg = f"PRICE DROP ALERT: '{title}' dropped to ${price:.2f} (Target: ${curr_target:.2f})!"
            cur.execute("INSERT INTO alerts (product_id, price, target_price, message) VALUES (?, ?, ?, ?)",
                        (prod_id, price, curr_target, alert_msg))
    else:
        lowest = price
        highest = price
        t_price = target_price if target_price > 0 else round(price * 0.9, 2)

        cur.execute("""
        INSERT INTO products (url, title, currency, target_price, current_price, lowest_price, highest_price, in_stock)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (url, title, currency, t_price, price, lowest, highest, 1 if in_stock else 0))
        prod_id = cur.lastrowid

        if price > 0 and price <= t_price:
            alert_triggered = True
            alert_msg = f"PRICE DROP ALERT: '{title}' at initial target of ${price:.2f}!"
            cur.execute("INSERT INTO alerts (product_id, price, target_price, message) VALUES (?, ?, ?, ?)",
                        (prod_id, price, t_price, alert_msg))

    # Record history
    if price > 0:
        cur.execute("INSERT INTO price_history (product_id, price) VALUES (?, ?)", (prod_id, price))

    conn.commit()
    conn.close()

    return {
        "product_id": prod_id,
        "title": title,
        "price": price,
        "alert_triggered": alert_triggered,
        "alert_message": alert_msg
    }

def get_tracked_products(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    init_db(db_path)
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM products ORDER BY id DESC")
    products = [dict(r) for r in cur.fetchall()]
    conn.close()
    return products

def get_product_history(product_id: int, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    init_db(db_path)
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT price, recorded_at FROM price_history WHERE product_id = ? ORDER BY id ASC", (product_id,))
    history = [dict(r) for r in cur.fetchall()]
    conn.close()
    return history
