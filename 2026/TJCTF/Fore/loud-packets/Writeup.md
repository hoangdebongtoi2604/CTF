# Đề bài 
<img width="995" height="354" alt="image" src="https://github.com/user-attachments/assets/a1bc1666-063b-4073-b05f-698f5db839ed" />

đề bài nói tên này đang chuyển 1 vài dữ liệu qua bluetooth và có ai đó đã lấy được nó

Ta mở file pcap bằng wireshark 

Ta thấy được giao thức chính là UDP, cùng với rất nhiều địa chỉ ip khác nhau 

Ta vào conversations để xem các ip đã giao tiếp, xếp theo số lượng packet.

<img width="1409" height="764" alt="image" src="https://github.com/user-attachments/assets/1b59b8db-0672-4d12-997d-1982605e56b1" />

Ở đây thấy một conversation nổi bật:

192.168.1.100:50000 → 192.168.1.200:62000

Luồng này có rất nhiều packet, trong khi các luồng khác chỉ là các UDP packet lẻ. Vì vậy đây là luồng khá sú 

Ta áp filter 
```bash
udp && ip.src == 192.168.1.100 && ip.dst == 192.168.1.200
```
Click vào 1 vài packet, ta thấy được magic header cố định là BTAV

<img width="1584" height="952" alt="image" src="https://github.com/user-attachments/assets/a89d6baa-4e4a-4bf9-ab60-c948410f8a4c" />

Ví dụ một packet:

42 54 41 56 00 00 00 ae ...

Tách ra:

42 54 41 56 = BTAV
00 00 00 ae = giá trị thay đổi

Packet khác:

42 54 41 56 00 00 00 98 ...

Tách ra:

42 54 41 56 = BTAV
00 00 00 98 = giá trị thay đổi

Ví dụ trong capture order:

packet đầu:  00 00 00 ae = 174
packet sau:  00 00 00 98 = 152
packet sau:  00 00 01 66 = 358

<img width="1605" height="935" alt="image" src="https://github.com/user-attachments/assets/68a454b4-0318-400a-b597-fdcf2f59224b" />

<img width="1572" height="877" alt="image" src="https://github.com/user-attachments/assets/36a156cc-d87c-458e-bc7c-90453177a2fc" />

Luồng có header BTAV lặp lại, nhưng thứ tự packet trong capture có dấu hiệu không đúng thứ tự cho lám 

Ta thêm cột hiển thị payload để nhìn được pattern.

```bash
Edit -> Preferences -> Appearance -> Columns
Title: Payload
Type: Custom
Fields: data.data
```

Cột payload trở thành như sau, sort theo tăng dần 

<img width="1864" height="935" alt="image" src="https://github.com/user-attachments/assets/0a41be24-56eb-4805-8f02-a07c05ca815a" />

Sau khi sort, nhìn phần đầu danh sách sẽ thấy:

42:54:41:56:00:00:00:00:...
42:54:41:56:00:00:00:01:...
42:54:41:56:00:00:00:02:...
42:54:41:56:00:00:00:03:...

Nhìn phần cuối danh sách sẽ thấy:

42:54:41:56:00:00:01:c7:...
42:54:41:56:00:00:01:c8:...
42:54:41:56:00:00:01:c9:...
42:54:41:56:00:00:01:ca:...

0x1ca đổi sang decimal là:

458

Wireshark cũng cho biết có tổng cộng:

459 displayed packets

Vậy các giá trị sau BTAV chạy từ 0 -> 458

Số lượng giá trị trong khoảng này là:

458 - 0 + 1 = 459

Vậy tác giả có thể đã giấu gì đó theo thứ tự tăng dần này 

Xác định cấu trúc chunk

format mỗi UDP payload được xác định là:

offset 0–3 : 42 54 41 56    = "BTAV"
offset 4–7 : sequence number
offset 8+  : dữ liệu thật của file

Vậy muốn khôi phục file thì không lấy nguyên UDP payload, mà phải:

- Sắp xếp packet theo sequence number.
- Bỏ 8 byte đầu mỗi packet.
- Nối phần dữ liệu còn lại.

Từ đây ta có thể export dữ liệu bằng tshark
```bash
tshark -r chall.pcap \
  -Y 'ip.src == 192.168.1.100 && ip.dst == 192.168.1.200 && udp.srcport == 50000 && udp.dstport == 62000' \
  -T fields -e data.data \
| sed 's/://g' \
| sort \
| cut -c17- \
| xxd -r -p > recovered.bin
```
dùng lệnh file thì ta biết đây là 1 file wav 

<img width="841" height="202" alt="image" src="https://github.com/user-attachments/assets/a6136af0-2371-4707-9c02-650e1ba3d81a" />

Vậy ta chuyển đuôi thành wav 

Nghe thử thì thấy khá nhiều tiếng lạ 

Mở file bằng audacity để soi thử phổ và ta có flag 

<img width="1916" height="862" alt="image" src="https://github.com/user-attachments/assets/12c12403-dd92-4ba8-8deb-0230368d991e" />

---
## Flag 
```bash
tjctf{v3ry_l0ud_pc4p_f1le}
```
