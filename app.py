from flask import Flask, jsonify
import os
import json

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Monitoring Pasang Surut Air Laut"})

@app.route("/data")
def get_data():
    file_path = "./data/sea_level.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
        return jsonify(data)
    else:
        return jsonify({"error": "Data tidak ditemukan"}), 404

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
