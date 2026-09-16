from flask import Flask, jsonify

from data_collector import (
    create_database,
    collect_market_data,
    database_stats,
    get_stock
)

from candle_engine import (
    create_candle_table,
    build_all_daily_candles,
    get_candle
)

from historical_importer import (
    create_history_table,
    import_watchlist,
    get_history,
    history_stats
)

from data_quality import (
    check_stock,
    check_all,
    market_quality
)

from market_universe import get_symbols


app = Flask(__name__)

create_database()
create_candle_table()
create_history_table()


@app.route("/")
def home():

    stats = database_stats()
    history = history_stats()

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>NEPSE AI Analyzer</title>
    </head>

    <body>

        <h1>NEPSE AI Analyzer</h1>

        <p>Live stocks: {stats["stocks"]}</p>
        <p>Live records: {stats["records"]}</p>

        <p>Historical stocks: {history["stocks"]}</p>
        <p>Historical candles: {history["candles"]}</p>

        <hr>

        <p><a href="/update">Update Live Data</a></p>

        <p><a href="/import-history">Import Watchlist History</a></p>

        <p><a href="/universe">Test Market Universe</a></p>

        <p><a href="/quality">Data Quality</a></p>

        <p><a href="/history/HATHY">HATHY History</a></p>

        <p><a href="/history/SICL">SICL History</a></p>

        <p><a href="/history/NLG">NLG History</a></p>

        <p><a href="/history/MAKAR">MAKAR History</a></p>

    </body>
    </html>
    """


@app.route("/universe")
def universe():

    try:

        symbols = get_symbols()

        return jsonify({
            "success": True,
            "symbols": len(symbols),
            "sample": symbols[:50]
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.route("/update")
def update():

    try:

        saved = collect_market_data()

        return jsonify({
            "success": True,
            "records_processed": saved,
            "database": database_stats()
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.route("/import-history")
def import_history():

    try:

        results = import_watchlist()

        return jsonify({
            "success": True,
            "results": results,
            "statistics": history_stats()
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.route("/history/<symbol>")
def history(symbol):

    try:

        data = get_history(symbol, 100)

        return jsonify({
            "success": True,
            "symbol": symbol.upper(),
            "candles": data
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.route("/quality")
def quality():

    try:

        return jsonify({
            "success": True,
            "summary": market_quality(),
            "stocks": check_all()
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.route("/quality/<symbol>")
def quality_symbol(symbol):

    try:

        return jsonify(check_stock(symbol))

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.route("/stock/<symbol>")
def stock(symbol):

    data = get_stock(symbol)

    if not data:

        return jsonify({
            "error": "Stock not found",
            "symbol": symbol.upper()
        }), 404

    return jsonify(data)


@app.route("/candle/<symbol>/<trade_date>")
def candle(symbol, trade_date):

    data = get_candle(symbol, trade_date)

    if not data:

        return jsonify({
            "error": "Candle not found",
            "symbol": symbol.upper(),
            "trade_date": trade_date
        }), 404

    return jsonify(data)


@app.route("/health")
def health():

    return jsonify({
        "status": "online"
    })


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000
    )
