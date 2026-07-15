# Write-up — V1T CTF 2026: Nice Try

## Thông tin thử thách

- **Tên thử thách:** Nice Try
- **Giải đấu:** V1T CTF 2026
- **Thể loại:** Forensics 
- **Artifact được cung cấp:**

```text
NTUSER.DAT
```

Đây là một Windows Registry Hive thuộc profile người dùng.

---

# 1. Phân tích ban đầu

Sau khi giải nén file thử thách, ta thu được:

- Một file Registry Hive tiêu chuẩn: `NTUSER.DAT`.
- Một file văn bản nhỏ chứa gợi ý rất cụ thể:

```text
Decrypt hidden registry slack by hashing a deleted key's FILETIME with its physical-offset-sorted CRC32 payload.
```

Tạm dịch:

> Giải mã dữ liệu ẩn trong Registry Slack bằng cách băm FILETIME của một Registry key đã bị xóa cùng với payload CRC32 được sắp xếp theo physical offset.

Đây là một thử thách Registry Forensics ở cấp độ byte.

Các công cụ thông thường như:

- Registry Explorer
- RegRipper
- RECmd
- reg.exe
- Python `winreg`

sẽ không đủ để giải toàn bộ bài này.

Lý do là thử thách yêu cầu xử lý những thành phần mà các Registry API thông thường thường bỏ qua:

- Registry key đã bị xóa.
- Free cell.
- Physical offset của cell.
- Các key không còn được tham chiếu.
- Registry slack space.
- Dữ liệu nằm ngoài `DataLength` được khai báo.
- Cấu trúc nhị phân thô của file `regf`.

Do đó, ta cần tự phân tích cấu trúc nhị phân của Registry Hive.

Dựa trên gợi ý, có thể chia hướng giải thành các giai đoạn sau:

```text
1. Carve Registry key đã bị xóa và lấy FILETIME.
2. Lấy các value của key, sắp xếp theo physical offset và khôi phục CRC32.
3. Tìm live key có tên khớp với CRC32 vừa tìm được.
4. Trích xuất Registry Slack trong value của live key.
5. Sinh keystream từ FILETIME và CRC32.
6. XOR để giải mã payload.
7. Base62 decode để thu được flag.
```

---

# 2. Kiến thức nền về cấu trúc Registry Hive

Một Registry Hive của Windows thường bắt đầu bằng signature:

```text
regf
```

Phần đầu file là Base Block, sau đó là các khối:

```text
hbin
```

Mỗi `hbin`, hay Hive Bin, chứa nhiều cell.

Các cell có thể lưu:

- Key Node.
- Value Key.
- Value List.
- Subkey List.
- Security Descriptor.
- Dữ liệu của value.
- Free space.

Một số signature quan trọng:

| Signature | Ý nghĩa |
|---|---|
| `nk` | Key Node |
| `vk` | Value Key |
| `lf` | Fast Leaf |
| `lh` | Hash Leaf |
| `li` | Index Leaf |
| `ri` | Root Index |
| `sk` | Security Key |
| `db` | Big Data |

---

## 2.1. Phân biệt allocated cell và free cell

Mỗi cell bắt đầu bằng trường kích thước 4 byte có dấu, little-endian.

Quy ước:

- Kích thước âm: cell đang được cấp phát.
- Kích thước dương: cell đang rảnh hoặc đã bị giải phóng.

Ví dụ:

```text
size < 0  -> allocated/live cell
size > 0  -> free/deleted cell
```

Kích thước thực của cell được tính bằng:

```python
abs(cell_size)
```

Vì Registry không nhất thiết xóa sạch dữ liệu khi giải phóng cell, nội dung cũ của key hoặc value vẫn có thể tồn tại trong free cell.

Đây là cơ sở để carve Registry key đã bị xóa.

---

# 3. Giai đoạn 1 — Carve Ghost Key

## 3.1. Mục tiêu

Ta cần tìm một `nk` cell đã bị xóa.

Điều kiện ban đầu:

- Cell có size dương.
- Nội dung cell bắt đầu bằng signature `nk`.
- Key không còn được tham chiếu bởi bất kỳ active subkey list nào.
- Key thực sự chứa các value liên quan đến thử thách.

Không thể chỉ search chuỗi byte:

```text
6E 6B
```

vì `nk` có thể xuất hiện ngẫu nhiên trong dữ liệu khác.

Cần kiểm tra cả cấu trúc cell và trạng thái cấp phát.

---

## 3.2. Quét các Hive Bin

Ta đọc Base Block và bắt đầu quét từ offset của Hive Bin đầu tiên.

Thông thường:

```text
Hive Bin đầu tiên bắt đầu tại file offset 0x1000
```

Mỗi Hive Bin có header bắt đầu bằng:

```text
hbin
```

Tại mỗi cell:

1. Đọc 4 byte `cell_size`.
2. Xác định allocated hoặc free.
3. Lấy kích thước tuyệt đối.
4. Kiểm tra signature ở đầu cell data.
5. Nếu là `nk`, parse Key Node.
6. Chuyển tới cell tiếp theo bằng kích thước cell.

Pseudo-code:

```python
offset = 0x1000

while offset < len(hive):
    if hive[offset:offset + 4] != b"hbin":
        break

    hbin_size = int.from_bytes(
        hive[offset + 8:offset + 12],
        "little"
    )

    cell_offset = offset + 0x20
    hbin_end = offset + hbin_size

    while cell_offset < hbin_end:
        cell_size = int.from_bytes(
            hive[cell_offset:cell_offset + 4],
            "little",
            signed=True
        )

        if cell_size == 0:
            break

        allocated = cell_size < 0
        real_size = abs(cell_size)

        cell_data = hive[
            cell_offset + 4:
            cell_offset + real_size
        ]

        if cell_data[:2] == b"nk":
            # Parse NK cell.
            pass

        cell_offset += real_size

    offset += hbin_size
```

---

## 3.3. Loại bỏ false positive bằng active subkey references

Một `nk` nằm trong free cell chưa chắc là key đã bị xóa hoàn toàn.

Để tránh false positive, ta cần xác định xem offset của `nk` đó còn được tham chiếu bởi các subkey list đang active hay không.

Các loại subkey list cần parse:

```text
lf
lh
li
ri
```

Ý nghĩa:

- `lf`: Fast Leaf.
- `lh`: Hash Leaf.
- `li`: Index Leaf.
- `ri`: Root Index trỏ tới các index list khác.

Ta xây dựng một tập hợp tất cả Registry relative offset được các active subkey list tham chiếu:

```python
referenced_nk_offsets = set()
```

Sau đó, một candidate deleted key chỉ được chấp nhận nếu:

```python
candidate_nk_offset not in referenced_nk_offsets
```

Điều này giúp xác định `nk` cell:

- Đã nằm trong free cell.
- Không còn thuộc cây Registry đang hoạt động.
- Có khả năng là dấu vết của key đã bị xóa.

---

## 3.4. Kết quả quét

Script parse Registry Hive cho kết quả:

```text
Tổng số NK cell tìm thấy: 3129
```

Trong số đó chỉ có một key đáp ứng đầy đủ điều kiện:

- Nằm trong free cell.
- Không được active subkey list tham chiếu.
- Có chứa các value.
- Có cấu trúc hợp lệ.

Ghost Key:

```text
{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}
```

File offset:

```text
0x1830b8
```

Đây là deleted key cần tìm.

---

# 4. Trích xuất FILETIME từ Ghost Key

Trong cấu trúc `nk`, trường LastWriteTime được lưu dưới dạng Windows FILETIME.

FILETIME gồm 8 byte, little-endian, biểu diễn số khoảng thời gian 100 nanosecond tính từ:

```text
1601-01-01 00:00:00 UTC
```

Trong thử thách này, ta không cần chuyển FILETIME sang ngày giờ.

Ta cần sử dụng chính xác 8 byte thô làm nguyên liệu sinh khóa.

FILETIME nằm tại offset:

```text
0x04
```

tính từ đầu phần dữ liệu của `nk` cell, tức là sau trường cell size.

FILETIME thô trích xuất được:

```text
80 ac bf ef b1 94 db 01
```

Viết liền:

```text
80acbfefb194db01
```

### Kết quả giai đoạn 1

```text
Ghost Key:
{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}

Ghost Key offset:
0x1830b8

FILETIME raw:
80acbfefb194db01
```

Cần giữ nguyên thứ tự byte little-endian trong file:

```python
filetime_raw = bytes.fromhex(
    "80acbfefb194db01"
)
```

Không nên chuyển sang timestamp rồi encode lại, vì điều đó có thể làm thay đổi byte order hoặc representation cần thiết cho quá trình giải mã.

---

# 5. Giai đoạn 2 — Sắp xếp Value theo Physical Offset

## 5.1. Value List của Ghost Key

`nk` cell chứa các trường liên quan đến value:

- Số lượng value.
- Relative offset tới Value List.

Value List là một cell chứa mảng các relative offset trỏ tới các `vk` cell.

Ghost Key có tổng cộng:

```text
4 values
```

Nếu đọc theo đúng thứ tự các offset xuất hiện trong Value List, ta có:

```text
0x183020
0x183080
0x183040
0x183060
```

Viết thành mảng:

```text
Value-list order:
[0x183020, 0x183080, 0x183040, 0x183060]
```

Nếu trích xuất dữ liệu theo thứ tự này, chuỗi thu được không có ý nghĩa.

---

## 5.2. Ý nghĩa của gợi ý physical-offset-sorted

Gợi ý có đoạn:

```text
physical-offset-sorted CRC32 payload
```

Điều này có nghĩa là không sử dụng logical order trong Value List.

Thay vào đó, phải sắp xếp các `vk` cell theo vị trí vật lý của chúng trong file Registry Hive.

Thứ tự vật lý tăng dần:

```text
0x183020
0x183040
0x183060
0x183080
```

Viết thành mảng:

```text
Physical order:
[0x183020, 0x183040, 0x183060, 0x183080]
```

Sự khác biệt:

```text
Value-list order:
0x183020 -> 0x183080 -> 0x183040 -> 0x183060

Physical order:
0x183020 -> 0x183040 -> 0x183060 -> 0x183080
```

---

## 5.3. Relative offset và physical file offset

Trong Registry Hive, nhiều offset được lưu dưới dạng relative offset tính từ Hive Bin area.

Nếu Hive Bin area bắt đầu tại file offset:

```text
0x1000
```

thì có thể chuyển relative offset sang absolute file offset bằng:

```python
absolute_offset = relative_offset + 0x1000
```

Tuy nhiên, cần kiểm tra cách script đang biểu diễn offset.

Trong write-up này, các giá trị:

```text
0x183020
0x183040
0x183060
0x183080
```

đã được biểu diễn dưới dạng physical file offset.

Không nên cộng thêm `0x1000` lần nữa.

---

## 5.4. Khôi phục chuỗi CRC32

Sau khi:

1. Lấy bốn value cell.
2. Sắp xếp chúng theo physical offset tăng dần.
3. Trích xuất data chunk tương ứng.
4. Ghép các chunk lại.

Ta thu được một chuỗi dài 8 ký tự:

```text
d03e17cb
```

Đây là chuỗi hexadecimal biểu diễn CRC32.

### Target CRC32

```text
d03e17cb
```

Chuỗi này không phải kết quả tính CRC32 của payload ghost key.

Nó là một payload được giấu trong bốn value, dùng làm mục tiêu để tìm key tiếp theo.

### Kết quả giai đoạn 2

```text
Physical offset order:
0x183020
0x183040
0x183060
0x183080

Recovered CRC32 string:
d03e17cb
```

---

# 6. Giai đoạn 3 — Tìm Live Key khớp CRC32

## 6.1. Ý tưởng

Ta đã có chuỗi:

```text
d03e17cb
```

Bước tiếp theo là quét toàn bộ allocated/live key trong Registry Hive.

Với mỗi key:

1. Lấy tên key.
2. Encode tên key thành đúng byte representation.
3. Tính CRC32.
4. Chuyển kết quả thành chuỗi hexadecimal 8 ký tự.
5. So sánh với `d03e17cb`.

Ví dụ Python:

```python
import zlib

name = "{EXAMPLE-KEY-NAME}"

crc = zlib.crc32(name.encode()) & 0xffffffff
crc_string = f"{crc:08x}"

print(crc_string)
```

Cần chú ý các yếu tố:

- Encoding của tên key.
- Có phân biệt chữ hoa và chữ thường.
- Có giữ nguyên `{}` và dấu `-`.
- Không thêm ký tự xuống dòng.
- CRC32 phải được giới hạn trong 32 bit.

Công thức:

```python
crc = zlib.crc32(data) & 0xffffffff
```

Format thành 8 ký tự hex:

```python
f"{crc:08x}"
```

---

## 6.2. Kết quả quét

Sau khi kiểm tra:

```text
3124 live keys
```

ta tìm được một key có CRC32 tên khớp với:

```text
d03e17cb
```

Matched Key:

```text
{4F384589-C0C4-4470-8C3D-AABC1F1B8B14}
```

Offset:

```text
0x183210
```

### Kiểm chứng

```text
CRC32("{4F384589-C0C4-4470-8C3D-AABC1F1B8B14}")
= d03e17cb
```

Đây là live key chứa payload ẩn trong Registry Slack.

---

# 7. Phân tích Registry Slack Space

## 7.1. Các value trong Matched Key

Bên trong key:

```text
{4F384589-C0C4-4470-8C3D-AABC1F1B8B14}
```

có hai value:

```text
Config
Cfg
```

Value cần quan tâm là:

```text
Cfg
```

Khi parse `Cfg`, ta thấy:

```text
Declared DataLength: 12 bytes
Physical Cell Capacity: 124 bytes
```

Điều này có nghĩa value chỉ khai báo 12 byte dữ liệu hợp lệ, nhưng cell vật lý có thể chứa tới 124 byte dữ liệu trong vùng liên quan.

Phần còn dư:

```text
124 - 12 = 112 bytes
```

Đây là Registry Slack.

---

## 7.2. Registry Slack là gì?

Registry Slack là vùng byte còn thừa trong một cell đã được cấp phát.

Ví dụ:

```text
Cell capacity: 124 byte
Declared data: 12 byte
Slack space  : 112 byte
```

Các Registry parser thông thường chỉ đọc đúng số byte được khai báo trong `DataLength`.

Phần byte còn lại thường bị bỏ qua.

Tuy nhiên, slack có thể chứa:

- Dữ liệu cũ.
- Dữ liệu đã bị ghi đè một phần.
- Payload bị ẩn có chủ đích.
- Fragment từ value trước đó.
- Dữ liệu chống phân tích.

Trong bài này, tác giả chủ động đặt ciphertext vào vùng Registry Slack.

---

## 7.3. Trích xuất Slack

Cần xác định:

- Vị trí bắt đầu của data.
- `DataLength` khai báo.
- Kích thước cell thực tế.
- Header và metadata của cell.
- Vùng dữ liệu hợp lệ.
- Phần slack còn lại.

Không được đơn giản lấy:

```python
cell[data_length:]
```

nếu chưa trừ đúng kích thước header.

Cần tính offset dựa trên cấu trúc thật của `vk` và data cell.

Sau khi trích xuất đúng phần slack, ta thu được 112 byte:

```text
fffd57fcb1e89478ea709d63b2672ba7215ba9d14a5ec24caa14cdb240e68896ce7b5e9a429bebeb292966e087bf5e733abafb0fb8a6e9365c0160ef24f5fcd423005a282de8fb28f1037912650b4f1839f31771c3388b22df2085ae10183890f73af4fdf9922ed2c534000000000000
```

Đây là encrypted payload.

### Thông tin value `Cfg`

```text
Declared DataLength:
12 bytes

Physical capacity:
124 bytes

Slack length:
112 bytes
```

### Ciphertext trong Registry Slack

```text
fffd57fcb1e89478ea709d63b2672ba7215ba9d14a5ec24caa14cdb240e68896ce7b5e9a429bebeb292966e087bf5e733abafb0fb8a6e9365c0160ef24f5fcd423005a282de8fb28f1037912650b4f1839f31771c3388b22df2085ae10183890f73af4fdf9922ed2c534000000000000
```

Phần cuối có các byte `00` padding:

```text
000000000000
```

Các byte này có thể được giữ nguyên trong quá trình XOR rồi loại bỏ bằng:

```python
rstrip(b"\x00")
```

sau khi giải mã, tùy cấu trúc plaintext.

---

# 8. Giai đoạn 4 — Giải mã Registry Slack

## 8.1. Xây dựng BaseKey

Gợi ý nói:

```text
hashing a deleted key's FILETIME with its physical-offset-sorted CRC32 payload
```

Ta cần kết hợp:

1. FILETIME thô của deleted key.
2. Chuỗi ASCII CRC32 đã khôi phục.

FILETIME:

```text
80 ac bf ef b1 94 db 01
```

CRC32 dưới dạng ASCII:

```text
d03e17cb
```

Cần phân biệt hai representation:

### Dạng ASCII đúng

```python
b"d03e17cb"
```

Byte tương ứng:

```text
64 30 33 65 31 37 63 62
```

### Dạng hexadecimal khác

```python
bytes.fromhex("d03e17cb")
```

Byte tương ứng:

```text
d0 3e 17 cb
```

Theo write-up và gợi ý, phải sử dụng **chuỗi ASCII**:

```python
crc_payload = b"d03e17cb"
```

BaseKey:

```python
base_key = filetime_raw + crc_payload
```

Tức là:

```text
80 ac bf ef b1 94 db 01
64 30 33 65 31 37 63 62
```

Viết liền:

```text
80acbfefb194db016430336531376362
```

---

## 8.2. Sinh keystream bằng SHA-256 và counter

Keystream được tạo bằng cách hash:

```text
BaseKey || Counter
```

Trong đó counter là số nguyên 4 byte little-endian.

Block đầu tiên:

```text
SHA256(BaseKey + Counter_0)
```

Block tiếp theo:

```text
SHA256(BaseKey + Counter_1)
```

Sau đó:

```text
SHA256(BaseKey + Counter_2)
SHA256(BaseKey + Counter_3)
...
```

Ghép tất cả digest:

```text
Stream =
SHA256(BaseKey || LE32(0))
||
SHA256(BaseKey || LE32(1))
||
SHA256(BaseKey || LE32(2))
||
...
```

Mỗi SHA-256 digest tạo ra:

```text
32 bytes
```

Ta sinh đủ số block để keystream dài ít nhất bằng ciphertext.

Với ciphertext 112 byte:

```text
ceil(112 / 32) = 4 blocks
```

Tổng keystream sinh ra:

```text
4 × 32 = 128 bytes
```

Sau đó chỉ lấy 112 byte đầu.

---

## 8.3. Counter little-endian

Counter phải được encode thành 4 byte little-endian:

```python
counter.to_bytes(
    4,
    byteorder="little"
)
```

Ví dụ:

```text
Counter 0 -> 00 00 00 00
Counter 1 -> 01 00 00 00
Counter 2 -> 02 00 00 00
Counter 3 -> 03 00 00 00
```

Không dùng big-endian:

```text
00 00 00 01
```

vì sẽ tạo ra keystream khác hoàn toàn.

---

## 8.4. XOR ciphertext với keystream

Sau khi có keystream:

```python
plaintext = bytes(
    encrypted_byte ^ stream_byte
    for encrypted_byte, stream_byte
    in zip(ciphertext, keystream)
)
```

Payload sau khi giải mã:

```text
if-you-are-not-human-so-this-is-not-the-flag-bl6qcYi3SDxUmgiRxMTQBwJFq4QcZCTsY9x7YXL2YBNbecvxDinTkXnJKzXVV
```

Chuỗi này có hai phần:

```text
if-you-are-not-human-so-this-is-not-the-flag-
```

và:

```text
bl6qcYi3SDxUmgiRxMTQBwJFq4QcZCTsY9x7YXL2YBNbecvxDinTkXnJKzXVV
```

Phần đầu là thông báo hoặc decoy text.

Phần sau là dữ liệu Base62 cần decode.

---

# 9. Script giải mã Registry Slack

```python
import hashlib


FILETIME_RAW = bytes.fromhex(
    "80acbfefb194db01"
)

CRC32_PAYLOAD = b"d03e17cb"

ENCRYPTED_SLACK = bytes.fromhex(
    "fffd57fcb1e89478ea709d63b2672ba7"
    "215ba9d14a5ec24caa14cdb240e68896"
    "ce7b5e9a429bebeb292966e087bf5e73"
    "3abafb0fb8a6e9365c0160ef24f5fcd4"
    "23005a282de8fb28f1037912650b4f18"
    "39f31771c3388b22df2085ae10183890"
    "f73af4fdf9922ed2c534000000000000"
)


def generate_keystream(
    base_key: bytes,
    required_length: int
) -> bytes:
    """
    Sinh keystream bằng:
    SHA256(BaseKey || Counter_LE32)
    """

    stream = bytearray()
    counter = 0

    while len(stream) < required_length:
        counter_bytes = counter.to_bytes(
            4,
            byteorder="little",
            signed=False
        )

        digest = hashlib.sha256(
            base_key + counter_bytes
        ).digest()

        stream.extend(digest)
        counter += 1

    return bytes(stream[:required_length])


def xor_bytes(
    data: bytes,
    key_stream: bytes
) -> bytes:
    """
    XOR từng byte của ciphertext với keystream.
    """

    return bytes(
        data_byte ^ key_byte
        for data_byte, key_byte
        in zip(data, key_stream)
    )


base_key = FILETIME_RAW + CRC32_PAYLOAD

key_stream = generate_keystream(
    base_key,
    len(ENCRYPTED_SLACK)
)

decrypted = xor_bytes(
    ENCRYPTED_SLACK,
    key_stream
)

# Loại bỏ null padding ở cuối nếu có.
decrypted = decrypted.rstrip(b"\x00")

print("[+] Base key:", base_key.hex())
print("[+] Decrypted bytes:", decrypted)
print(
    "[+] Decrypted text:",
    decrypted.decode("utf-8")
)
```

Kết quả:

```text
if-you-are-not-human-so-this-is-not-the-flag-bl6qcYi3SDxUmgiRxMTQBwJFq4QcZCTsY9x7YXL2YBNbecvxDinTkXnJKzXVV
```

---

# 10. Base62 Decode

## 10.1. Xác định chuỗi Base62

Phần cần decode:

```text
bl6qcYi3SDxUmgiRxMTQBwJFq4QcZCTsY9x7YXL2YBNbecvxDinTkXnJKzXVV
```

Alphabet Base62 được thử thách sử dụng:

```text
abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789
```

Thứ tự alphabet rất quan trọng.

Alphabet này khác với một số implementation Base62 phổ biến sử dụng:

```text
0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
```

Nếu dùng sai alphabet, dữ liệu decode sẽ khác hoàn toàn.

---

## 10.2. Nguyên lý Base62 Decode

Mỗi ký tự được ánh xạ thành một số từ 0 đến 61.

Với alphabet:

```text
abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789
```

ta có:

```text
a = 0
b = 1
...
z = 25
A = 26
...
Z = 51
0 = 52
...
9 = 61
```

Chuỗi Base62 được coi như một số nguyên trong hệ cơ số 62:

```python
number = number * 62 + alphabet.index(character)
```

Sau khi thu được số nguyên lớn, chuyển số đó sang byte theo big-endian:

```python
number.to_bytes(
    (number.bit_length() + 7) // 8,
    "big"
)
```

---

## 10.3. Script Base62 Decode

```python
def base62_decode(
    encoded: str,
    alphabet: str = (
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
    )
) -> bytes:
    """
    Chuyển chuỗi Base62 thành byte.
    """

    number = 0

    for character in encoded:
        if character not in alphabet:
            raise ValueError(
                f"Ký tự không hợp lệ trong Base62: "
                f"{character!r}"
            )

        number = (
            number * 62
            + alphabet.index(character)
        )

    byte_length = (
        number.bit_length() + 7
    ) // 8

    return number.to_bytes(
        byte_length,
        byteorder="big"
    )


encoded_flag = (
    "bl6qcYi3SDxUmgiRxMTQBwJFq4QcZCTs"
    "Y9x7YXL2YBNbecvxDinTkXnJKzXVV"
)

decoded = base62_decode(encoded_flag)

print("[+] Base62 decoded bytes:", decoded)
print(
    "[+] Base62 decoded text:",
    decoded.decode("utf-8")
)
```

Kết quả:

```text
-payload-V1T{f4r3_w3ll_buddy}-write-a-trojan-
```

---

# 11. Trích xuất flag

Plaintext sau Base62 decode:

```text
-payload-V1T{f4r3_w3ll_buddy}-write-a-trojan-
```
## Flag :
```text
V1T{f4r3_w3ll_buddy}
```
