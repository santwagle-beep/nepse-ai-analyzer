from flask import Flask, jsonify
from data_collector import (
    create_database,
    collect_market_data,
    database_stats
)
from candle_engine import (
    create_candle_table,
    build_all_daily_candles,
    get_candle
)

app = Flask(__name__)

create_database()
create_candle_table()


@app.route("/")
def home():

    stats = database_stats()

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <title>NEPSE AI Analyzer</title>

        <style>
            body {{
                font-family: Arial;
                background: #0b1220;
                color: white;
                padding: 20px;
            }}

            .card {{
                background: #172033;
                padding: 18px;
                margin: 12px 0;
                border-radius: 14px;
            }}

            a {{
                color: #21c77a;
            }}

            button {{
                background: #21c77a;
                color: white;
                border: 0;
                padding: 14px;
                border-radius: 10px;
                font-size: 16px;
            }}
        </style>
    </head>

    <body>

        <h1>NEPSE AI Analyzer</h1>

        <div class="card">

            <h2>Market Database</h2>

            <p>
                Stocks:
                <b>{stats["stocks"]}</b>
            </p>

            <p>
                Records:
                <b>{stats["records"]}</b>
            </p>

            <p>
                <a href="/update">
                    <button>Update Market Data</button>
                </a>
            </p>

        </div>

        <div class="card">

            <h2>Daily Candle Builder</h2>

            <p>
                <a href="/update-candles">
                    <button>Build Daily Candles</button>
                </a>
            </p>

        </div>

        <div class="card">

            <h2>Watchlist</h2>

            <p><a href="/stock/SICL">SICL</a></p>
            <p><a href="/stock/NLG">NLG</a></p>
            <p><a href="/stock/MAKAR">MAKAR</a></p>
            <p><a href="/stock/HATHY">HATHY</a></p>

        </div>

    </body>
    </html>
    """


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


@app.route("/update-candles")
def update_candles():

    try:

        from datetime import datetime

        trade_date = datetime.utcnow().strftime("%Y-%m-%d")

        candles = build_all_daily_candles(
            trade_date
        )

        return jsonify({
            "success": True,
            "trade_date": trade_date,
            "candles_created": len(candles),
            "sample": candles[:5]
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.route("/stock/<symbol>")
def stock(symbol):

    from data_collector import get_stock

    data = get_stock(symbol)

    if not data:

        return jsonify({
            "error": "Stock not found",
            "symbol": symbol.upper()
        }), 404

    return jsonify(data)


@app.route("/candle/<symbol>/<trade_date>")
def candle(symbol, trade_date):

    data = get_candle(
        symbol,
        trade_date
    )

    if not data:

        return jsonify({
            "error": "Candle not found"
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
