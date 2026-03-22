from flask import Flask, request, jsonify
import os, time, uuid

app = Flask(__name__)
SECRET = os.environ.get("TV_SECRET", "")

LAST_SIGNAL = None

@app.route("/", methods=["GET"])
def home():
    return "TV Webhook Bridge running"

@app.route("/tv", methods=["POST"])
def webhook():
    global LAST_SIGNAL
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No JSON"}), 400

    if data.get("secret") != SECRET:
        return jsonify({"error": "Unauthorized"}), 403

    symbol = str(data.get("symbol", "")).upper()
    side   = str(data.get("side", "")).lower()
    qty    = str(data.get("contracts", "1"))

    if side not in ("buy", "sell"):
        return jsonify({"error": "Invalid side"}), 400

    LAST_SIGNAL = {
        "id": str(uuid.uuid4()),
        "ts": int(time.time()),
        "symbol": symbol,
        "side": side,
        "contracts": qty
    }

    print("Signal received:", LAST_SIGNAL)
    return jsonify({"status": "ok", "id": LAST_SIGNAL["id"]}), 200

@app.route("/pull", methods=["GET"])
def pull():
    global LAST_SIGNAL
    sec = request.args.get("secret", "")
    if sec != SECRET:
        return jsonify({"error": "Unauthorized"}), 403

    if not LAST_SIGNAL:
        return jsonify({"status": "empty"}), 200

    # IMPORTANT : on “consomme” le signal pour éviter doublons
    sig = LAST_SIGNAL
    LAST_SIGNAL = None
    return jsonify({"status": "ok", "signal": sig}), 200

# ✅ Health check pour Render
@app.route("/healthz", methods=["GET"])
def health():
    return "OK", 200
