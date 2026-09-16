import sqlite3
import requests
import csv
import io
from datetime import datetime

DATABASE = "nepse.db"

BASE_URL = (
    "https://raw.githubusercontent.com/"
    "binayabaral/nepal-market-data/main/data/nepse/"
)

SYMBOLS = [
    "HATHY",
    "SICL",
    "NLG",
    "MAKAR",
]


def create_history_table():

    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS historical_candles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            trade_date TEXT NOT NULL,
            open REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            close REAL NOT NULL,
            percent_change REAL,
            volume REAL,
            turnover REAL,
            status TEXT,
            source TEXT,
            imported_at TEXT,
            UNIQUE(symbol, trade_date)
        )
    """)

    connection.commit()
    connection.close()


def valid_candle(open_price, high, low, close):

    if None in (
        open_price,
        high,
        low,
        close
    ):
        return False

    if high < low:
        return False

    if not (
        low <= open_price <= high
        and low <= close <= high
    ):
        return False

    return True


def import_symbol(symbol):

    url = BASE_URL + symbol.upper() + ".csv"

    response = requests.get(
        url,
        timeout=30
    )

    if response.status_code != 200:

        return {
            "symbol": symbol,
            "success": False,
            "status_code": response.status_code,
            "imported": 0
        }

    reader = csv.DictReader(
        io.StringIO(
            response.text
        )
    )

    connection = sqlite3.connect(DATABASE)

    imported = 0
    skipped = 0

    for row in reader:

        try:

            trade_date = row["published_date"]

            open_price = float(row["open"])
            high = float(row["high"])
            low = float(row["low"])
            close = float(row["close"])

            percent_change = (
                float(row["per_change"])
                if row.get("per_change")
                else None
            )

            volume = (
                float(row["traded_quantity"])
                if row.get("traded_quantity")
                else None
            )

            turnover = (
                float(row["traded_amount"])
                if row.get("traded_amount")
                else None
            )

            status = row.get("status")

            if not valid_candle(
                open_price,
                high,
                low,
                close
            ):
                skipped += 1
                continue

            connection.execute("""
                INSERT OR REPLACE INTO historical_candles
                (
                    symbol,
                    trade_date,
                    open,
                    high,
                    low,
                    close,
                    percent_change,
                    volume,
                    turnover,
                    status,
                    source,
                    imported_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol.upper(),
                trade_date,
                open_price,
                high,
                low,
                close,
                percent_change,
                volume,
                turnover,
                status,
                "nepal-market-data",
                datetime.utcnow().isoformat()
            ))

            imported += 1

        except (
            ValueError,
            KeyError,
            TypeError
        ):
            skipped += 1

    connection.commit()
    connection.close()

    return {
        "symbol": symbol.upper(),
        "success": True,
        "imported": imported,
        "skipped": skipped
    }


def import_watchlist():

    create_history_table()

    results = []

    for symbol in SYMBOLS:

        try:

            result = import_symbol(
                symbol
            )

        except Exception as error:

            result = {
                "symbol": symbol,
                "success": False,
                "error": str(error)
            }

        results.append(result)

    return results


def get_history(
    symbol,
    limit=100
):

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    rows = connection.execute("""
        SELECT
            symbol,
            trade_date,
            open,
            high,
            low,
            close,
            percent_change,
            volume,
            turnover,
            status
        FROM historical_candles
        WHERE symbol = ?
        ORDER BY trade_date DESC
        LIMIT ?
    """, (
        symbol.upper(),
        limit
    )).fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


def history_stats():

    connection = sqlite3.connect(DATABASE)

    stocks = connection.execute("""
        SELECT COUNT(DISTINCT symbol)
        FROM historical_candles
    """).fetchone()[0]

    candles = connection.execute("""
        SELECT COUNT(*)
        FROM historical_candles
    """).fetchone()[0]

    connection.close()

    return {
        "stocks": stocks,
        "candles": candles
    }


if __name__ == "__main__":

    results = import_watchlist()

    for result in results:
        print(result)

    print()
    print(
        "History statistics:",
        history_stats()
    )
