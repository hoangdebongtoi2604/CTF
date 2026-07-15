# Write-up — V1T CTF 2026: Polar Fragment

## Flag cuối cùng

```text
V1t{d0_y0u_7h1nk_1c3_b34r_15_cu73?}
```

---

# 1. Kiểm tra gói thử thách ban đầu

Sau khi giải nén file `challenge.zip`, ta thu được các file chính sau:

```text
challenge.E01
locked.zip
pcap1.pcapng
pcap2.pcapng
pcap3.pcapng
pcap4.pcapng
pcap5.pcapng
```

Trong đó:

- `challenge.E01` là ảnh đĩa theo định dạng EnCase.
- `locked.zip` là file ZIP bị khóa bằng mật khẩu.
- `pcap1.pcapng` đến `pcap5.pcapng` là các file bắt lưu lượng mạng.

Mặc dù các file mạng có phần mở rộng `.pcapng`, bốn byte đầu của chúng lại là:

```text
d4 c3 b2 a1
```

Đây là magic bytes của định dạng **PCAP little-endian cổ điển**, không phải PCAPNG thực sự.

Vì vậy, nếu Wireshark hoặc một công cụ khác báo lỗi liên quan đến PCAPNG, không nên vội kết luận file bị hỏng. Hãy thử đọc chúng như file PCAP thông thường.

Có thể kiểm tra magic bytes và loại file bằng câu lệnh:

```bash
for f in pcap*.pcapng; do
    echo "[*] $f"
    xxd -g 1 -l 4 "$f"
    file "$f"
done
```

---

# 2. Phân tích ảnh đĩa E01

## 2.1. Triage ảnh đĩa dựa trên các dấu mốc nội bộ

Ảnh đĩa chứa rất nhiều file nền và dữ liệu không liên quan.

Cách giải đúng không phải là duyệt ngẫu nhiên toàn bộ hệ thống file, mà là lần theo những dấu mốc được cài sẵn trong ảnh đĩa, bao gồm:

- Ghi chú của Bob.
- Nhật ký của công cụ StegAnalyzer.
- Thùng rác `$RECYCLE.BIN`.
- Các file backup đã bị xóa.

Các artifact quan trọng:

| Artifact | Vai trò trong quá trình giải |
|---|---|
| `Users/Bob/Desktop/flag.txt` | Flag giả. Dùng để xác định format `V1t{...}`, nhưng nội dung tự khẳng định đây không phải flag thật |
| `Users/Bob/Desktop/investigation_notes.txt` | Dấu mốc điều tra, nhắc đến `$RECYCLE.BIN`, `photo_009.png`, FTP log và các file PCAP |
| `Program Files/StegAnalyzer/scan_history.log` | Ghi nhận `photo_009.png` là file đáng ngờ, có khả năng chứa dữ liệu LSB |
| `$RECYCLE.BIN/.../system_backup_nov.zip` | File backup thật cần trích xuất; bên trong có `backup/photo_009.png` và `backup/large.zip` |
| `$RECYCLE.BIN/.../large.zip` | File ZIP có header bị phá hỏng, cần sửa lại dựa trên signature chuẩn của ZIP |

Tuy nhiên, chính nội dung của nó nói rằng đây không phải flag thật:

```text
th1s_1s_n0t_th3_fl4g_k33p_l00k1ng
```

Do đó, ta chỉ sử dụng nó để xác định format, không sử dụng làm kết quả cuối cùng.

---

## 2.2. Khôi phục mật khẩu của `large.zip` từ `photo_009.png`

Sau khi trích xuất `system_backup_nov.zip`, ta thu được:

```text
backup/photo_009.png
backup/large.zip
```

Khi kiểm tra `photo_009.png`, ta tìm thấy marker sau tại offset:

```text
0x36181d
```

Marker đầy đủ:

```text
ASCII-aGFoYV84Mzg2
```

Tiền tố:

```text
ASCII-
```

là một dấu hiệu cho biết dữ liệu đứng sau được lưu dưới dạng văn bản an toàn, không phải các byte ngẫu nhiên.

Phần dữ liệu cần xử lý là:

```text
aGFoYV84Mzg2
```

Giải mã Base64:

```text
aGFoYV84Mzg2
        ↓
haha_8386
```

Có thể thực hiện bằng câu lệnh:

```bash
echo 'aGFoYV84Mzg2' | base64 -d
```

Kết quả:

```text
haha_8386
```

Đây là mật khẩu của `large.zip`.

---

## 2.3. Sửa `large.zip` bằng signature chuẩn của ZIP

File `large.zip` có hai signature quan trọng đã bị phá hỏng:

1. Local File Header.
2. End of Central Directory, viết tắt là EOCD.

Theo định dạng ZIP chuẩn, Local File Header phải bắt đầu bằng:

```text
50 4B 03 04
```

EOCD phải bắt đầu bằng:

```text
50 4B 05 06
```

Trong file bị hỏng, các giá trị hiện tại là:

```text
Local header trước khi sửa: 11 11 11 11
Local header sau khi sửa : 50 4B 03 04

EOCD trước khi sửa        : 00 00 00 00
EOCD sau khi sửa          : 50 4B 05 06
```

Có thể mở file bằng hex editor như:

- `hexedit`
- `bless`
- `HxD`
- `010 Editor`

Sau đó thay các byte bị hỏng bằng signature chuẩn.

Sau khi sửa xong, mở `large.zip` bằng mật khẩu:

```text
haha_8386
```

Ta thu được:

```text
README.txt
small.zip
```

Nội dung quan trọng của `README.txt`:

```text
Look carefully at all the images...
One of them is hiding something.
Chloe is our best friend and the house is where we met.
```

Tạm dịch:

```text
Hãy kiểm tra cẩn thận tất cả các bức ảnh...
Một trong số chúng đang che giấu thứ gì đó.
Chloe là người bạn thân nhất của chúng ta và căn nhà là nơi chúng ta gặp nhau.
```

Dòng đầu tiên yêu cầu kiểm tra **tất cả các ảnh**.

Vì vậy, hướng giải đúng là chạy OpenStego trên toàn bộ ảnh, (tại vì anh long đã chạy và nó ra, mình vẫn đéo hiểu tại sao :v) trong `small.zip`, không chỉ kiểm tra riêng `chloe.png`.

---

## 2.4. Phân tích các ảnh trong `small.zip` bằng OpenStego

File `small.zip` chứa sáu ảnh:

```text
panda.png
nomnom.png
house.png
icy.png
chloe.png
grizzly.png
```

Ta sử dụng OpenStego phiên bản `0.8.6` để thử trích xuất dữ liệu từ tất cả các ảnh.

Phiên bản được sử dụng trong write-up gốc:

```text
OpenStego 0.8.6
```

Nếu phiên bản này phát sinh lỗi, có thể thử một phiên bản khác.

Ví dụ chạy OpenStego bằng Java:

```bash
java -jar openstego.jar extract \
    -sf icy.png \
    -xd output_icy
```

Có thể lặp lại với toàn bộ ảnh:

```bash
for img in *.png; do
    mkdir -p "output_${img%.png}"

    java -jar openstego.jar extract \
        -sf "$img" \
        -xd "output_${img%.png}"
done
```

---

### 2.4.1. `icy.png` — Fragment mở đầu thật

Khi trích xuất `icy.png`, OpenStego tạo ra file:

```text
flag.txt
```

Nội dung:

```text
V1t{d0_
```

Đây là phần mở đầu thật của flag.

### Fragment từ `icy.png`

```text
V1t{d0_
```

---

### 2.4.2. `house.png` — Gợi ý sử dụng XOR

`house.png` không trực tiếp chứa fragment cuối cùng.

Thay vào đó, nó chứa một gợi ý:

```text
XOR
```

Vai trò của ảnh này là xác định chính xác phép biến đổi cần sử dụng cho payload tiếp theo.

Điều này giúp ta tránh việc thử ngẫu nhiên các phương pháp như:

- Caesar cipher.
- Base64.
- ROT13.
- ROT47.
- Vigenère.
- Các phép dịch byte khác.

Artifact này chỉ rõ rằng dữ liệu tiếp theo phải được xử lý bằng phép XOR.

---

### 2.4.3. `chloe.png` — Trích xuất `key.txt` và giải XOR một byte

Khi trích xuất `chloe.png`, ta thu được file:

```text
key.txt
```

Nội dung:

```text
z3v\4k2mh\
```

Do `house.png` đã cho biết cần sử dụng XOR, nhiệm vụ tiếp theo là xác định XOR key.

#### Lý do chọn key `0x03`

Payload thô chứa hai ký tự `\` tại các vị trí có vẻ là dấu phân cách:

```text
z3v\4k2mh\
```

Trong các fragment của thử thách, ký tự phân cách thường là dấu gạch dưới:

```text
_
```

Ta có thể sử dụng known-plaintext để tính key.

Mã ASCII của `\`:

```text
\ = 0x5c
```

Mã ASCII của `_`:

```text
_ = 0x5f
```

XOR hai giá trị:

```text
0x5c ^ 0x5f = 0x03
```

Do đó, XOR key là:

```text
0x03
```

Áp dụng XOR `0x03` cho toàn bộ nội dung `key.txt`:

```text
z ^ 0x03 = y
3 ^ 0x03 = 0
v ^ 0x03 = u
\ ^ 0x03 = _
4 ^ 0x03 = 7
k ^ 0x03 = h
2 ^ 0x03 = 1
m ^ 0x03 = n
h ^ 0x03 = k
\ ^ 0x03 = _
```

Kết quả:

```text
y0u_7h1nk_
```

### Fragment từ `chloe.png`

```text
y0u_7h1nk_
```

Có thể kiểm chứng bằng cách brute-force toàn bộ key XOR một byte từ `0x00` đến `0xff`:

```python
raw = b"z3v\\4k2mh\\"

charset = set(
    b"abcdefghijklmnopqrstuvwxyz"
    b"0123456789_{}?"
)

for key in range(256):
    output = bytes(byte ^ key for byte in raw)

    if all(byte in charset for byte in output):
        print(hex(key), output)
```

Kết quả có ý nghĩa:

```text
0x3 b'y0u_7h1nk_'
```

Brute-force ở đây chỉ đóng vai trò kiểm chứng.

Key `0x03` vẫn được suy ra có căn cứ từ:

- Gợi ý XOR trong `house.png`.
- Cặp known-plaintext `\` và `_`.

---

## Kết luận phần E01

Các fragment thu được từ ảnh đĩa:

```text
icy.png   -> V1t{d0_
house.png -> Gợi ý XOR
chloe.png -> y0u_7h1nk_
```

Ghép lại:

```text
V1t{d0_y0u_7h1nk_
```

---

# 3. Phân tích `pcap5` — Khôi phục mật khẩu của `locked.zip`

`pcap5` đóng vai trò là cánh cổng để truy cập dữ liệu trong bốn file PCAP còn lại.

Capture này chứa rất nhiều request HTTP giả tới endpoint:

```text
/data/stream
```

Không thể lấy body của các request rồi ghép theo thứ tự frame toàn cục.

Các request phải được:

1. Nhóm theo từng network flow.
2. Sắp xếp theo header `X-Frame-Index`.
3. Ghép lại thành bitstream.
4. Chuyển bitstream sang ASCII.
5. Kiểm chứng bằng cách mở `locked.zip`.

Các nhóm đáng chú ý:

| Endpoint | Khoảng frame và số lượng | Kết quả kiểm tra |
|---|---:|---|
| `10.0.0.5 -> 10.10.10.50:9091` | `251–445`, 48 byte hex | Dữ liệu nhiễu |
| `172.16.0.5 -> 10.10.10.50:9090` | `96134–96489`, 72 bit | ASCII `hihi_6969` |
| `10.0.0.5 -> 10.10.10.50:9090` | `192143–192259`, 30 bit | Dữ liệu nhiễu |

Bitstream đúng:

```text
01101000
01101001
01101000
01101001
01011111
00110110
00111001
00110110
00111001
```

Ghép lại:

```text
011010000110100101101000011010010101111100110110001110010011011000111001
```

Chuyển từng nhóm 8 bit sang ASCII:

| Binary | Hex | ASCII |
|---|---:|---|
| `01101000` | `68` | `h` |
| `01101001` | `69` | `i` |
| `01101000` | `68` | `h` |
| `01101001` | `69` | `i` |
| `01011111` | `5f` | `_` |
| `00110110` | `36` | `6` |
| `00111001` | `39` | `9` |
| `00110110` | `36` | `6` |
| `00111001` | `39` | `9` |

Kết quả:

```text
hihi_6969
```

Đây là mật khẩu của:

```text
locked.zip
```

Ta kiểm chứng bằng cách mở file:

```bash
unzip -P 'hihi_6969' locked.zip
```

Bên trong `locked.zip`, file `hint.txt` xác nhận rằng dữ liệu ẩn còn lại nằm trong:

```text
pcap1
pcap2
pcap3
pcap4
```

---

# 4. Phân tích `pcap1` — HTTP POST chứa ảnh PNG mã hóa Base64

Mục tiêu của `pcap1` là tìm đúng HTTP request có body chứa một file.

Không chọn flow bằng cảm tính. Flow đúng phải đồng thời thỏa mãn ba điều kiện:

1. Request sử dụng phương thức HTTP POST.
2. Header `Content-Type` là `application/octet-stream`.
3. Body bắt đầu bằng `iVBORw0KGgo`, tiền tố Base64 phổ biến của file PNG.

Thông tin flow đúng:

| Thuộc tính | Giá trị |
|---|---|
| Flow | `10.0.0.5:58999 -> 10.10.10.99:8888` |
| Request | `POST /api/data` |
| User-Agent | `python-requests/2.28.2` |
| Content-Length | `1492` |
| Tiền tố body | `iVBORw0KGgo` |
| Magic sau khi decode | `89 50 4E 47 0D 0A 1A 0A` |

Có thể lọc trong Wireshark:

```wireshark
http.request.method == "POST"
```

Hoặc:

```wireshark
http.request.uri == "/api/data"
```

Sau đó:

1. Chọn request đúng.
2. Nhấn chuột phải.
3. Chọn **Follow**.
4. Chọn **TCP Stream**.
5. Xác định phần body.
6. Cắt chính xác `1492` byte theo `Content-Length`.
7. Giải mã Base64.

Ví dụ:

```bash
base64 -d body.b64 > decoded.png
```

Kiểm tra file:

```bash
xxd -g 1 -l 16 decoded.png
file decoded.png
```

Kết quả đầu file phải là:

```text
89 50 4E 47 0D 0A 1A 0A
```

Đây là magic bytes của PNG.

Khi mở ảnh đã giải mã, ta thấy fragment:

```text
1c3_
```

### Fragment từ `pcap1`

```text
1c3_
```

Các upload giả bị loại vì không vượt qua toàn bộ chuỗi kiểm chứng:

```text
HTTP POST
    ↓
Content-Type: application/octet-stream
    ↓
Body là Base64 hợp lệ
    ↓
Giải mã được file có PNG magic
    ↓
Ảnh mở được
    ↓
Ảnh chứa fragment
```

Một body chỉ trông giống Base64 là chưa đủ.

Dữ liệu sau khi decode phải có magic hợp lệ và ảnh phải thực sự chứa fragment.

---

# 5. Phân tích `pcap2` — FTP transfer, PDF Base64 và các PDF filter

Đây là phần dễ khiến người chơi mắc kẹt.

Nhiều người chỉ kiểm tra port 21, thấy username, password và các lệnh FTP, nhưng không trích xuất được dữ liệu thật.

FTP có hai kênh riêng biệt:

- **Control channel:** dùng để truyền lệnh FTP.
- **Data channel:** dùng để truyền nội dung file.

Fragment không nằm trực tiếp trong control channel mà nằm trong data channel.

---

## 5.1. Cần làm gì đầu tiên sau khi mở file?

Mở `pcap2` trong Wireshark, sau đó kiểm tra:

```text
Statistics -> Protocol Hierarchy
```

hoặc:

```text
Statistics -> Conversations
```

Mục tiêu ban đầu là xác định protocol chính.

Nếu thấy FTP, không nên áp dụng hướng HTTP giống `pcap1`.

Lọc control channel bằng:

```wireshark
ftp
```

hoặc:

```wireshark
tcp.port == 21
```

Control channel chỉ cho biết:

- Quá trình đăng nhập.
- Chế độ truyền.
- Tên file được tải lên.
- Thông tin để xác định data port.

Nhấn chuột phải vào packet FTP và chọn:

```text
Follow TCP Stream
```

Tìm các lệnh quan trọng:

```text
USER
PASS
PASV
STOR
```

Không nên dừng lại sau khi thấy username và password.

Credentials chỉ là một phần của FTP log, không phải fragment.

---

## 5.2. Đọc control stream để tìm data channel

Control stream chứa các dòng quan trọng:

```text
USER ftpuser
PASS FtpP@ss2024!
PASV
STOR secret_data.bin
```

Phản hồi của lệnh `PASV` chứa:

```text
(10,0,0,1,192,1)
```

Trong Passive FTP, server trả về IP và port theo dạng:

```text
(a,b,c,d,p1,p2)
```

Địa chỉ IP:

```text
a.b.c.d
```

Data port được tính bằng công thức:

```text
port = p1 × 256 + p2
```

Trong trường hợp này:

```text
p1 = 192
p2 = 1
```

Tính:

```text
port = 192 × 256 + 1
port = 49152 + 1
port = 49153
```

Data port là:

```text
49153
```

Đây là bước chuyển từ control channel sang data channel.

Nếu không tính port từ phản hồi PASV, người chơi sẽ không thấy file thật được tải lên.

---

## 5.3. Trích xuất data stream

Lọc data port:

```wireshark
tcp.port == 49153
```

Flow dữ liệu đúng:

```text
10.0.0.5:49154 -> 10.0.0.1:49153
```

Lệnh FTP được sử dụng là:

```text
STOR secret_data.bin
```

`STOR` có nghĩa là client đang tải file lên server.

Vì vậy, chiều dữ liệu cần lấy là:

```text
Client -> Server
```

Thực hiện:

1. Chọn packet thuộc data connection.
2. Nhấn chuột phải.
3. Chọn **Follow TCP Stream**.
4. Chuyển chế độ hiển thị sang **Raw**.
5. Lưu toàn bộ stream.

Không nên copy trực tiếp từ chế độ ASCII vì nội dung có thể:

- Bị định dạng lại.
- Thêm xuống dòng.
- Mất byte.
- Bị chuyển đổi ký tự.

Payload trước khi decode là văn bản Base64:

```text
Payload type: base64 text
```

---

## 5.4. Giải mã Base64 thành PDF

Sau khi trích xuất data stream, giải mã Base64:

```bash
base64 -d secret_data.b64 > secret_data.pdf
```

Không chỉ kiểm tra rằng Base64 decode không báo lỗi.

Điều kiện chấp nhận là file sau khi decode phải bắt đầu bằng:

```text
%PDF-1.3
```

Kiểm tra:

```bash
head -c 16 secret_data.pdf
```

Hoặc:

```bash
xxd -g 1 -l 16 secret_data.pdf
```

Kết quả mong đợi:

```text
25 50 44 46 2D 31 2E 33
```

Tương ứng với:

```text
%PDF-1.3
```

Nếu file sau khi decode không bắt đầu bằng `%PDF`, có thể xảy ra một trong các trường hợp:

- Chọn sai stream.
- Chọn sai chiều truyền dữ liệu.
- Dữ liệu bị copy thiếu.
- Có thêm dữ liệu không thuộc Base64.
- Dùng nhầm control channel thay vì data channel.

---

## 5.5. Đọc stream và filter bên trong PDF

Khi mở PDF bằng trình đọc thông thường, fragment có thể không hiển thị rõ.

Trong trường hợp đó, cần kiểm tra các PDF object thô.

Content stream trong PDF sử dụng hai filter:

```text
/Filter [/ASCII85Decode /FlateDecode]
```

Cấu trúc object:

```text
/Filter [/ASCII85Decode /FlateDecode]
stream
    ... dữ liệu đã mã hóa ...
endstream
```

Các filter phải được xử lý đúng thứ tự:

```text
ASCII85Decode
      ↓
FlateDecode hoặc zlib decompress
```

Sau khi decode, ta thu được lệnh vẽ văn bản của PDF:

```text
BT 1 0 0 1 200 400 Tm (b34r_) Tj T* ET
```

Giải thích nhanh:

- `BT`: bắt đầu text object.
- `Tm`: thiết lập text matrix và vị trí.
- `(b34r_)`: chuỗi văn bản được vẽ.
- `Tj`: hiển thị chuỗi.
- `ET`: kết thúc text object.

Fragment là:

```text
b34r_
```

### Fragment từ `pcap2`

```text
b34r_
```

---

## 5.6. Tiêu chí loại bỏ decoy và hướng đi sai trong `pcap2`

Các hướng sai được loại bỏ bằng tiêu chí kỹ thuật:

- Port 21 chỉ là control channel, không chứa fragment.
- FTP username và password không phải flag.
- FTP password cũng không phải mật khẩu của `locked.zip`.
- Stream đúng phải vượt qua đầy đủ chuỗi kiểm chứng:

```text
PASV
  ↓
Tính data port 49153
  ↓
STOR secret_data.bin
  ↓
Trích xuất data stream đúng chiều
  ↓
Base64 decode
  ↓
%PDF-1.3
  ↓
ASCII85Decode
  ↓
FlateDecode
  ↓
Nội dung b34r_
```

Nếu PDF mở ra trống, chưa thể kết luận file sai.

Cần kiểm tra content stream vì fragment nằm trong stream đã qua filter.

---

# 6. Phân tích `pcap3` — File DOCX đính kèm qua SMTP

`pcap3` sử dụng SMTP multipart MIME.

Người chơi có thể mắc kẹt vì:

- Có nhiều attachment.
- Tên attachment gây nhiễu.
- Copy Base64 thủ công bị dính MIME boundary.
- Thiếu một số dòng Base64.
- Lấy nhầm SMTP terminator.
- Chỉ nhìn subject hoặc snippet mà không parse attachment.

Cách ổn định nhất là:

1. Xác định SMTP.
2. Tìm phần `DATA`.
3. Parse MIME.
4. Decode toàn bộ attachment.
5. Kiểm tra magic bytes của từng file.
6. Xác minh cấu trúc bên trong.

---

## 6.1. Cần làm gì đầu tiên sau khi mở file?

Mở `pcap3` trong Wireshark và kiểm tra:

```text
Statistics -> Protocol Hierarchy
```

Mục tiêu là nhận ra SMTP, không đi theo hướng HTTP hoặc FTP.

Lọc bằng:

```wireshark
smtp
```

hoặc:

```wireshark
tcp.port == 25
```

Trong SMTP, control data và nội dung email nằm trong cùng một flow.

Phần nội dung email được gửi sau lệnh:

```text
DATA
```

Nhấn chuột phải vào flow SMTP:

```text
Follow TCP Stream
```

Tìm các thành phần MIME:

```text
DATA
Content-Type
Content-Disposition
Content-Transfer-Encoding
boundary
filename
```

Không nên chọn attachment chỉ dựa vào:

- Tên file hấp dẫn.
- Kích thước file.
- Vị trí trong email.
- Cảm giác rằng đó là file đáng ngờ.

Cần decode tất cả attachment và kiểm tra file signature.

---

## 6.2. Parse MIME thay vì copy thủ công

Email sử dụng multipart MIME.

Mỗi attachment thường có header như:

```text
Content-Disposition: attachment; filename="data.bin"
Content-Transfer-Encoding: base64
```

Copy thủ công có thể gây ra các lỗi:

- Copy kèm MIME boundary.
- Copy kèm dấu kết thúc SMTP.
- Thiếu dòng Base64 đầu hoặc cuối.
- Thêm khoảng trắng không mong muốn.
- Chọn nhầm phần body.

Cách ổn định hơn:

- Lấy toàn bộ email sau lệnh `DATA`.
- Parse bằng thư viện email của Python.
- Hoặc dùng tính năng Export Objects nếu công cụ hỗ trợ.

Ví dụ script parse MIME:

```python
from email import policy
from email.parser import BytesParser
from pathlib import Path

message_path = Path("message.eml")
output_dir = Path("attachments")
output_dir.mkdir(exist_ok=True)

with message_path.open("rb") as file:
    message = BytesParser(policy=policy.default).parse(file)

for part in message.walk():
    filename = part.get_filename()

    if not filename:
        continue

    payload = part.get_payload(decode=True)

    if payload is None:
        continue

    output_path = output_dir / filename
    output_path.write_bytes(payload)

    print(f"[+] Extracted: {output_path}")
```

---

## 6.3. Decode toàn bộ attachment và kiểm tra magic bytes

Sau khi giải mã Base64 của các attachment, file đúng là:

```text
data.bin
```

Các byte đầu:

```text
50 4B 03 04
```

Đây là magic của ZIP Local File Header:

```text
PK\x03\x04
```

DOCX thực chất là một ZIP container chứa các file XML.

Thông tin của attachment đúng:

| Thuộc tính | Giá trị |
|---|---|
| Attachment | `data.bin` |
| Magic | `50 4B 03 04` |
| Loại file | ZIP container, ứng viên DOCX |

Tuy nhiên, chỉ thấy `PK` là chưa đủ.

Rất nhiều định dạng khác cũng sử dụng ZIP container, ví dụ:

- DOCX.
- XLSX.
- PPTX.
- JAR.
- APK.
- EPUB.
- File ZIP thông thường.

Do đó, cần liệt kê nội dung:

```bash
unzip -l data.bin | head
```

Cấu trúc mong đợi:

```text
[Content_Types].xml
_rels/.rels
word/document.xml
```

Sự xuất hiện của:

```text
word/document.xml
```

xác nhận đây là file DOCX.

Có thể đổi phần mở rộng:

```bash
cp data.bin recovered.docx
```

---

## 6.4. Trích xuất `word/document.xml` để lấy fragment

Nội dung chính của file DOCX được lưu trong:

```text
word/document.xml
```

Không bắt buộc phải dùng Microsoft Word.

Có thể trích xuất trực tiếp bằng câu lệnh:

```bash
unzip -p data.bin word/document.xml > document.xml
```

Sau đó loại bỏ các XML tag bằng Python:

```python
import re

with open(
    "document.xml",
    encoding="utf-8",
    errors="ignore"
) as file:
    xml = file.read()

text = re.sub(r"<[^>]+>", "\n", xml)

for line in text.splitlines():
    line = line.strip()

    if line:
        print(line)
```

Nội dung trích xuất được:

```text
15_
```

### Fragment từ `pcap3`

```text
15_
```

---

## 6.5. Tiêu chí loại bỏ decoy và hướng đi sai trong `pcap3`

Các attachment có tên hấp dẫn vẫn bị loại nếu:

- Decode ra file quá nhỏ.
- Không có magic hợp lệ.
- Không mở được.
- Không có cấu trúc DOCX.
- Không chứa `word/document.xml`.

Một file bắt đầu bằng `PK` vẫn chưa đủ để kết luận là DOCX.

Chuỗi kiểm chứng đầy đủ:

```text
SMTP DATA
    ↓
Multipart MIME
    ↓
Attachment Base64
    ↓
Decode data.bin
    ↓
Magic PK 03 04
    ↓
Cấu trúc DOCX
    ↓
word/document.xml
    ↓
Nội dung 15_
```

Fragment phải được lấy từ `document.xml`, không lấy từ:

- Subject.
- Email body snippet.
- Tên attachment.
- SMTP credentials.
- MIME headers.

---

# 7. Phân tích `pcap4` — Ghép các HTTP chunk thành ảnh JPEG

Trong `pcap4`, dữ liệu được chia nhỏ qua nhiều request tới endpoint:

```text
/api/chunk
```

Capture chứa rất nhiều nhóm chunk nhiễu.

Các cách sau sẽ dẫn đến kết quả sai:

- Lấy riêng một request.
- Ghép mọi HTTP body trong toàn capture.
- Ghép theo frame order toàn cục.
- Không phân biệt các flow.
- Sắp xếp index theo chuỗi thay vì theo số.

Mỗi chunk chỉ chứa một phần Base64 và không thể tự tạo thành file hoàn chỉnh.

Các chunk phải được:

1. Nhóm theo flow hoặc session.
2. Kiểm tra `X-Chunk-Total`.
3. Sắp xếp theo `X-Chunk-Index`.
4. Ghép body.
5. Base64 decode.
6. Xác minh magic JPEG.
7. Mở ảnh để đọc fragment.

---

## 7.1. Cần làm gì đầu tiên sau khi mở file?

Mở `pcap4` trong Wireshark và lọc HTTP:

```wireshark
http
```

Lọc chính xác endpoint:

```wireshark
http.request.uri contains "/api/chunk"
```

Kiểm tra các header:

```text
X-Chunk-Index: <index>
X-Chunk-Total: <total>
```

Trong đó:

- `X-Chunk-Index` cho biết vị trí của chunk.
- `X-Chunk-Total` cho biết tổng số chunk cần có.

Không nên export riêng từng body và thử mở, vì mỗi body chỉ là một đoạn Base64.

Cũng không được ghép tất cả request trong capture vì có nhiều nhóm nhiễu.

---

## 7.2. Nhóm các chunk đúng cách

Mỗi request `/api/chunk` có body chứa một đoạn Base64.

Phương pháp nhóm an toàn:

- Nhóm theo network 4-tuple hoặc 5-tuple:
  - Source IP.
  - Destination IP.
  - Source port.
  - Destination port.
  - Protocol.
- Có thể kết hợp thêm `X-Chunk-Total`.
- Chỉ chấp nhận nhóm chứa đủ số lượng chunk được chỉ ra.
- Không được thiếu index.
- Không được có index trùng lặp.
- Sắp xếp `X-Chunk-Index` theo số nguyên.
- Không sắp xếp theo chuỗi.
- Không phụ thuộc vào frame order nếu đã có index rõ ràng.

Ví dụ, với:

```text
X-Chunk-Total: 7
```

nhóm hợp lệ phải có đủ bảy index, chẳng hạn:

```text
0, 1, 2, 3, 4, 5, 6
```

hoặc:

```text
1, 2, 3, 4, 5, 6, 7
```

tùy cách đánh số được sử dụng trong capture.

Sau khi sắp xếp, ghép body theo đúng thứ tự.

Kết quả sau khi ghép vẫn là Base64 text, chưa phải JPEG thô.

Sau quá trình nhóm và kiểm chứng, nhóm đúng nằm quanh các frame:

```text
95872–95896
```

Thông tin:

| Thuộc tính | Giá trị |
|---|---|
| Frames | `95872–95896` |
| Số chunk | `7` |
| X-Chunk-Total | `7` |
| Magic sau khi decode | `FF D8 FF E0 00 10 4A 46 49 46` |
| Loại file | JPEG/JFIF |

Khoảng frame không phải điều kiện để đoán trước.

Đó chỉ là kết quả sau khi thực hiện việc nhóm và kiểm chứng.

Điều kiện chấp nhận thật sự là dữ liệu sau khi decode phải tạo thành một JPEG hợp lệ.

---

## 7.3. Decode và xác minh file JPEG

Sau khi ghép Base64 từ bảy chunk, giải mã:

```bash
base64 -d joined_chunks.b64 > recovered.jpg
```

Không chỉ kiểm tra xem lệnh Base64 có chạy thành công hay không.

Cần xác minh file signature:

```text
JPEG start magic: FF D8 FF
JFIF marker     : 4A 46 49 46
JPEG end marker : FF D9
```

Kiểm tra bằng:

```bash
xxd -g 1 -l 16 recovered.jpg
file recovered.jpg
```

Kết quả mong đợi:

```text
FF D8 FF E0 00 10 4A 46 49 46
```

Trong đó:

```text
FF D8 FF
```

là JPEG magic, còn:

```text
4A 46 49 46
```

là chuỗi ASCII:

```text
JFIF
```

Có thể kiểm tra hai byte cuối:

```bash
tail -c 2 recovered.jpg | xxd -g 1
```

Kết quả tùy chọn:

```text
FF D9
```

Nếu một nhóm khác cũng Base64 decode được nhưng:

- Không bắt đầu bằng `FF D8 FF`.
- Không được lệnh `file` nhận diện là ảnh.
- Không mở được.
- Không có JFIF marker.
- Không hiển thị fragment.

thì nhóm đó là dữ liệu nhiễu.

Ảnh JPEG đúng hiển thị:

```text
cu73?}
```

### Fragment từ `pcap4`

```text
cu73?}
```

---

## 7.4. Tiêu chí loại bỏ decoy và hướng đi sai trong `pcap4`

Một request `/api/chunk` đơn lẻ không chứa đủ dữ liệu để tạo file.

Không được ghép toàn bộ HTTP body trong capture vì có nhiều nhóm nhiễu.

Các nhóm sau phải bị loại:

- Thiếu index.
- Có index trùng lặp.
- Có số chunk ít hơn `X-Chunk-Total`.
- Không cùng flow.
- Ghép xong nhưng Base64 không hợp lệ.
- Decode được byte nhưng không có JPEG magic.
- File không mở được.
- Ảnh không chứa fragment.

Chuỗi kiểm chứng đầy đủ:

```text
/api/chunk
    ↓
Nhóm theo flow và X-Chunk-Total
    ↓
Kiểm tra đủ index
    ↓
Sắp xếp theo X-Chunk-Index
    ↓
Ghép Base64
    ↓
Decode
    ↓
JPEG/JFIF magic
    ↓
Mở ảnh
    ↓
cu73?}
```

---

# 8. Ghép flag

Flag được ghép dựa trên cách thử thách chia dữ liệu:

- Ảnh đĩa E01 cung cấp phần mở đầu và fragment đầu tiên.
- `locked.zip` xác nhận `pcap1` đến `pcap4` chứa bốn fragment còn lại.
- Số thứ tự của các PCAP chính là thứ tự ghép fragment.

Bảng tổng hợp:

| Thứ tự | Nguồn | Phương pháp kiểm chứng chính | Fragment |
|---:|---|---|---|
| 1 | E01 — `icy.png` | OpenStego trích xuất `flag.txt` | `V1t{d0_` |
| 2 | E01 — `chloe.png` | OpenStego trích xuất `key.txt`, sau đó XOR `0x03` | `y0u_7h1nk_` |
| 3 | `pcap1` | HTTP POST, Base64 decode thành PNG | `1c3_` |
| 4 | `pcap2` | FTP PASV data, Base64 PDF, ASCII85 và Flate | `b34r_` |
| 5 | `pcap3` | SMTP MIME attachment, DOCX và `document.xml` | `15_` |
| 6 | `pcap4` | HTTP chunks, Base64 decode thành JPEG | `cu73?}` |

Ghép theo thứ tự:

```text
V1t{d0_
y0u_7h1nk_
1c3_
b34r_
15_
cu73?}
```

Kết quả:

```text
V1t{d0_y0u_7h1nk_1c3_b34r_15_cu73?}
```

---

# 9. Checklist tái hiện quá trình giải

## Phần E01

- [ ] Mở ảnh đĩa E01.
- [ ] Xác định phân vùng NTFS bắt đầu tại sector `2048`.
- [ ] Tính byte offset:

```text
2048 × 512 = 1048576
```

- [ ] Kiểm tra `Users/Bob/Desktop/flag.txt`.
- [ ] Xác định đây là flag giả.
- [ ] Đọc `investigation_notes.txt`.
- [ ] Kiểm tra log của StegAnalyzer.
- [ ] Truy cập `$RECYCLE.BIN`.
- [ ] Trích xuất `system_backup_nov.zip`.
- [ ] Lấy `backup/photo_009.png`.
- [ ] Lấy `backup/large.zip`.
- [ ] Trong `photo_009.png`, tìm marker:

```text
ASCII-aGFoYV84Mzg2
```

- [ ] Xác nhận marker nằm tại offset:

```text
0x36181d
```

- [ ] Base64 decode:

```text
aGFoYV84Mzg2 -> haha_8386
```

- [ ] Sửa Local File Header của `large.zip`:

```text
11 11 11 11 -> 50 4B 03 04
```

- [ ] Sửa EOCD:

```text
00 00 00 00 -> 50 4B 05 06
```

- [ ] Mở `large.zip` bằng:

```text
haha_8386
```

- [ ] Trích xuất `small.zip`.
- [ ] Dùng OpenStego 0.8.6 trên toàn bộ ảnh.
- [ ] Ghi lại:

```text
icy.png   -> V1t{d0_
house.png -> XOR
chloe.png -> z3v\4k2mh\
```

- [ ] XOR dữ liệu của `chloe.png` với `0x03`.
- [ ] Thu được:

```text
y0u_7h1nk_
```

---

## Phần `pcap5`

- [ ] Mở `pcap5`.
- [ ] Xác định các HTTP `/data/stream`.
- [ ] Nhóm request theo flow.
- [ ] Sắp xếp bằng `X-Frame-Index`.
- [ ] Không ghép theo frame order toàn cục.
- [ ] Tìm bitstream có 72 bit.
- [ ] Chuyển từng nhóm 8 bit sang ASCII.
- [ ] Thu được:

```text
hihi_6969
```

- [ ] Dùng mật khẩu này mở `locked.zip`.
- [ ] Đọc `hint.txt`.
- [ ] Xác nhận `pcap1` đến `pcap4` chứa các fragment còn lại.

---

## Phần `pcap1`

- [ ] Tìm HTTP POST.
- [ ] Xác nhận URI:

```text
/api/data
```

- [ ] Xác nhận:

```text
Content-Type: application/octet-stream
```

- [ ] Xác nhận:

```text
Content-Length: 1492
```

- [ ] Xác nhận body bắt đầu bằng:

```text
iVBORw0KGgo
```

- [ ] Reassemble TCP stream.
- [ ] Cắt chính xác số byte theo `Content-Length`.
- [ ] Base64 decode.
- [ ] Kiểm tra PNG magic:

```text
89 50 4E 47 0D 0A 1A 0A
```

- [ ] Mở ảnh.
- [ ] Thu được:

```text
1c3_
```

---

## Phần `pcap2`

- [ ] Lọc FTP control channel:

```wireshark
ftp
```

hoặc:

```wireshark
tcp.port == 21
```

- [ ] Đọc các lệnh:

```text
USER ftpuser
PASS FtpP@ss2024!
PASV
STOR secret_data.bin
```

- [ ] Đọc phản hồi PASV:

```text
(10,0,0,1,192,1)
```

- [ ] Tính data port:

```text
192 × 256 + 1 = 49153
```

- [ ] Lọc:

```wireshark
tcp.port == 49153
```

- [ ] Xác định chiều truyền:

```text
10.0.0.5:49154 -> 10.0.0.1:49153
```

- [ ] Export stream ở chế độ Raw.
- [ ] Base64 decode.
- [ ] Xác nhận PDF magic:

```text
%PDF-1.3
```

- [ ] Kiểm tra PDF filter:

```text
/ASCII85Decode
/FlateDecode
```

- [ ] Decode theo thứ tự:

```text
ASCII85 -> Flate
```

- [ ] Thu được lệnh PDF:

```text
BT 1 0 0 1 200 400 Tm (b34r_) Tj T* ET
```

- [ ] Fragment:

```text
b34r_
```

---

## Phần `pcap3`

- [ ] Lọc SMTP:

```wireshark
smtp
```

hoặc:

```wireshark
tcp.port == 25
```

- [ ] Tìm lệnh `DATA`.
- [ ] Trích xuất toàn bộ MIME message.
- [ ] Parse tất cả attachment.
- [ ] Decode Base64.
- [ ] Xác định attachment đúng là:

```text
data.bin
```

- [ ] Xác nhận magic:

```text
50 4B 03 04
```

- [ ] Liệt kê ZIP.
- [ ] Xác nhận có:

```text
[Content_Types].xml
_rels/.rels
word/document.xml
```

- [ ] Trích xuất:

```text
word/document.xml
```

- Đọc text.
- Thu được:

```text
15_
```

---

## Phần `pcap4`

- [ ] Lọc:

```wireshark
http.request.uri contains "/api/chunk"
```

- Đọc:

```text
X-Chunk-Index
X-Chunk-Total
```

- Nhóm theo flow.
- Chỉ giữ nhóm có đủ chunk.
- Loại nhóm thiếu hoặc trùng index.
- Sắp xếp index theo số.
- Ghép body Base64.
- Base64 decode.
- Xác nhận JPEG magic:

```text
FF D8 FF
```

- [ ] Xác nhận JFIF marker:

```text
4A 46 49 46
```

- [ ] Mở ảnh.
- [ ] Thu được:

```text
cu73?}
```

---

## Ghép flag

- Ghép:

```text
V1t{d0_
y0u_7h1nk_
1c3_
b34r_
15_
cu73?}
```

- Kết quả:

```text
V1t{d0_y0u_7h1nk_1c3_b34r_15_cu73?}
```

---
