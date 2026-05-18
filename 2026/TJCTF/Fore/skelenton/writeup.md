# Đề bài

<img width="1021" height="370" alt="image" src="https://github.com/user-attachments/assets/6b99a65a-d7a2-4d70-a56a-d6084fc65b6b" />


Đọc đề bài là ta biết ta sẽ phải khôi phục ảnh từ file txt chứa hash của nó.

Mở hash.txt, ta thấy hash có dạng:

flag.zip/flag.png:$pkzip2$...

Đây là hash do zip2john sinh ra cho ZIP dùng cơ chế mã hóa cũ kiểu ZipCrypto. 

Trong hash cũng có đầy đủ thông tin về entry flag.png, bao gồm CRC, kích thước file, method nén, và encrypted data.

Quan sát mã hash 1 chút, sau khi vứt lên gpt phân tích thì ta nhận được 

encrypted size = 0x12c = 300 bytes

plaintext size = 0x120 = 288 bytes

300 - 288 = 12 bytes, chênh lệch 12 bytes

CRC32 = c8a6617a

filename = flag.png

với ZipCrypto, trước dữ liệu thật của file sẽ có thêm 12 byte encryption header. Vì thế ta biết được

encrypted blob = 12 byte ZipCrypto header + encrypted flag.png

Nếu hash chứa đủ encrypted data và file bên trong ZIP được Stored, không bị nén, thì sau khi giải mã ZipCrypto, ta sẽ thu được PNG gốc.

Ta dựng file zip với script như sau 
```bash
import re
import struct
import sys

if len(sys.argv) != 3:
    print(f"Usage: python3 {sys.argv[0]} hash.txt recovered_fixed.zip")
    sys.exit(1)

hash_path = sys.argv[1]
out_zip = sys.argv[2]

line = open(hash_path, "r", encoding="utf-8").read().strip()

# Ví dụ prefix:
# flag.zip/flag.png:$pkzip2$...
left = line.split(":", 1)[0]

if "/" in left:
    zip_name, filename = left.split("/", 1)
else:
    zip_name = "flag.zip"
    filename = "flag.png"

m = re.search(r"\$pkzip2\$(.*?)\*\$/pkzip2\$", line)
if not m:
    raise SystemExit("[-] Could not find $pkzip2$ body")

p = m.group(1).split("*")

# Với hash của bài này:
# p[2]  = data type
# p[4]  = encrypted/compressed size
# p[5]  = plaintext/uncompressed size
# p[6]  = CRC32
# p[9]  = compression method
# p[10] = encrypted data length
# p[11] = CS
# p[12] = TC
# p[13] = encrypted blob
dt = int(p[2], 16)
enc_size = int(p[4], 16)
plain_size = int(p[5], 16)
crc = int(p[6], 16)
method = int(p[9], 16)
data_len = int(p[10], 16)
cs = p[11]
tc = p[12]
enc = bytes.fromhex(p[13])

if dt != 2:
    raise SystemExit(f"[-] Expected inline encrypted data, got DT={dt}")

if len(enc) != data_len:
    raise SystemExit(f"[-] Encrypted data length mismatch: got {len(enc)}, expected {data_len}")

if len(enc) != enc_size:
    raise SystemExit(f"[-] Encrypted size mismatch: got {len(enc)}, expected {enc_size}")

fn = filename.encode("utf-8")
extra = b""

# ZipCrypto + data descriptor.
# Bit 0  = encrypted
# Bit 3  = data descriptor follows file data
general_flag = 0x0009

version_needed = 20

# TC trong hash là timestamp/check field.
# Giữ đúng TC rất quan trọng để bkcrack xử lý đúng header/check byte.
mtime = int(tc, 16)
mdate = 0

# Local file header.
# Khi dùng data descriptor, local header có thể để CRC/size = 0.
local_header = struct.pack(
    "<IHHHHHIIIHH",
    0x04034B50,       # local file header signature
    version_needed,
    general_flag,
    method,
    mtime,
    mdate,
    0,                # CRC placeholder
    0,                # compressed size placeholder
    0,                # uncompressed size placeholder
    len(fn),
    len(extra),
) + fn + extra

# Data descriptor sau encrypted data.
data_descriptor = struct.pack(
    "<IIII",
    0x08074B50,
    crc,
    enc_size,
    plain_size,
)

central_directory_offset = len(local_header) + len(enc) + len(data_descriptor)

# Central directory header.
central_directory = struct.pack(
    "<IHHHHHHIIIHHHHHII",
    0x02014B50,       # central directory signature
    0x0314,           # version made by
    version_needed,
    general_flag,
    method,
    mtime,
    mdate,
    crc,
    enc_size,
    plain_size,
    len(fn),
    len(extra),
    0,                # file comment length
    0,                # disk number start
    0,                # internal file attributes
    0,                # external file attributes
    0,                # local header offset
) + fn + extra

# End of central directory.
eocd = struct.pack(
    "<IHHHHIIH",
    0x06054B50,
    0,
    0,
    1,
    1,
    len(central_directory),
    central_directory_offset,
    0,
)

with open(out_zip, "wb") as f:
    f.write(local_header)
    f.write(enc)
    f.write(data_descriptor)
    f.write(central_directory)
    f.write(eocd)

print("[+] Rebuilt ZIP:", out_zip)
print("[+] Original ZIP name :", zip_name)
print("[+] Entry name        :", filename)
print("[+] Method            :", method, "(0 = Store)")
print("[+] CRC32             :", f"{crc:08x}")
print("[+] Encrypted size    :", enc_size)
print("[+] Plaintext size    :", plain_size)
print("[+] CS                :", cs)
print("[+] TC / mtime        :", tc)
print("[+] Encrypted blob len:", len(enc))
```
kết quả cho ra 

```bash
┌──(chuatebongtoi2604㉿chuatebongtoi2604)-[/mnt/d/ctftraining/tjctf/fore/skelenton]
└─$ python3 hash_to_zip_fixed.py hash.txt recovered_fixed.zip
[+] Rebuilt ZIP: recovered_fixed.zip
[+] Original ZIP name : flag.zip
[+] Entry name        : flag.png
[+] Method            : 0 (0 = Store)
[+] CRC32             : c8a6617a
[+] Encrypted size    : 300
[+] Plaintext size    : 288
[+] CS                : c8a6
[+] TC / mtime        : 81bd
[+] Encrypted blob len: 300

┌──(chuatebongtoi2604㉿chuatebongtoi2604)-[/mnt/d/ctftraining/tjctf/fore/skelenton]
└─$ bkcrack -L recovered_fixed.zip
bkcrack 1.8.1 - 2025-10-25
Archive: recovered_fixed.zip
Index Encryption Compression CRC32    Uncompressed  Packed size Name
----- ---------- ----------- -------- ------------ ------------ ----------------
    0 ZipCrypto  Store       c8a6617a          288          300 flag.png
```

Vì file là flag.png, ta biết file PNG luôn bắt đầu bằng signature:

89 50 4E 47 0D 0A 1A 0A

Ngay sau đó thường là chunk IHDR:

00 00 00 0D 49 48 44 52

Tạo file known plaintext:
```bash
python3 - << 'PY'
open("plain.bin", "wb").write(bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452"
))
PY
```
Kiểm tra:

xxd plain.bin

Kết quả:

00000000: 8950 4e47 0d0a 1a0a 0000 000d 4948 4452  .PNG........IHDR

Ta biết 16 byte đầu của plaintext flag.png.

---
Từ đây ta sẽ dựng ZipCrypto keys bằng plaintext đã biết
```bash
bkcrack -C recovered_fixed.zip -c flag.png -p plain.bin -o 0
```
<img width="785" height="253" alt="image" src="https://github.com/user-attachments/assets/010211f8-53f8-43c3-862e-4aef59f5cb38" />

Ta được key c639d1ca b1fd3d6c 25bb9b08

Ta lấy key này giải mã và lấy file flag.png
```bash
bkcrack -C recovered_fixed.zip -c flag.png \
  -k c639d1ca b1fd3d6c 25bb9b08 \
  -d recovered_flag.png
```
<img width="220" height="20" alt="recovered_flag" src="https://github.com/user-attachments/assets/582a2502-33a4-46d2-9ece-c37f43760d5f" />

--- 
## Flag 
```bash
tjctf{1ts_4ll_ab0ut_th3_keys}
```
