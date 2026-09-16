from flask import Flask, jsonify
from data_collector import (
    create_database,
    collect_market_data,
    get_stock,
    database_stats
)

app = Flask(__name__)

create_database()


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
                font-family: Arial, sans-serif;
                background: #0b1220;
                color: white;
                padding: 20px;
                margin: 0;
            }}

            .card {{
                background: #172033;
                padding: 18px;
                margin: 12px 0;
                border-radius: 14px;
            }}

            button {{
                background: #21c77a;
                color: white;
                border: none;
                padding: 14px 20px;
                border-radius: 10px;
                font-size: 16px;
            }}

            a {{
                color: #21c77a;
                text-decoration: none;
            }}
        </style>
    </head>

    <body>

        <h1>NEPSE AI Analyzer</h1>

        <div class="card">
            <h2>Market Data</h2>

            <p>
                Stocks stored:
                <b>{stats["stocks"]}</b>
            </p>

            <p>
                Records:
                <b>{stats["records"]}</b>
            </p>

            <a href="/update">
                <button>Update Market Data</button>
            </a>
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

        stats = database_stats()

        return jsonify({
            "success": True,
            "records_processed": saved,
            "database": stats
        })

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
