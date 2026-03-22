from flask import Flask, request, jsonify
import os

app = Flask(__name__)

SECRET = os.environ.get("TV_SECRET", "")
LAST_SIGNAL = None


@app.route("/")
def home():
    return "TV Webhook Bridge running"


@app.route("/healthz")
def health():
    return "OK"


@app.route("/tv", methods=["POST"])
def webhook():
    global LAST_SIGNAL

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No JSON"}), 400

    if data.get("secret") != SECRET:
        return jsonify({"error": "Unauthorized"}), 403

    LAST_SIGNAL = data
    return jsonify({"status": "received", "data": data}), 200


@app.route("/pull", methods=["GET"])
def pull():
    global LAST_SIGNAL
    return jsonify(LAST_SIGNAL if LAST_SIGNAL else {}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
