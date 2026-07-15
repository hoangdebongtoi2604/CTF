# Colonel — Writeup

## TL;DR

Khôi phục khóa AES-256 từ một bản dump bộ nhớ Linux bằng cách tìm hai lần xác thực thất bại của một kernel module (`check_service.ko`), trong đó mỗi lần có các byte sai khác nhau. Kết hợp các byte đúng từ cả hai lần thử giúp tái tạo đầy đủ khóa và giải mã được flag.

**Tóm tắt một dòng:** `strings memory.dump | grep "Invalid key"` cho thấy hai khóa chưa hoàn chỉnh với các vị trí lỗi bù trừ cho nhau; ghép chúng lại sẽ thu được khóa AES dùng để giải mã `flag.enc`.

## Thông tin Challenge

| Trường | Giá trị |
|---|---|
| Tên | Colonel |
| Thể loại | Forensics |
| Tác giả | Archan6el |
| Định dạng Flag | `gigem{...}` |

## Mô tả Challenge

> Một Đại tá Quân đội đang gặp khó khăn khi giải mã một tệp nhạy cảm. Ông nhớ rằng tệp được mã hóa bằng AES-CBC với IV là `1234567890123456`, nhưng hoàn toàn không thể nhớ khóa đã sử dụng. Ông đã chụp lại một bản dump bộ nhớ trong lúc cố gắng giải mã tệp. Có lẽ bạn có thể tìm thấy thứ gì đó trong đó?

## Quan sát ban đầu / Dấu hiệu đáng chú ý

- Tên challenge `"Colonel"` là một cách chơi chữ với `"kernel"`, gợi ý rằng challenge có liên quan đến Linux kernel.
- Challenge cung cấp một bản dump bộ nhớ và một tệp được mã hóa bằng AES-CBC với IV đã biết nhưng chưa biết khóa.
- Bản dump bộ nhớ là một tệp core ELF 64-bit, dung lượng khoảng 2,7 GB, lấy từ một máy ảo Ubuntu 24.04 chạy kernel `6.17.0-14-generic` trên VirtualBox.
- Tệp flag đã mã hóa (`flag.enc`) có kích thước chính xác 48 byte, tương đương 3 block AES, cho thấy plaintext khá ngắn và có padding.

## Phương pháp thực hiện chi tiết

### Bước 1: Phân tích ban đầu

**Mục tiêu:** Xác định loại tệp và các tham số của challenge.

```bash
file memory.dump
# memory.dump: ELF 64-bit LSB core file, x86-64, version 1 (SYSV)

xxd flag.enc
# 48 bytes of ciphertext
```

**Kết luận:** Đây là một bản dump bộ nhớ Linux tiêu chuẩn cùng với một tệp mã hóa nhỏ. Khóa phải được khôi phục từ bộ nhớ.

### Bước 2: Tìm kiếm AES Key Schedule — Ngõ cụt

**Mục tiêu:** Thử các công cụ tự động khôi phục khóa AES.

```bash
aeskeyfind memory.dump
# Không tìm thấy khóa

bulk_extractor -E aes -o be_output memory.dump
# Tìm thấy các AES-256 key schedule
```

**Kết quả:** `bulk_extractor` tìm thấy một số AES-256 expanded key schedule, nhưng không có khóa nào giải mã thành công flag.

**Kết luận:** Khóa không được lưu trong bộ nhớ dưới dạng AES expanded key schedule. Nó phải được lưu dưới dạng chuỗi thô hoặc passphrase.

### Bước 3: Phát hiện lịch sử terminal

**Mục tiêu:** Tìm hiểu người dùng đã thực hiện những thao tác gì trên hệ thống.

```bash
strings memory.dump | grep "ubuntu@ubuntuvm"
```

**Kết quả:** Tìm thấy lịch sử phiên terminal:

```text
ubuntu@ubuntuvm:~$ cd validate/
ubuntu@ubuntuvm:~/validate$ sudo insmod check_service.ko key_path=validation
ubuntu@ubuntuvm:~/validate$ sudo rmmod check_service
ubuntu@ubuntuvm:~/validate$ sudo insmod check_service.ko key_path=validation2
```

**Kết luận:** Một kernel module có tên `check_service.ko` đã được nạp với hai tệp khóa khác nhau là `validation` và `validation2`. Cách chơi chữ `"Colonel"` = `"kernel"` xác nhận rằng challenge xoay quanh kernel module này.

### Bước 4: Phân tích Kernel Module

**Mục tiêu:** Hiểu chức năng của `check_service.ko`.

Module được tìm thấy trong bộ nhớ bằng cách tìm chuỗi modinfo `parm=key_path`, sau đó trích xuất các chuỗi bên trong:

```text
"Reading from %s"
"Success: key correct!"
"Error: failed to open key file (%ld)"
"Error: Invalid key length (%zd), expected %d bytes"
"Error: Invalid key %*phN, indices %sincorrect"
parm=key_path:Path to key file
```

**Kết luận:** Module đọc khóa từ một tệp, kiểm tra từng byte của khóa và thông báo các chỉ số byte không chính xác.

### Bước 5: Trích xuất kết quả xác thực từ dmesg

**Mục tiêu:** Tìm output của module trong cả hai lần xác thực.

```bash
strings memory.dump | grep -E "Invalid key|Reading from|indices"
```

**Kết quả:**

```text
Reading from validation
Error: Invalid key 51782b4b765251314e32525236364978534d35566a6b72474b67303946483266, indices 9 21 31 incorrect
Reading from validation2
Error: Invalid key 58782b4b765251314e51525235364978534d35566a6a72524b673039466c3265, indices 0 12 23 29 incorrect
```

Các chuỗi hex khi được chuyển sang ASCII:

- `validation`: `Qx+KvRQ1N2RR66IxSM5VjkrGKg09FH2f` — sai tại các chỉ số `9`, `21`, `31`
- `validation2`: `Xx+KvRQ1NQRR56IxSM5VjjrRKg09Fl2e` — sai tại các chỉ số `0`, `12`, `23`, `29`

**Kết luận:** Mỗi tệp khóa chỉ có một vài byte sai tại các vị trí khác nhau. Hai tập vị trí lỗi không trùng nhau, vì vậy có thể kết hợp các byte đúng từ cả hai khóa để thu được khóa đầy đủ.

### Bước 6: Tái tạo khóa và giải mã

**Mục tiêu:** Ghép hai khóa chưa hoàn chỉnh và giải mã flag.

Với mỗi vị trí trong khóa:

- Nếu chỉ số thuộc `{9, 21, 31}`, nghĩa là khóa thứ nhất sai, sử dụng byte từ khóa thứ hai.
- Nếu chỉ số thuộc `{0, 12, 23, 29}`, nghĩa là khóa thứ hai sai, sử dụng byte từ khóa thứ nhất.
- Với các vị trí còn lại, cả hai khóa giống nhau nên có thể sử dụng byte từ khóa nào cũng được.

Khóa được tái tạo:

```text
Qx+KvRQ1NQRR66IxSM5VjjrGKg09FH2e
```
Script giải mã : 
```bash
#!/usr/bin/env python3
"""Solver for Colonel (Forensics) - TamuCTF 2026"""

from Crypto.Cipher import AES

# Step 1: Define the two validation keys and their incorrect indices
# Found by: strings memory.dump | grep "Invalid key"
# validation:  indices 9, 21, 31 incorrect
key1 = "Qx+KvRQ1N2RR66IxSM5VjkrGKg09FH2f"
bad1 = {9, 21, 31}

# validation2: indices 0, 12, 23, 29 incorrect
key2 = "Xx+KvRQ1NQRR56IxSM5VjjrRKg09Fl2e"
bad2 = {0, 12, 23, 29}

# Step 2: Reconstruct the correct key by taking correct bytes from each
correct_key = []
for i in range(32):
    if i in bad1:
        correct_key.append(key2[i])  # key1 wrong here, use key2
    elif i in bad2:
        correct_key.append(key1[i])  # key2 wrong here, use key1
    else:
        assert key1[i] == key2[i], f"Mismatch at index {i}: {key1[i]} vs {key2[i]}"
        correct_key.append(key1[i])
correct_key = ''.join(correct_key)
print(f"AES key: {correct_key}")

# Step 3: Decrypt flag.enc with AES-256-CBC
iv = b'1234567890123456'
key = correct_key.encode('ascii')

with open("flag.enc", "rb") as f:
    ct = f.read()

cipher = AES.new(key, AES.MODE_CBC, iv)
pt = cipher.decrypt(ct)

# Step 4: Strip null padding and print flag
flag = pt.rstrip(b'\x00').decode('ascii')
print(f"Flag: {flag}")
```

Chạy script giải mã:

```bash
python3 solve.py
```
## Flag: 
```bash
gigem{bl3ss3d_4r3_th3_c010n31_m33k}
```
