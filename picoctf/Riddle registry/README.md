# Riddle registry
### Đề bài :
Hi, intrepid investigator! 📄🔍 You've stumbled upon a peculiar PDF filled with what seems like nothing more than garbled nonsense. But beware! Not everything is as it appears. Amidst the chaos lies a hidden treasure—an elusive flag waiting to be uncovered.

Find the PDF file here Hidden Confidential Document and uncover the flag within the metadata.

PDF: 
![pdf](assets/confidential.pdf)

Ta dùn exiftool thử check metadata: 
```bash
exiftool confidental.pdf
```
Ta được kết quả 
```bash
ExifTool Version Number         : 13.25
File Name                       : confidential.pdf
Directory                       : .
File Size                       : 183 kB
File Modification Date/Time     : 2026:05:11 15:05:08+07:00
File Access Date/Time           : 2026:05:11 15:06:39+07:00
File Inode Change Date/Time     : 2026:05:11 15:07:08+07:00
File Permissions                : -rwxrwxrwx
File Type                       : PDF
File Type Extension             : pdf
MIME Type                       : application/pdf
PDF Version                     : 1.7
Linearized                      : No
Page Count                      : 1
Producer                        : PyPDF2
Author                          : cGljb0NURntwdXp6bDNkX20zdGFkYXRhX2YwdW5kIV9jOTk5ZTJhNH0=
```
Thấy được 1 dòng base64 trên mục author:
```bash
cGljb0NURntwdXp6bDNkX20zdGFkYXRhX2YwdW5kIV9jOTk5ZTJhNH0=
```
đem đi decode trên [kt.gy](kt.gy)
### Flag: 
```bash
picoCTF{puzzl3d_m3tadata_f0und!_c999e2a4}
```
