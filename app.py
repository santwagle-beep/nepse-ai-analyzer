from flask import Flask, jsonify
from data_collector import create_database, test_source

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>NEPSE AI Analyzer</h1>
    <p>System: ONLINE</p>
    <p>Collector: READY</p>
    <p>Database: READY</p>
    """

@app.route("/test-source")
def test_source_route():
    result = test_source()
    return jsonify({
        "nepsealpha_connection": result
    })

@app.route("/health")
def health():
    return jsonify({"status": "online"})

create_database()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
