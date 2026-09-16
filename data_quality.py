import sqlite3
from datetime import datetime

DATABASE = "nepse.db"


def check_stock(symbol):

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    rows = connection.execute("""
        SELECT
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
        ORDER BY trade_date ASC
    """, (symbol.upper(),)).fetchall()

    connection.close()

    if not rows:
        return {
            "symbol": symbol.upper(),
            "found": False
        }

    problems = []
    dates = []

    for row in rows:

        date = row["trade_date"]
        open_price = row["open"]
        high = row["high"]
        low = row["low"]
        close = row["close"]
        volume = row["volume"]

        dates.append(date)

        if low > high:
            problems.append({
                "date": date,
                "problem": "low_above_high"
            })

        if not (
            low <= open_price <= high
        ):
            problems.append({
                "date": date,
                "problem": "open_outside_range"
            })

        if not (
            low <= close <= high
        ):
            problems.append({
                "date": date,
                "problem": "close_outside_range"
            })

        if volume is not None and volume < 0:
            problems.append({
                "date": date,
                "problem": "negative_volume"
            })

    duplicates = []

    seen = set()

    for date in dates:

        if date in seen:
            duplicates.append(date)
        else:
            seen.add(date)

    large_moves = []

    previous_close = None

    for row in rows:

        close = row["close"]
        date = row["trade_date"]

        if previous_close and previous_close != 0:

            move = (
                (close - previous_close)
                / previous_close
            ) * 100

            if abs(move) >= 15:

                large_moves.append({
                    "date": date,
                    "move_percent": round(
                        move,
                        2
                    )
                })

        previous_close = close

    return {
        "symbol": symbol.upper(),
        "found": True,
        "candles": len(rows),
        "first_date": rows[0]["trade_date"],
        "last_date": rows[-1]["trade_date"],
        "duplicate_dates": duplicates,
        "ohlc_problems": problems,
        "large_moves": large_moves,
        "quality": (
            "GOOD"
            if not problems and not duplicates
            else "REVIEW"
        )
    }


def check_all():

    connection = sqlite3.connect(DATABASE)

    symbols = connection.execute("""
        SELECT DISTINCT symbol
        FROM historical_candles
        ORDER BY symbol
    """).fetchall()

    connection.close()

    results = []

    for row in symbols:

        results.append(
            check_stock(row[0])
        )

    return results


def market_quality():

    results = check_all()

    good = 0
    review = 0
    total_candles = 0

    for result in results:

        total_candles += result.get(
            "candles",
            0
        )

        if result.get("quality") == "GOOD":
            good += 1
        else:
            review += 1

    return {
        "stocks_checked": len(results),
        "good": good,
        "review": review,
        "total_candles": total_candles
    }


if __name__ == "__main__":

    print(
        market_quality()
    )

    for result in check_all():

        print(result)
