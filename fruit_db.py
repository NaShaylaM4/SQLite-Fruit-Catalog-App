import sqlite3
from typing import List, Dict, Any, Optional

DB_NAME = "fruit_catalog.db"

def get_conn(db_path: str = DB_NAME) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def create_table(db_path: str = DB_NAME) -> None:
    sql = """
    CREATE TABLE IF NOT EXISTS fruits (
        fruit_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        color TEXT NOT NULL DEFAULT 'Unknown',
        category TEXT NOT NULL DEFAULT 'Other',
        price_per_lb REAL NOT NULL DEFAULT 0.00 CHECK(price_per_lb >= 0),
        origin_country TEXT NOT NULL DEFAULT 'Unknown',
        in_stock INTEGER NOT NULL DEFAULT 1 CHECK(in_stock IN (0,1))
    );
    """
    with get_conn(db_path) as conn:
        conn.execute(sql)

def add_fruit(name: str, color: str, category: str, price: float,
              origin: str, in_stock: int = 1, db_path: str = DB_NAME) -> int:
    sql = """
    INSERT INTO fruits(name, color, category, price_per_lb, origin_country, in_stock)
    VALUES(?,?,?,?,?,?)
    """
    with get_conn(db_path) as conn:
        cur = conn.execute(sql, (name, color, category, price, origin, in_stock))
        return cur.lastrowid

def get_all_fruits(db_path: str = DB_NAME) -> List[Dict[str, Any]]:
    with get_conn(db_path) as conn:
        rows = conn.execute("SELECT * FROM fruits ORDER BY name").fetchall()
        return [dict(r) for r in rows]

def search_fruits(name="", category="", origin="", db_path: str = DB_NAME) -> List[Dict[str, Any]]:
    sql = """
    SELECT * FROM fruits
    WHERE name LIKE ? AND category LIKE ? AND origin_country LIKE ?
    ORDER BY name
    """
    with get_conn(db_path) as conn:
        rows = conn.execute(sql, (f"%{name}%", f"%{category}%", f"%{origin}%")).fetchall()
        return [dict(r) for r in rows]

def update_fruit(fruit_id: int, name: str, color: str, category: str, price: float,
                 origin: str, in_stock: int, db_path: str = DB_NAME) -> int:
    sql = """
    UPDATE fruits
    SET name=?, color=?, category=?, price_per_lb=?, origin_country=?, in_stock=?
    WHERE fruit_id=?
    """
    with get_conn(db_path) as conn:
        cur = conn.execute(sql, (name, color, category, price, origin, in_stock, fruit_id))
        return cur.rowcount

def delete_fruit(fruit_id: int, db_path: str = DB_NAME) -> int:
    with get_conn(db_path) as conn:
        cur = conn.execute("DELETE FROM fruits WHERE fruit_id=?", (fruit_id,))
        return cur.rowcount

def report_stats(db_path: str = DB_NAME):
    with get_conn(db_path) as conn:
        total = conn.execute("SELECT COUNT(*) FROM fruits").fetchone()[0]
        instock = conn.execute("SELECT COUNT(*) FROM fruits WHERE in_stock=1").fetchone()[0]
        avg_price = conn.execute("SELECT AVG(price_per_lb) FROM fruits").fetchone()[0]
        return total, instock, round(avg_price or 0, 2)
