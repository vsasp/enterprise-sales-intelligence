from pathlib import Path
import sqlite3
from contextlib import contextmanager
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "enterprise_sales.db"

@contextmanager
def get_connection():
    """Yield a SQLite connection and always commit/rollback and close it."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def create_tables():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            transaction_date TEXT NOT NULL,
            customer_id TEXT,
            customer_name TEXT,
            product_id TEXT,
            product_name TEXT,
            category TEXT,
            branch TEXT,
            quantity REAL,
            unit_price REAL,
            discount REAL,
            gross_sales REAL,
            discount_amount REAL,
            net_sales REAL,
            payment_method TEXT,
            order_status TEXT,
            source_file TEXT,
            inserted_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS data_quality_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT,
            source_file TEXT,
            issue TEXT NOT NULL,
            logged_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS anomalies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT,
            anomaly_type TEXT NOT NULL,
            details TEXT,
            net_sales REAL,
            detected_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);
        CREATE INDEX IF NOT EXISTS idx_transactions_branch ON transactions(branch);
        CREATE INDEX IF NOT EXISTS idx_transactions_product ON transactions(product_id);
        """)

def _value(row, col):
    value = row.get(col)
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            pass
    return value

def save_sales_data(df):
    if df.empty:
        return {"inserted": 0, "skipped": 0}
    required = [
        "Transaction_ID", "Transaction_Date", "Customer_ID", "Customer_Name",
        "Product_ID", "Product_Name", "Category", "Branch", "Quantity",
        "Unit_Price", "Discount", "Gross_Sales", "Discount_Amount",
        "Net_Sales", "Payment_Method", "Order_Status"
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError("Cannot save data; missing columns: " + ", ".join(missing))
    sql = """INSERT OR IGNORE INTO transactions (
        transaction_id, transaction_date, customer_id, customer_name, product_id,
        product_name, category, branch, quantity, unit_price, discount, gross_sales,
        discount_amount, net_sales, payment_method, order_status, source_file
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    rows = []
    for _, row in df.iterrows():
        date_value = pd.to_datetime(row["Transaction_Date"]).strftime("%Y-%m-%d")
        rows.append((
            str(_value(row, "Transaction_ID")), date_value,
            _value(row, "Customer_ID"), _value(row, "Customer_Name"),
            _value(row, "Product_ID"), _value(row, "Product_Name"),
            _value(row, "Category"), _value(row, "Branch"),
            _value(row, "Quantity"), _value(row, "Unit_Price"),
            _value(row, "Discount"), _value(row, "Gross_Sales"),
            _value(row, "Discount_Amount"), _value(row, "Net_Sales"),
            _value(row, "Payment_Method"), _value(row, "Order_Status"),
            _value(row, "Source_File")
        ))
    with get_connection() as conn:
        before = conn.total_changes
        conn.executemany(sql, rows)
        inserted = conn.total_changes - before
    return {"inserted": inserted, "skipped": len(rows) - inserted}

def save_quality_issues(df):
    if df.empty:
        return 0
    rows = []
    for _, row in df.iterrows():
        rows.append((
            str(_value(row, "Transaction_ID") or ""),
            str(_value(row, "Source_File") or ""),
            str(_value(row, "Validation_Issue") or "Unknown validation issue")
        ))
    with get_connection() as conn:
        conn.executemany(
            "INSERT INTO data_quality_logs(transaction_id, source_file, issue) VALUES (?, ?, ?)",
            rows
        )
    return len(rows)

def save_anomalies(df):
    if df.empty:
        return 0
    rows = [
        (str(_value(row, "Transaction_ID") or ""),
         str(_value(row, "Anomaly_Type") or ""),
         str(_value(row, "Details") or ""),
         _value(row, "Net_Sales"))
        for _, row in df.iterrows()
    ]
    with get_connection() as conn:
        conn.executemany(
            "INSERT INTO anomalies(transaction_id, anomaly_type, details, net_sales) VALUES (?, ?, ?, ?)",
            rows
        )
    return len(rows)

def query_df(sql, params=()):
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)

def get_database_summary():
    with get_connection() as conn:
        transactions = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        quality = conn.execute("SELECT COUNT(*) FROM data_quality_logs").fetchone()[0]
        anomalies = conn.execute("SELECT COUNT(*) FROM anomalies").fetchone()[0]
        revenue = conn.execute("SELECT COALESCE(SUM(net_sales), 0) FROM transactions").fetchone()[0]
    return {"transactions_in_database": transactions, "quality_issues_logged": quality,
            "anomalies_logged": anomalies, "database_net_sales": round(float(revenue), 2)}
