import sqlite3
from datetime import datetime

DATABASE = "nepse.db"


def create_candle_table():
    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS daily_candles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            trade_date TEXT NOT NULL,
            open REAL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            close REAL NOT NULL,
            volume REAL,
            turnover REAL,
            trades INTEGER,
            candle_complete INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            UNIQUE(symbol, trade_date)
        )
    """)

    connection.commit()
    connection.close()


def build_daily_candle(symbol, trade_date):
    connection = sqlite3.connect(DATABASE)

    rows = connection.execute("""
        SELECT
            ltp,
            high,
            low,
            volume,
            turnover,
            trades,
            data_time
        FROM market_data
        WHERE symbol = ?
        AND substr(data_time, 1, 10) = ?
        ORDER BY data_time ASC
    """, (symbol.upper(), trade_date)).fetchall()

    if not rows:
        connection.close()
        return None

    # Highest and lowest prices observed during the session.
    high = max(row[1] for row in rows if row[1] is not None)
    low = min(row[2] for row in rows if row[2] is not None)

    # First and last observed prices.
    first_price = rows[0][0]
    last_price = rows[-1][0]

    # We currently do not have a true Open field
    # in the source feed.
    open_price = None

    close = last_price

    # Use the latest cumulative market totals.
    volume = rows[-1][3]
    turnover = rows[-1][4]
    trades = rows[-1][5]

    complete = (
        open_price is not None
        and high is not None
        and low is not None
        and close is not None
    )

    connection.execute("""
        INSERT OR REPLACE INTO daily_candles
        (
            symbol,
            trade_date,
            open,
            high,
            low,
            close,
            volume,
            turnover,
            trades,
            candle_complete,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        symbol.upper(),
        trade_date,
        open_price,
        high,
        low,
        close,
        volume,
        turnover,
        trades,
        int(complete),
        datetime.utcnow().isoformat()
    ))

    connection.commit()
    connection.close()

    return {
        "symbol": symbol.upper(),
        "date": trade_date,
        "open": open_price,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
        "turnover": turnover,
        "trades": trades,
        "complete": complete
    }


def build_all_daily_candles(trade_date):
    connection = sqlite3.connect(DATABASE)

    symbols = connection.execute("""
        SELECT DISTINCT symbol
        FROM market_data
        WHERE substr(data_time, 1, 10) = ?
        ORDER BY symbol
    """, (trade_date,)).fetchall()

    connection.close()

    results = []

    for row in symbols:
        candle = build_daily_candle(
            row[0],
            trade_date
        )

        if candle:
            results.append(candle)

    return results


def get_candle(symbol, trade_date):
    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    row = connection.execute("""
        SELECT *
        FROM daily_candles
        WHERE symbol = ?
        AND trade_date = ?
    """, (
        symbol.upper(),
        trade_date
    )).fetchone()

    connection.close()

    if row:
        return dict(row)

    return None


if __name__ == "__main__":

    create_candle_table()

    print("Daily candle table ready.")
