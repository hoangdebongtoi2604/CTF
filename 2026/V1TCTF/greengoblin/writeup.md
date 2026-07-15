
# Write-up — V1T CTF 2026: Green Plasma

## File được cung cấp

- `GreenGoblin.raw` — Raw memory dump của hệ điều hành Windows.

---

## Challenge Description

> Green Goblin đã sử dụng một nguồn Dark Energy bí mật để tấn công hệ thống. May mắn thay, hệ thống phòng thủ đã đóng băng payload ngay trong lúc thực thi, khiến Dark Energy bị vỡ thành 5 mảnh và phân tán trong các thành phần nội bộ của hệ điều hành: R, KO, D, EL và M.
>
> Nhiệm vụ của người chơi là tìm lại cả 5 mảnh, ghép chúng theo đúng thứ tự và phong ấn sức mạnh của Green Goblin.

---

## Tổng quan

Thử thách cung cấp một file memory dump duy nhất:

```text
GreenGoblin.raw
```

Theo mô tả, có tổng cộng 5 fragment được giấu trong các thành phần khác nhau của hệ điều hành.

Các ký hiệu **R, KO, D, EL và M** tương ứng với những artifact quen thuộc trong Windows Forensics:

| Ký hiệu | Ý nghĩa | Artifact cần kiểm tra |
|---|---|---|
| R | Registry | Windows Registry |
| KO | Kernel Objects | Handles, Section, Mutant |
| D | Disk | File Objects, MFT, ADS |
| EL | Event Logs | Windows Event Logs |
| M | Memory | VAD, mapped memory |

Thứ tự ghép fragment được chỉ rõ trong đề:

```text
R → KO → D → EL → M
```

Sau khi thu thập đủ 5 fragment, chúng ta cần ghép chúng lại và giải mã để lấy flag.

---

# 1. Fragment 1 — R: Registry

Mảnh đầu tiên được giấu trong Windows Registry.

Do thử thách chỉ cung cấp memory dump mà không có disk image, chúng ta không thể mở trực tiếp các file Registry hive như:

```text
SYSTEM
SOFTWARE
SAM
SECURITY
NTUSER.DAT
```

Tuy nhiên, những Registry hive đang được hệ điều hành sử dụng vẫn được ánh xạ trong bộ nhớ.

Volatility 3 cho phép đọc các Registry key trực tiếp từ memory dump thông qua plugin:

```text
windows.registry.printkey
```

Trong quá trình kiểm tra các chuỗi tồn tại trong memory dump, có thể thấy rất nhiều dữ liệu lặp lại chứa chuỗi:

```text
N01S3_
```

Chuỗi này có vẻ là dữ liệu nhiễu hoặc decoy do malware tạo ra nhằm làm khó quá trình điều tra.

Khi kiểm tra ngữ cảnh xung quanh các chuỗi này, chúng ta thấy chúng có liên quan đến Registry key:

```text
Software\Policies\Microsoft\CloudFiles
```

Do đó, ta truy vấn trực tiếp key này:

```bash
vol -f GreenGoblin.raw windows.registry.printkey \
    --key "Software\Policies\Microsoft\CloudFiles"
```

Kết quả cho thấy có 15 giá trị giả, từ:

```text
DiagnosticData_0
```

đến:

```text
DiagnosticData_14
```

Các giá trị này đều chứa chuỗi nhiễu:

```text
N01S3_
```

Tuy nhiên, bên cạnh các giá trị giả còn có một giá trị chính mang tên:

```text
DiagnosticData
```

Giá trị này chứa fragment thật.

## Fragment 1

```text
'`%L`0
```

---

# 2. Fragment 2 — KO: Kernel Objects

Mảnh thứ hai nằm trong các **Kernel Object**.

Trong Windows, tiến trình tương tác với các đối tượng kernel thông qua handle.

Một số loại Kernel Object phổ biến bao gồm:

- File
- Process
- Thread
- Mutant
- Event
- Section
- Registry Key

Trước tiên, chúng ta cần xác định tiến trình đáng ngờ đang chạy trong hệ thống.

Sử dụng plugin:

```text
windows.pslist
```

Sau đó lọc những tiến trình có tên liên quan đến thử thách:

```bash
vol -f GreenGoblin.raw windows.pslist | grep -i "Green"
```

Kết quả:

```text
8040    GreenPlasma.exe
```

Tiến trình đáng ngờ là:

```text
GreenPlasma.exe
```

với PID:

```text
8040
```

Tiếp theo, chúng ta liệt kê toàn bộ handle đang được tiến trình này mở bằng plugin:

```text
windows.handles
```

Malware thường sử dụng `Section Object` để:

- Tạo vùng nhớ chia sẻ.
- Giao tiếp giữa các tiến trình.
- Ánh xạ dữ liệu vào bộ nhớ.
- Lưu dữ liệu tạm thời mà không cần ghi trực tiếp ra file.
- Hỗ trợ các kỹ thuật process injection.

Do đó, ta lọc các handle thuộc loại `Section`:

```bash
vol -f GreenGoblin.raw windows.handles --pid 8040 | grep "Section"
```

Trong kết quả, có một Section Object với tên rất bất thường:

```text
8040    GreenPlasma.exe    0x54    Section    \Sessions\1\BaseNamedObjects\9cGb0c
```

Tên của đối tượng nằm trong namespace:

```text
\Sessions\1\BaseNamedObjects\
```

Đây là nơi Windows thường lưu các named object như:

- Mutex
- Event
- Semaphore
- Shared memory section

Phần tên bất thường của Section Object chính là fragment cần tìm.

## Fragment 2

```text
9cGb0c
```

---

# 3. Fragment 3 — D: Disk và Alternate Data Streams

Mảnh thứ ba liên quan đến dữ liệu trên ổ đĩa.

Mặc dù không có disk image, Windows Memory Manager vẫn có thể giữ lại các `File Object` của những file:

- Đang được mở.
- Vừa được sử dụng.
- Đang nằm trong bộ nhớ cache.
- Được tiến trình malware truy cập.

Volatility có thể quét các File Object trong memory dump bằng plugin:

```text
windows.filescan
```

Malware thường lưu file trong những thư mục mà người dùng thông thường có quyền ghi, ví dụ:

```text
C:\Users\Public
C:\Windows\Temp
C:\Users\<username>\AppData\Local\Temp
```

Vì vậy, ta tìm kiếm những file nằm trong thư mục `Users\Public`:

```bash
vol -f GreenGoblin.raw windows.filescan | grep -i "Users\\Public"
```

Kết quả đáng chú ý:

```text
0x3f8a9b1c    \Device\HarddiskVolume3\Users\Public\Downloads\config.ini:hidden
```

Đường dẫn có phần:

```text
config.ini:hidden
```

Đây là một **Alternate Data Stream**, viết tắt là ADS.

## Alternate Data Stream là gì?

Trên hệ thống file NTFS, một file có thể chứa nhiều luồng dữ liệu.

Luồng dữ liệu mặc định thường được truy cập như sau:

```text
filename
```

Trong khi đó, một luồng dữ liệu phụ có cú pháp:

```text
filename:streamname
```

Trong trường hợp này:

```text
File chính: config.ini
ADS: hidden
```

Malware đã giấu dữ liệu trong ADS để tránh bị phát hiện khi người dùng chỉ kiểm tra file bằng File Explorer hoặc các câu lệnh thông thường.

Offset vật lý của File Object là:

```text
0x3f8a9b1c
```

Ta sử dụng plugin `windows.dumpfiles` để trích xuất nội dung file từ memory dump:

```bash
vol -f GreenGoblin.raw windows.dumpfiles --physaddr 0x3f8a9b1c
```

Volatility xác nhận file đang được dump:

```text
[*] Dumping \Device\HarddiskVolume3\Users\Public\Downloads\config.ini:hidden
```

Đọc nội dung file vừa trích xuất, ta thu được fragment thứ ba.

## Fragment 3

```text
03`809
```

---

# 4. Fragment 4 — EL: Event Logs

Mảnh thứ tư nằm trong Windows Event Logs.

Một cách tiếp cận đầy đủ là tìm và trích xuất các file log như:

```text
Application.evtx
System.evtx
Security.evtx
```

Tuy nhiên, các file EVTX được carve từ memory dump có thể gặp các vấn đề như:

- Không đầy đủ.
- Bị phân mảnh.
- Bị hỏng cấu trúc.
- Không thể mở trực tiếp bằng Event Viewer.
- Chỉ còn một phần dữ liệu nằm trong cache.

Trong trường hợp này, các thông báo sự kiện gần đây vẫn còn tồn tại dưới dạng chuỗi plaintext trong bộ nhớ.

Vì vậy, ta có thể sử dụng `strings` và `grep` để tìm nội dung của các event.

Theo dấu vết của thử thách, ta cần kiểm tra các sự kiện ứng dụng bị crash.

Trên Windows, lỗi ứng dụng thường được ghi trong `Application Log` với Event ID:

```text
1000
```

Một Event ID 1000 thường chứa những trường như:

```text
Faulting application name
Faulting module name
Faulting application path
Faulting module path
Exception code
Fault offset
```

Do đó, ta tìm chuỗi:

```text
faulting module path:
```

bằng câu lệnh:

```bash
strings GreenGoblin.raw | grep -i "faulting module path:"
```

Kết quả chứa rất nhiều event giả:

```text
Faulting application name: svchost.exe, version: 10.0.22621.1, faulting module path: N01S3_
Faulting application name: svchost.exe, version: 10.0.22621.1, faulting module path: N01S3_
...
```

Có khoảng 25 bản ghi giả liên quan đến `svchost.exe`, tất cả đều chứa chuỗi nhiễu:

```text
N01S3_
```

Tuy nhiên, xen giữa các event giả có một event khác biệt:

```text
Faulting application name: ctfmon.exe, version: 10.0.22621.1, faulting module path: cC50C_
```

Sự kiện liên quan đến `ctfmon.exe` không giống các bản ghi decoy còn lại.

Phần `faulting module path` của event này chứa fragment thật.

## Fragment 4

```text
cC50C_
```

---

# 5. Fragment 5 — M: Memory Map và VAD

Mảnh cuối cùng nằm trong không gian bộ nhớ của tiến trình.

Ở Fragment 2, chúng ta đã tìm thấy một Section Object đáng ngờ:

```text
\Sessions\1\BaseNamedObjects\9cGb0c
```

Section Object thường được sử dụng để:

- Tạo shared memory.
- Ánh xạ dữ liệu vào không gian địa chỉ của tiến trình.
- Giao tiếp giữa các tiến trình.
- Chia sẻ payload hoặc configuration.
- Hỗ trợ process injection.

Để kiểm tra các vùng bộ nhớ được ánh xạ trong `GreenPlasma.exe`, ta phân tích **Virtual Address Descriptor**, viết tắt là VAD.

## VAD là gì?

Mỗi tiến trình Windows có một cây VAD dùng để quản lý các vùng địa chỉ ảo của tiến trình.

Các vùng này có thể bao gồm:

- Executable image.
- DLL.
- Heap.
- Stack.
- Shared memory.
- Private memory.
- Memory-mapped file.
- Những vùng bộ nhớ được cấp phát thủ công.

Ta dump toàn bộ VAD của tiến trình `GreenPlasma.exe`, PID `8040`:

```bash
mkdir -p vads

vol -f GreenGoblin.raw windows.vaddump \
    --pid 8040 \
    --dump-dir ./vads/
```

Sau khi dump, thư mục `vads` sẽ chứa nhiều file `.dmp`.

Mỗi file tương ứng với một vùng bộ nhớ của tiến trình.

Ta tiếp tục chạy `strings` trên toàn bộ các vùng nhớ đã dump.

Do đã biết malware sử dụng chuỗi `N01S3_` làm dữ liệu giả, ta loại bỏ những kết quả chứa chuỗi này:

```bash
strings ./vads/*.dmp | grep -v "N01S3" | grep -E "^.{6}$"
```

Giải thích câu lệnh:

```text
strings ./vads/*.dmp
```

Trích xuất các chuỗi có thể đọc được từ tất cả file VAD dump.

```text
grep -v "N01S3"
```

Loại bỏ những dòng chứa chuỗi decoy `N01S3`.

```text
grep -E "^.{6}$"
```

Chỉ giữ lại những chuỗi có đúng 6 ký tự.

Trong kết quả, ta tìm thấy chuỗi đáng ngờ:

```text
_dEbCN
```

Chuỗi này xuất hiện tại offset `0x250` của vùng shared memory section.

## Fragment 5

```text
_dEbCN
```

---

# 6. Ghép các Fragment

Sau quá trình điều tra, chúng ta đã thu được đầy đủ 5 fragment:

| Thứ tự | Artifact | Fragment |
|---|---|---|
| 1 | Registry — R | `'`%L`0` |
| 2 | Kernel Objects — KO | `9cGb0c` |
| 3 | Disk — D | `03`809` |
| 4 | Event Logs — EL | `cC50C_` |
| 5 | Memory — M | `_dEbCN` |

Ghép các fragment theo đúng thứ tự được nêu trong đề:

```text
R → KO → D → EL → M
```

Ta thu được chuỗi:

```text
'`%L`09cGb0c03`809cC50C__dEbCN
```

Chuỗi này có độ dài 30 ký tự và trông giống dữ liệu ngẫu nhiên.

Tuy nhiên, flag của giải có định dạng:

```text
V1T{...}
```

Ta có thể so sánh những ký tự đầu tiên của ciphertext với phần đầu của flag:

| Ciphertext | Mã ASCII | Plaintext | Mã ASCII | Khoảng cách |
|---|---:|---|---:|---:|
| `'` | 39 | `V` | 86 | +47 |
| `` ` `` | 96 | `1` | 49 | Dịch 47 và quay vòng |
| `%` | 37 | `T` | 84 | +47 |
| `L` | 76 | `{` | 123 | +47 |

Khoảng dịch chuyển 47 ký tự trong vùng ASCII có thể in được cho thấy đây là mã hóa:

```text
ROT47
```

---

# 7. Giải mã ROT47

ROT47 hoạt động trên các ký tự ASCII có thể in được, nằm trong khoảng mã ASCII từ 33 đến 126.

Mỗi ký tự được dịch đi 47 vị trí trong tập gồm 94 ký tự.

Nếu phép dịch vượt qua ký tự cuối cùng, nó sẽ quay lại từ đầu.

Ta có thể giải mã bằng CyberChef hoặc sử dụng Python.

Tạo file:

```text
solve.py
```

Nội dung:

```python
def rot47(ciphertext):
    result = []

    for character in ciphertext:
        ascii_value = ord(character)

        # ROT47 chỉ áp dụng với các ký tự ASCII
        # có thể in được từ 33 đến 126.
        if 33 <= ascii_value <= 126:
            decoded_ascii = 33 + ((ascii_value - 33 + 47) % 94)
            result.append(chr(decoded_ascii))
        else:
            # Giữ nguyên ký tự nằm ngoài phạm vi ROT47.
            result.append(character)

    return "".join(result)


cipher = "'`%L`09cGb0c03`809cC50C__dEbCN"

flag = rot47(cipher)

print(f"[+] FLAG: {flag}")
```

Chạy script:

```bash
python3 solve.py
```

Kết quả:

```text
[+] FLAG: V1T{1_h4v3_4_b1g_h4rd_r005t3r}
```

---

# Flag

```text
V1T{1_h4v3_4_b1g_h4rd_r005t3r}
```

---

# Tổng kết

Thử thách yêu cầu người chơi kết hợp nhiều kỹ thuật Windows Memory Forensics khác nhau:

- Đọc Registry hive từ memory dump.
- Phân tích process và handle.
- Kiểm tra Kernel Object.
- Tìm File Object trong bộ nhớ.
- Nhận diện và trích xuất Alternate Data Stream.
- Tìm Windows Event Log còn tồn tại dưới dạng plaintext.
- Dump và phân tích các vùng VAD.
- Điều tra shared memory.
- Nhận diện và giải mã ROT47.

Luồng giải tổng thể:

```text
GreenGoblin.raw
        │
        ├── Registry
        │      └── DiagnosticData
        │
        ├── Kernel Objects
        │      └── Named Section Object
        │
        ├── Disk
        │      └── NTFS Alternate Data Stream
        │
        ├── Event Logs
        │      └── Application Crash Event
        │
        └── Memory
               └── VAD và Shared Memory
                        │
                        ▼
                 Ghép 5 fragment
                        │
                        ▼
                     ROT47
                        │
                        ▼
                      Flag

