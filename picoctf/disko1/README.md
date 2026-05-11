# Disko 1
Nếu làm bài này theo strings và grep thì quá ez, chúng ta sẽ làm theo hướng khác đi 1 chút, nhưng mình vẫn sẽ để lệnh strings ở đây
```bash
strings disko-1.dd | grep "pico"
```
trước hết ta xác định loại file system nào 
```bash
file disko-1.dd
disko-1.dd: DOS/MBR boot sector, code offset 0x58+2, OEM-ID "mkfs.fat", Media descriptor 0xf8, sectors/track 32, heads 8, sectors 102400 (volumes > 32 MB), FAT (32 bit), sectors/FAT 788, serial number 0x241a4420, unlabeled
```
Ta xác dịnh đây là FAT32 

FAT32 là một loại filesystem.

Filesystem là “cách ổ đĩa sắp xếp và quản lý file”

---

Tìm hiểu về FAT32: 

## FAT32 gồm những phần chính nào?

Một FAT32 image thường có 4 vùng quan trọng:

```bash
[ Boot Sector ][ FAT Table ][ Directory Entries ][ Data Area ]
```
### Boot Sector

Boot sector là vùng đầu filesystem, chứa thông tin cấu hình.

Nó cho biết:

```bash
mỗi sector bao nhiêu byte
mỗi cluster gồm bao nhiêu sector
FAT table bắt đầu ở đâu
Data area bắt đầu ở đâu
root directory nằm ở cluster nào
```
### 2. Cluster

Cluster là đơn vị cấp phát dữ liệu của filesystem.

Hệ điều hành không cấp phát từng byte một. Nó cấp phát theo từng cụm gọi là cluster.

Ví dụ:
```bash
Cluster size = 512 bytes

Một file dù chỉ có 10 bytes thì vẫn phải chiếm ít nhất 1 cluster:

File thật:       10 bytes
Disk cấp phát:  512 bytes
Dư:             502 bytes
```
Phần dư đó chính là file slack.

### FAT Table

FAT là viết tắt của:

File Allocation Table

Nó là cái bảng nói rằng:
```bash
File này dùng cluster nào
cluster này nối sang cluster nào
cluster nào đã dùng
cluster nào còn trống
```
Ví dụ một file có cluster chain:
```bash
56553 → 56554 → 56555 → 56556
```
Nghĩa là file đó không chỉ nằm ở một chỗ, mà dữ liệu file được nối qua nhiều cluster.

Hệ điều hành đọc file bằng cách:
```bash
đọc directory entry
→ biết cluster bắt đầu
→ nhìn FAT table
→ lần theo chuỗi cluster
→ ghép dữ liệu lại thành file
```
### Directory Entry

Directory entry là bản ghi mô tả một file/thư mục.

Nó chứa:
```bash
tên file
đuôi file
thuộc tính file
file size
cluster bắt đầu
thời gian tạo/sửa
```
Ví dụ directory entry nói:
```bash
File name      = kali-treecd
Path           = /bin/kali-treecd
Start cluster  = 56553
File size      = 1832 bytes
```
Từ đây hệ điều hành biết:

File /bin/kali-treecd bắt đầu ở cluster 56553
File dài 1832 bytes

Sau đó nó hỏi FAT table:
```bash
56553 nối tới đâu?
→ 56554
56554 nối tới đâu?
→ 56555
56555 nối tới đâu?
→ 56556
56556 là cluster cuối
```
Vậy file này chiếm:
```bash
56553 → 56554 → 56555 → 56556
```
### Data Area

Data area là vùng thật sự chứa nội dung file.

Directory entry chỉ là “bản ghi quản lý”.

FAT table chỉ là “bảng nối cluster”.

Còn dữ liệu file thật nằm trong Data Area.

## Xem thông tin các file bằng fls
```bash
fls -rp disko-1.dd
```
-r  : recursive, đi sâu vào thư mục con
-p  : hiện full path

## Kiểm tra deleted files
```bash
fls -rdp disko-1.dd
```
Tìm file đã xóa nhưng directory entry vẫn còn.
## Kiểm tra unallocated space bằng blkls
```bash
blkls disko-1.dd | strings -a -n 8
```
Dump vùng unallocated space rồi lọc chuỗi đọc được.

## Kiểm tra file slack toàn filesystem
```bash
blkls -s disko-1.dd | strings -a -n 8
```
output ra flag, vậy flag bài này nhét trong phần file slack
## Flag
```bash
picoCTF{1t5_ju5t_4_5tr1n9_be6031da}
```
