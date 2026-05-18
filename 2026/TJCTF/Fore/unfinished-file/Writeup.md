# Đề bài 
<img width="971" height="249" alt="image" src="https://github.com/user-attachments/assets/36a2a178-0d33-4b58-b363-dbc97c84a114" />

Đề bài bảo ta thằng bạn nó đã tải 1 cái gì đáy trước khi shut down máy, và flow của ta sẽ là tìm xem nó đã tải cái gì về máy 

Bài cho ta 1 file .zip.crdownload, dùng file chỉ biết là dạng data 

Ta dùng strings để xem thử file vì file khá bé : 
```bash
strings -a secret_archive.zip.crdownload
```
Output :

```bash
CRDL
https://example.com/secret_archive.zip
xmB6(!6$9,q4q0
r6*'0
2qr2.'
6r7!*
!r/276'0?
readme.txtThis file is incomplete. Keep looking...
hidden/.flagdata6(!6$9,q4q0
r6*'0
2qr2.'
6r7!*
!r/276'0?PK
```
Tức là file .crdownload này không phải ZIP hoàn chỉnh. Nó có metadata tải xuống ở đầu file, rồi mới tới dữ liệu ZIP.

Bài này ta dùng zipdetails 
```bash
zipdetails --scan secret_archive.zip.crdownload
```
Output :
```bash
#
# INFO: Offset 0x0: found 0x100 (256) bytes before beginning of zipfile
#

0000 UNEXPECTED PADDING    CRDL....k.......&.https://example.com/secret_archive.zip...............xmB6(!6$9,q4q0..q6.r6*'0.2qr2.'.6r7!*.70.!r/276'0?............
                           ...........................................................................................................................

0100 LOCAL HEADER #1       04034B50 (67324752)
0104 Extract Zip Spec      14 (20) '2.0'
0105 Extract OS            00 (0) 'MS-DOS'
0106 General Purpose Flag  0000 (0)
0108 Compression Method    0000 (0) 'Stored'
010A Modification Time     00000000 (0) 'No Date/Time'
010E CRC                   6EB09ECE (1857068750)
0112 Compressed Size       00000029 (41)
0116 Uncompressed Size     00000029 (41)
011A Filename Length       000A (10)
011C Extra Length          0000 (0)
011E Filename              'readme.txt'
0128 PAYLOAD               This file is incomplete. Keep looking....

0151 LOCAL HEADER #2       04034B50 (67324752)
0155 Extract Zip Spec      14 (20) '2.0'
0156 Extract OS            00 (0) 'MS-DOS'
0157 General Purpose Flag  0000 (0)
0159 Compression Method    0000 (0) 'Stored'
015B Modification Time     00000000 (0) 'No Date/Time'
015F CRC                   CB2EE23D (3408847421)
0163 Compressed Size       0000002F (47)
0167 Uncompressed Size     0000002F (47)
016B Filename Length       0010 (16)
016D Extra Length          0000 (0)
016F Filename              'hidden/.flagdata'
017F PAYLOAD               6(!6$9,q4q0..q6.r6*'0.2qr2.'.6r7!*.70.!r/276'0?

01AE CENTRAL HEADER #1     02014B50 (33639248)
#
# FATAL: Offset 0x1B2: Unexpected zip file truncation while reading 'Central Directory Header'
#        Expected 0x2A (42) bytes, but only 0x1D (29) available .
#
```
Ta biết được file zip bắt đầu ở offset 100, hidden/.flagdata payload bắt đầu ở offset 0x17F và payload size: 0x2F = 47 bytes

Ta không thể dùng unzip cho bài này vì vẫn thiếu phần cuối của file 

Ta sẽ đi theo hướng carve file bằng dd sau khi biết được offset và byte :v 

payload
```bash
dd if=secret_archive.zip.crdownload of=flagdata.bin bs=1 skip=$((0x17f)) count=$((0x2f))
```
mở lên thì thấy toàn kí tự rác 

ta mở thẳng bằng xxd

<img width="787" height="118" alt="image" src="https://github.com/user-attachments/assets/52948822-799d-4161-a304-dc6455268ad5" />

Ta xác định xor key thông qua flag form là tjctf 
```bash
0x36 ^ 't' = 0x42
0x28 ^ 'j' = 0x42
0x21 ^ 'c' = 0x42
```
vậy key xor là 0x42

script:
```bash
data = open("flagdata.bin", "rb").read()
print(bytes(b ^ 0x42 for b in data).decode())
```
ta có được flag 

<img width="822" height="141" alt="image" src="https://github.com/user-attachments/assets/1195f50b-05f3-443e-976b-970f92af1f34" />

---
## Flag 

```bash
tjctf{n3v3r_l3t_0ther_p30ple_t0uch_ur_c0mputer}
```
