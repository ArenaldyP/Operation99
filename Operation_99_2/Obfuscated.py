import zlib
import base64
import os


# Fungsi untuk mengobfuskasi kode satu lapisan
def obfuscate_layer(code):
    # Langkah 1: Encode ke UTF-8 bytes
    code_bytes = code.encode('utf-8')

    # Langkah 2: Kompresi dengan ZLIB
    compressed = zlib.compress(code_bytes)

    # Langkah 3: Encode ke Base64
    base64_encoded = base64.b64encode(compressed)

    # Langkah 4: Balik string (reverse)
    reversed_str = base64_encoded[::-1]

    # Buat kode yang akan mengeksekusi dan membuka lapisan ini
    # Menggunakan __import__ untuk impor dinamis zlib dan base64
    obfuscated = f"exec(__import__('zlib').decompress(__import__('base64').b64decode('{reversed_str.decode('utf-8')}'[::-1])))"
    return obfuscated


# Fungsi untuk mengobfuskasi kode dengan beberapa lapisan
def obfuscate_code(input_code, layers=65):
    current_code = input_code
    for _ in range(layers):
        current_code = obfuscate_layer(current_code)
    return current_code


# Membaca kode dari file eksternal
input_file = "Main99.py"  # Nama file input
try:
    with open(input_file, "r") as f:
        sample_code = f.read()
except FileNotFoundError:
    print(f"Error: File '{input_file}' tidak ditemukan. Pastikan file ada di direktori yang sama.")
    exit(1)

# Obfuskasi kode dengan 65 lapisan (seperti dalam laporan)
obfuscated_code = obfuscate_code(sample_code, layers=10)

# Simpan kode yang diobfuskasi ke file
output_file = "obfuscated_script.py"
with open(output_file, "w") as f:
    f.write(obfuscated_code)

print(f"Obfuscated code telah disimpan ke {output_file}")

# Untuk menjalankan langsung (opsional, uncomment untuk tes)
# exec(obfuscated_code)