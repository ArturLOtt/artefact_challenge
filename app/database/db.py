import os
import csv
import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            base_path = Path(__file__).resolve().parent.parent.parent
            self.data_dir = base_path / "data"
        else:
            self.data_dir = Path(data_dir)

        self._conn: Optional[sqlite3.Connection] = None
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        if self._conn is None:
            self.init_database()
        return self._conn

    def init_database(self) -> None:
        """Initializes an in-memory SQLite database populated directly from CSV files."""
        self._conn = sqlite3.connect(":memory:", check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        cursor = self._conn.cursor()

        table_schemas = {
            "categories": """
                CREATE TABLE categories (
                    category_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT
                );
            """,
            "customers": """
                CREATE TABLE customers (
                    customer_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    phone TEXT,
                    email TEXT,
                    city TEXT
                );
            """,
            "products": """
                CREATE TABLE products (
                    product_id INTEGER PRIMARY KEY,
                    price_brl REAL NOT NULL,
                    name TEXT NOT NULL,
                    category_id INTEGER,
                    description TEXT,
                    stock_quantity INTEGER DEFAULT 0,
                    status TEXT,
                    specs TEXT,
                    created_at TEXT,
                    FOREIGN KEY(category_id) REFERENCES categories(category_id)
                );
            """,
            "promotions": """
                CREATE TABLE promotions (
                    promotion_id INTEGER PRIMARY KEY,
                    product_id INTEGER NOT NULL,
                    discount_percent REAL,
                    description TEXT,
                    is_active INTEGER DEFAULT 0,
                    FOREIGN KEY(product_id) REFERENCES products(product_id)
                );
            """,
            "orders": """
                CREATE TABLE orders (
                    order_id INTEGER PRIMARY KEY,
                    customer_id INTEGER NOT NULL,
                    order_date TEXT,
                    status TEXT,
                    total_brl REAL,
                    payment_method TEXT,
                    tracking_code TEXT,
                    estimated_delivery TEXT,
                    notes TEXT,
                    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
                );
            """,
            "order_items": """
                CREATE TABLE order_items (
                    order_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    FOREIGN KEY(order_id) REFERENCES orders(order_id),
                    FOREIGN KEY(product_id) REFERENCES products(product_id)
                );
            """
        }

        for table_name, create_sql in table_schemas.items():
            cursor.execute(create_sql)

        file_mapping = {
            "categories": ["desafio_tecnico_ai_eng - categories.csv", "categories.csv"],
            "customers": ["desafio_tecnico_ai_eng - customers.csv", "customers.csv"],
            "products": ["desafio_tecnico_ai_eng - products.csv", "products.csv"],
            "promotions": ["desafio_tecnico_ai_eng - promotions.csv", "promotions.csv"],
            "orders": ["desafio_tecnico_ai_eng - orders.csv", "orders.csv"],
            "order_items": ["desafio_tecnico_ai_eng - order_items.csv", "order_items.csv"]
        }

        for table_name, candidates in file_mapping.items():
            loaded = False
            for cand in candidates:
                file_path = self.data_dir / cand
                if file_path.exists():
                    self._load_csv(cursor, table_name, file_path)
                    loaded = True
                    break
            if not loaded:
                logger.warning(f"Could not find CSV file for table: {table_name} in {self.data_dir}")

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prod_cat ON products(category_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prod_name ON products(name);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prom_prod ON promotions(product_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ord_cust ON orders(customer_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ord_trk ON orders(tracking_code);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_ord ON order_items(order_id);")

        self._conn.commit()
        logger.info("SQLite database successfully populated from CSV files.")

    def _load_csv(self, cursor: sqlite3.Cursor, table_name: str, file_path: Path):
        try:
            with open(file_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                if not rows:
                    return

                columns = list(rows[0].keys())
                placeholders = ", ".join(["?" for _ in columns])
                col_names = ", ".join([f'"{c}"' for c in columns])
                insert_sql = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"

                data_tuples = []
                for row in rows:
                    data_tuples.append([row[col] for col in columns])

                cursor.executemany(insert_sql, data_tuples)
                logger.info(f"Loaded {len(data_tuples)} records into table '{table_name}'.")
        except Exception as e:
            logger.error(f"Error loading {file_path} into table '{table_name}': {e}")

db_service = DatabaseService()
