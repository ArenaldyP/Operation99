import zlib
import base64

def obfuscate_code(code):
    # Compress using ZLIB
    compressed = zlib.compress(code.encode('utf-8'))

    # Encode to Base64 and convert to string
    encoded = base64.b64encode(compressed).decode('utf-8')

    # Reverse the string 15 times
    for _ in range(15):
        encoded = encoded[::-1]

    return encoded

def obfuscate_file(input_file, output_file):
    # Read the file content
    with open(input_file, "r", encoding="utf-8") as f:
        original_code = f.read()

    # Obfuscate the code
    obfuscated_code = obfuscate_code(original_code)

    # Generate the obfuscated Python code
    obfuscated_py_code = f"""
_ = lambda __: __import__('zlib').decompress(__import__('base64').b64decode(__[::-1].decode('utf-8').encode('utf-8')))
exec((_)(b'{obfuscated_code}'))
"""

    # Save the obfuscated code to the output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(obfuscated_py_code)

    print(f"File {input_file} has been obfuscated with 15 reverses and saved to {output_file}")

# Example usage
input_file = "Payload.py"  # Python file to obfuscate
output_file = "obfuscated_script.py"  # Output obfuscated file

obfuscate_file(input_file, output_file)