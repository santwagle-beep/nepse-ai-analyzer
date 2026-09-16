import sqlite3
import requests
from datetime import datetime

DATABASE = "nepse.db"

YONEPSE_URL = "https://shubhamnpk.github.io/yonepse/data/nepse_data.json"


def create_database():
    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            name TEXT,
            ltp REAL,
            previous_close REAL,
            high REAL,
            low REAL,
            change REAL,
            percent_change REAL,
            volume REAL,
            turnover REAL,
            trades INTEGER,
            market_cap REAL,
            data_time TEXT,
            collected_at TEXT,
            UNIQUE(symbol, data_time)
        )
    """)

    connection.commit()
    connection.close()


def collect_market_data():
    response = requests.get(
        YONEPSE_URL,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    connection = sqlite3.connect(DATABASE)

    saved = 0

    for stock in data:

        symbol = stock.get("symbol")

        if not symbol:
            continue

        data_time = stock.get("last_updated")

        if not data_time:
            data_time = datetime.utcnow().isoformat()

        connection.execute("""
            INSERT OR REPLACE INTO market_data
            (
                symbol,
                name,
                ltp,
                previous_close,
                high,
                low,
                change,
                percent_change,
                volume,
                turnover,
                trades,
                market_cap,
                data_time,
                collected_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            symbol,
            stock.get("name"),
            stock.get("ltp"),
            stock.get("previous_close"),
            stock.get("high"),
            stock.get("low"),
            stock.get("change"),
            stock.get("percent_change"),
            stock.get("volume"),
            stock.get("turnover"),
            stock.get("trades"),
            stock.get("market_cap"),
            data_time,
            datetime.utcnow().isoformat()
        ))

        saved += 1

    connection.commit()
    connection.close()

    return saved


def get_stock(symbol):
    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    row = connection.execute("""
        SELECT *
        FROM market_data
        WHERE symbol = ?
        ORDER BY data_time DESC
        LIMIT 1
    """, (symbol.upper(),)).fetchone()

    connection.close()

    if row:
        return dict(row)

    return None


def database_stats():
    connection = sqlite3.connect(DATABASE)

    stocks = connection.execute("""
        SELECT COUNT(DISTINCT symbol)
        FROM market_data
    """).fetchone()[0]

    records = connection.execute("""
        SELECT COUNT(*)
        FROM market_data
    """).fetchone()[0]

    connection.close()

    return {
        "stocks": stocks,
        "records": records
    }


if __name__ == "__main__":

    print("Creating database...")

    create_database()

    print("Collecting NEPSE market data...")

    saved = collect_market_data()

    print("Records processed:", saved)

    print("Database statistics:")

    print(database_stats())
