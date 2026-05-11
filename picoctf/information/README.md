# Information
Files can always be changed in a secret way. Can you find the flag?

---
```bash
 exiftool cat\ \(1\).jpg
```
### Output: 
```bash
┌──(chuatebongtoi2604㉿chuatebongtoi2604)-[/mnt/d/ctftraining/picoctf/fore/information]
└─$ exiftool cat\ \(1\).jpg
ExifTool Version Number         : 13.25
File Name                       : cat (1).jpg
Directory                       : .
File Size                       : 878 kB
File Modification Date/Time     : 2026:05:11 21:32:32+07:00
File Access Date/Time           : 2026:05:11 21:36:01+07:00
File Inode Change Date/Time     : 2026:05:11 21:36:00+07:00
File Permissions                : -rwxrwxrwx
File Type                       : JPEG
File Type Extension             : jpg
MIME Type                       : image/jpeg
JFIF Version                    : 1.02
Resolution Unit                 : None
X Resolution                    : 1
Y Resolution                    : 1
Current IPTC Digest             : 7a78f3d9cfb1ce42ab5a3aa30573d617
Copyright Notice                : PicoCTF
Application Record Version      : 4
XMP Toolkit                     : Image::ExifTool 10.80
License                         : cGljb0NURnt0aGVfbTN0YWRhdGFfMXNfbW9kaWZpZWR9
Rights                          : PicoCTF
Image Width                     : 2560
Image Height                    : 1598
Encoding Process                : Baseline DCT, Huffman coding
Bits Per Sample                 : 8
Color Components                : 3
Y Cb Cr Sub Sampling            : YCbCr4:2:0 (2 2)
Image Size                      : 2560x1598
Megapixels                      : 4.1
```
Decode chuỗi base64 từ license

Ta được flag 

## Flag 
```bash
picoCTF{the_m3tadata_1s_modified}
```
