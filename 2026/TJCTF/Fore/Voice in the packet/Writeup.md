# Đề bài :
<img width="949" height="247" alt="image" src="https://github.com/user-attachments/assets/b6e14c96-a416-4e9c-9d5c-8c79b88c068a" />

Đề cho ta 1 file pcap, ta mở file bằng wireshark

Ta vào 
```bash
Statistics > Conversations > UDP
```
<img width="1315" height="402" alt="image" src="https://github.com/user-attachments/assets/5772fffb-cd9f-40bb-b631-58734f42517a" />

Ta thấy 3 luồng UDP chính :
```bash
10.13.37.1:31337      -> 10.13.37.2:31338       1 packet
192.168.1.100:10000   -> 192.168.1.200:20000    1000 packets
172.16.24.10:4242     -> 172.16.24.11:9001      1 packet
```
Ta thấy luồng đáng nghi với 1000 packet 
```
192.168.1.100:10000 -> 192.168.1.200:20000
```

Ta filter theo luồng chính này 

Sau khi filter, ta vào 1 packet và xem thử UDP payload 
```bash
800003e800000000123456780000000d78180c21b625ec25a6216419220e340122f478e894df86dae8d9caddb6e5c0f096fdb60a9016c21f30253b26be22271b59109c0374f66aeaf0e020dbaed9c3dc03e492ee30fb61089214561e84246126b223cc1c7e120106cff875ec6ae2e1db9bd
```
Sau khi vứt phần UDP payload thì ta có thể biết được ý nghĩa chính của dòng này 

Header chính của nó là 
```bash
80 00 03 e8 00 00 00 00 12 34 56 78
```
Đây chính là header của RTP 

RTP là protocol chính dùng để truyền dữ liệu thời gian thực qua mạng
```bash
80          -> RTP version 2
00          -> Payload Type 0
03 e8       -> Sequence number = 1000
00 00 00 00 -> Timestamp
12 34 56 78 -> SSRC
```

Payload Type 0 trong RTP thường là G.711 PCMU, đúng kiểu VoIP, voice over ip 

Ta chỉnh sửa decode mặc định của packet thành rdp, sau đó dùng lại filter RDP 
```bash
chuột phải vào 1 gói tin, chọn decode as, sau đấy chuyển từ mặc định sang RDP
```

Khi soi các packet đầu của RTP stream, sẽ thấy payload audio lặp theo chu kỳ 5 packet.

Các packet sau gần như lặp lại mẫu cũ, nhưng 5 packet đầu có vài byte bị đổi đúng 1 bit.

Giống kiểu như sau 2 và 7 có thể lệnh nhau đúng 1 bit,3 và 8 cũng vậy, 4 vầ 9 cũng vậy 

| packet 2 | packet 7 | 
| --- | --- | 
| <img width="1915" height="910" alt="image" src="https://github.com/user-attachments/assets/b2ea914a-79d1-46ae-9021-64bc81673628" /> | <img width="1588" height="926" alt="image" src="https://github.com/user-attachments/assets/9dc2f2e0-9d2b-4b4a-90a9-27db437f4d21" />

Các thay đổi chỉ lệch +1 hoặc -1, tức là thay đổi bit thấp nhất — LSB.

Hướng tư duy của ta như sau : 
Lấy 5 RTP audio payload đầu tiên.
Mỗi payload dài 160 bytes.
Chỉ lấy byte ở offset chẵn: 0, 2, 4, ..., 158.
Lấy LSB của các byte đó.
Ghép bit theo MSB-first.

Tổng số bit : 
```
5 packets * 80 bytes = 400 bits = 50 bytes
```

Script giải cho bài này :
```bash
#!/usr/bin/env python3
import sys
import struct

pcap = sys.argv[1]

data = open(pcap, "rb").read()

magic = data[:4]

if magic == b"\xd4\xc3\xb2\xa1":
    endian = "<"
elif magic == b"\xa1\xb2\xc3\xd4":
    endian = ">"
else:
    sys.exit("not pcap")

off = 24
payloads = []

while off + 16 <= len(data):
    ts_sec, ts_usec, incl_len, orig_len = struct.unpack(
        endian + "IIII",
        data[off:off + 16]
    )
    off += 16

    pkt = data[off:off + incl_len]
    off += incl_len

    # Trường hợp packet bắt đầu thẳng bằng IPv4
    if len(pkt) >= 20 and pkt[0] >> 4 == 4:
        ip = pkt

    # Trường hợp có Ethernet header
    elif len(pkt) >= 34 and pkt[12:14] == b"\x08\x00":
        ip = pkt[14:]

    else:
        continue

    ihl = (ip[0] & 0x0f) * 4

    # Chỉ lấy UDP
    if ip[9] != 17:
        continue

    udp = ip[ihl:]

    if len(udp) < 8:
        continue

    udp_len = struct.unpack("!H", udp[4:6])[0]
    udp_payload = udp[8:udp_len]

    # RTP header 12 bytes + audio payload 160 bytes
    if len(udp_payload) != 172:
        continue

    # RTP version 2
    if udp_payload[0] >> 6 != 2:
        continue

    # Payload type 0 = G.711 PCMU
    if (udp_payload[1] & 0x7f) != 0:
        continue

    audio = udp_payload[12:]

    if len(audio) == 160:
        payloads.append(audio)

    if len(payloads) == 5:
        break


for audio in payloads:
    bits = []

    # lấy LSB ở offset chẵn: 0, 2, 4, ..., 158
    for i in range(0, 160, 2):
        bits.append(audio[i] & 1)

    chunk = bytearray()

    # ghép bit MSB-first, 8 bit thành 1 byte
    for i in range(0, len(bits), 8):
        b = 0

        for bit in bits[i:i + 8]:
            b = (b << 1) | bit

        chunk.append(b)

    print(bytes(chunk).rstrip(b"\x00").decode(errors="replace"))
```

sau khi chạy xong, ta được 1 chuỗi base64 

<img width="841" height="165" alt="image" src="https://github.com/user-attachments/assets/0d55cc99-b595-44ac-bfe9-1c521c6a00ab" />

mang đi decode và ta được flag

---

## Flag 
```bash
tjctf{h3y_v0ip_s73g_is_4_7hing}
```









