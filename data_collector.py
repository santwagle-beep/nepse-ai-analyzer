import csv
import io
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

DATABASE = "nepse.db"

# NepseAlpha historical price page
SOURCE_URL = "https://nepsealpha.com/nepse-data"

WATCHLIST = [
    "SICL",
    "NLG",
    "MAKAR",
    "HATHY",
]


def create_database():
    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS ohlcv (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            turnover REAL,
            source TEXT,
            created_at TEXT,
            UNIQUE(symbol, date)
        )
    """)

    connection.commit()
    connection.close()


def save_candle(
    symbol,
    date,
    open_price,
    high,
    low,
    close,
    volume=None,
    turnover=None,
):
    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        INSERT OR REPLACE INTO ohlcv
        (
            symbol,
            date,
            open,
            high,
            low,
            close,
            volume,
            turnover,
            source,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        symbol,
        date,
        open_price,
        high,
        low,
        close,
        volume,
        turnover,
        "NepseAlpha",
        datetime.utcnow().isoformat(),
    ))

    connection.commit()
    connection.close()


def validate_candle(open_price, high, low, close):
    values = [open_price, high, low, close]

    if any(value is None for value in values):
        return False

    if high < low:
        return False

    if open_price < low or open_price > high:
        return False

    if close < low or close > high:
        return False

    return True


def database_summary():
    connection = sqlite3.connect(DATABASE)

    rows = connection.execute("""
        SELECT symbol, COUNT(*), MAX(date)
        FROM ohlcv
        GROUP BY symbol
        ORDER BY symbol
    """).fetchall()

    connection.close()

    return rows


def test_source():
    print("Testing NepseAlpha connection...")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 "
            "like Mac OS X) AppleWebKit/605.1.15 "
            "Version/17.0 Mobile/15E148 Safari/604.1"
        )
    }

    try:
        response = requests.get(
            SOURCE_URL,
            headers=headers,
            timeout=20
        )

        print("HTTP status:", response.status_code)
        print("Downloaded bytes:", len(response.content))

        if response.status_code == 200:
            print("NepseAlpha connection: OK")
            return True

        print("NepseAlpha connection: FAILED")
        return False

    except requests.RequestException as error:
        print("Connection error:", error)
        return False


def main():
    print("=" * 50)
    print("NEPSE AI ANALYZER - DATA COLLECTOR")
    print("=" * 50)

    create_database()

    connected = test_source()

    if not connected:
        print("No data saved because the source could not be verified.")
        return

    print()
    print("Database ready.")
    print("Watchlist:")

    for symbol in WATCHLIST:
        print(" -", symbol)

    print()
    print("Current database:")
    
    summary = database_summary()

    if not summary:
        print("No OHLCV candles stored yet.")
    else:
        for symbol, count, last_date in summary:
            print(
                f"{symbol}: {count} candles, "
                f"latest={last_date}"
            )

    print()
    print("Collector test completed.")
    print()
    print("Next step:")
    print("Connect the verified NepseAlpha OHLCV source.")


if __name__ == "__main__":
    main()
