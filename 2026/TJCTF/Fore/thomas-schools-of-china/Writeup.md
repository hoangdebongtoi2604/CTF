# Đề bài 

<img width="966" height="366" alt="image" src="https://github.com/user-attachments/assets/38200805-54f5-4450-83a3-6069aeb769e4" />

Đề cho ta 1 file tsc lạ, chưa gặp bao giờ. 

Ta kiểm tra bằng vài lệnh file thì window cũng k nhận diện được, vậy ta soi byte, dùng xxd hay hxd đều được 

<img width="907" height="479" alt="image" src="https://github.com/user-attachments/assets/7f7c6cb3-c2ba-4edb-acab-2143bc58b233" />

Ta phân tích từng phần đầu header này 

54 53 43 46     -> ASCII: TSCF
01 00 00 00     -> version = 1
3c 00 00 00     -> 0x3c = 60
3d              -> 0x3d = 61

60 61 có thể liên quan gì đấy đến kích thước của ảnh 

Ta kiểm tra thử kích thước của file 
```bash
stat -c%s chall.tsc
```
output ra được :
```bash
14657
```
Nếu ảnh có kích thước 60x61, ta được 3660 pixels

Nếu mỗi pixel dùng đúng 4 bytes theo dạng rgba, thì tức là 3660 x 4 = 14640 bytes

So sánh với kích thước file thì kém 17 bytes, đây chính là 17 bytes header 

Ta bỏ 17 byte header đầu tiên để lấy phần ảnh thô.
```bash
dd if=chall.tsc of=pixels.rgba bs=1 skip=17 status=none
```

Sau đấy render file rgba raw bằng imagemagick
```bash
magick -size 60x61 -depth 8 rgba:pixels.rgba out.png
```

Ta không thể nhìn trực tiếp ảnh vì ảnh quá nhỏ

Sau khi có out.png, ta có thể đoán tác giả giấu flag trong các kênh rgba, vì ảnh chỉ 60 x 61 

Ta sẽ thử viết script theo flow sau 

Đọc ảnh theo thứ tự:

trái sang phải
trên xuống dưới

Với mỗi pixel:R, G, B, A

Nếu R, G, B đều là ASCII printable, thì lấy:

chr(R) + chr(G) + chr(B)

Ghép tất cả lại sẽ ra một stream, có thể cho flag 

Script giải cho bài này :
```bash
from PIL import Image
import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "out.png"

img = Image.open(path).convert("RGBA")
w, h = img.size

print(f"[+] image size: {w}x{h}")

chunks = []

for y in range(h):
    for x in range(w):
        r, g, b, a = img.getpixel((x, y))

        # Mỗi pixel là RGBA.
        # Flag được nhét trong 3 byte RGB nếu cả 3 byte đều là ASCII printable.
        if all(32 <= v <= 126 for v in (r, g, b)) and not (r == g == b):
            chunks.append(chr(r) + chr(g) + chr(b))

stream = "".join(chunks)

print("[+] extracted stream:")
print(stream)

m = re.search(r"tjctf\{[^}]+\}", stream)

if m:
    print("[+] flag:", m.group(0))
else:
    print("[-] flag not found")
```

Output ra được flag: 

<img width="905" height="146" alt="image" src="https://github.com/user-attachments/assets/055f6e14-a897-4661-ad2a-d38d43ea3612" />

---
# Flag
```bash
tjctf{c0ngr4ts_u_s0lv3d_my_f1st_CTF_chall!_btw_1_l1ke_b1rds}
```





