"""
PriceWatch — SQLite Historical Price Repository
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

class PriceDatabase:
    def __init__(self, db_path: str = "pricewatch.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tracked_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                target_threshold REAL,
                created_at TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                price REAL,
                recorded_at TEXT,
                FOREIGN KEY(url) REFERENCES tracked_products(url)
            )
        """)
        conn.commit()
        conn.close()

    def add_product(self, url: str, title: str, threshold: float):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
            INSERT OR REPLACE INTO tracked_products (url, title, target_threshold, created_at)
            VALUES (?, ?, ?, ?)
        """, (url, title, threshold, now))
        conn.commit()
        conn.close()

    def record_price(self, url: str, price: float):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO price_history (url, price, recorded_at) VALUES (?, ?, ?)", (url, price, now))
        conn.commit()
        conn.close()

    def get_tracked_items(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT url, title, target_threshold FROM tracked_products")
        rows = cur.fetchall()
        conn.close()
        return [{"url": r[0], "title": r[1], "target_threshold": r[2]} for r in rows]
