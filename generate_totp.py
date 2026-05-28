import time
import hmac
import hashlib
import struct
import base64
import os

SECRET = "7FEJUNUEC6IA6XD3TNM6MIXMERBY2IDC"
OUTPUT_FILE = "/home/rishab/QuerySafe/totp_code.txt"

def get_totp(secret):
    try:
        key = base64.b32decode(secret, True)
        msg = struct.pack(">Q", int(time.time()) // 30)
        hs = hmac.new(key, msg, hashlib.sha1).digest()
        o = hs[19] & 15
        h = (struct.unpack(">I", hs[o:o+4])[0] & 0x7fffffff) % 1000000
        return f"{h:06d}"
    except Exception as e:
        return str(e)

print("Starting TOTP generator daemon...")
while True:
    code = get_totp(SECRET)
    try:
        with open(OUTPUT_FILE, "w") as f:
            f.write(code)
    except Exception as e:
        print("Error writing TOTP code:", e)
    time.sleep(5)
