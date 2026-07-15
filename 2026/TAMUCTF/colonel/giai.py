from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

key = b"Qx+KvRQ1NQRR66IxSM5VjjrGKg09FH2e"
iv = b"1234567890123456"

with open("flag.enc", "rb") as f:
    ct = f.read()

pt = AES.new(key, AES.MODE_CBC, iv).decrypt(ct)

print("raw:", pt)

try:
    print("unpadded:", unpad(pt, 16))
except Exception as e:
    print("unpad failed:", e)
