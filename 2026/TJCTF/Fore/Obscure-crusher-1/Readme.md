# Đề bài 
<img width="1035" height="281" alt="image" src="https://github.com/user-attachments/assets/93be708b-7e81-4c0a-9da0-52efbfdbdac1" />

---
Ta nhận được 1 file chall.bin, đề bài bắt ta tìm 3 cái key để làm gì đấy 

Ta test thử vài lệnh xem định dạng :

```bash
file chall.bin
```

```bash
wc chall.bin
```

Kết quả trả về : 

<img width="909" height="207" alt="Ảnh chụp màn hình 2026-05-17 215048" src="https://github.com/user-attachments/assets/1613df23-7253-4a95-9194-17735c266e16" />

Ta nhận thấy file khá nhỏ, chỉ 169 bytes, ta test thử luôn với strings:

```bash
strings -a -td chall.bin
```

Kết quả trả về : 

<img width="834" height="165" alt="image" src="https://github.com/user-attachments/assets/9eeda40f-6b4c-4c18-b0c3-8d26df69a7de" />

Ta thấy được vài chuỗi ASCII nằm rải rác
```bash
0 icns
      8 icns
     77 name
    114 lzmaKLZMA_DATA:
    148 @s+E
```

Thử soi bằng xxd để xem hex :

```bash
xxd -g 1 chall.bin
```

Kết quả trả về : 

<img width="842" height="278" alt="image" src="https://github.com/user-attachments/assets/73ee1ea7-17a1-49b7-a0e0-d53bc77436e2" />

Ta thấy được 1 vùng sau dấu 2 chấm không đọc được, có thể nó bị obfuscate hoặc mã hóa gì đấy 

Bài toán bắt ta tìm 3 keys, ta có thể liên tưởng tới phép xor và kết hợp vài dòng ascii nằm bên trên lại để xor

Ta biết flag format là tjctf{

Payload của đống rác đằng sau dấu 2 chấm là như sau :

```bash
1d 09 0d 07 67 0f
```

Ta có thể tính ngược lại được key như sau :

```bash
1d ^ 74 ('t') = 69 = i
09 ^ 6a ('j') = 63 = c
0d ^ 63 ('c') = 6e = n
07 ^ 74 ('t') = 73 = s
67 ^ 66 ('f') = 01
0f ^ 7b ('{') = 74 = t
```
như vậy có thể biết được cụm đầu là icns\x01t

Ta kết hợp 3 cụm ASCII lại trong xxd, nhờ AI viết hộ script giải xor tự động :
```bash
from pathlib import Path

data = Path("chall.bin").read_bytes()

marker = b"KLZMA_DATA:"
start = data.index(marker) + len(marker)
cipher = data[start:]

candidates = [
    b"icns\x01ttf\x02xylzma",
    b"icns\x01ttf\x02xylzmaK",
    b"icns\x01ttf\x02xylzmaKLZMA_DATA:",
]

for key in candidates:
    plain = bytes(c ^ key[i % len(key)] for i, c in enumerate(cipher))
    print(f"{key!r} => {plain!r}")
```
<img width="828" height="127" alt="image" src="https://github.com/user-attachments/assets/bf803a3c-4f8d-4097-8872-60b312947e52" />

như vậy ta được flag với key là 
```bash
icns\x01ttf\x02xylzmaK
```
---
## Flag 
```bash
tjctf{0bscur3_crush3r_1cns_ttf_lzm3}
```

















