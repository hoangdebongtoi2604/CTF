# Red
RED, RED, RED, RED

Đề đưa ta 1 file ảnh cho có màu đỏ 
ta check metadata 

```bash
ExifTool Version Number         : 13.25
File Name                       : red.png
Directory                       : .
File Size                       : 796 bytes
File Modification Date/Time     : 2026:05:11 18:34:09+07:00
File Access Date/Time           : 2026:05:11 18:47:58+07:00
File Inode Change Date/Time     : 2026:05:11 18:47:58+07:00
File Permissions                : -rwxrwxrwx
File Type                       : PNG
File Type Extension             : png
MIME Type                       : image/png
Image Width                     : 128
Image Height                    : 128
Bit Depth                       : 8
Color Type                      : RGB with Alpha
Compression                     : Deflate/Inflate
Filter                          : Adaptive
Interlace                       : Noninterlaced
Poem                            : Crimson heart, vibrant and bold,.Hearts flutter at your sight..Evenings glow softly red,.Cherries burst with sweet life..Kisses linger with your warmth..Love deep as merlot..Scarlet leaves falling softly,.Bold in every stroke.
Image Size                      : 128x128
Megapixels                      : 0.016
```
Ta thấy 1 dòng thư được thêm vào trong ảnh png 

Ta thử láy các chữ đầu viét hoa, ghép lại ta được 

CHECKLSB

Như vậy ta sẽ check các kênh LSB của nó 

Ta thử trước bằng zsteg

```bash
zsteg red.png
```
Output: 
```bash
meta Poem           .. text: "Crimson heart, vibrant and bold,\nHearts flutter at your sight.\nEvenings glow softly red,\nCherries burst with sweet life.\nKisses linger with your warmth.\nLove deep as merlot.\nScarlet leaves falling softly,\nBold in every stroke."
b1,rgba,lsb,xy      .. text: "cGljb0NURntyM2RfMXNfdGgzX3VsdDFtNHQzX2N1cjNfZjByXzU0ZG4zNTVffQ==cGljb0NURntyM2RfMXNfdGgzX3VsdDFtNHQzX2N1cjNfZjByXzU0ZG4zNTVffQ==cGljb0NURntyM2RfMXNfdGgzX3VsdDFtNHQzX2N1cjNfZjByXzU0ZG4zNTVffQ==cGljb0NURntyM2RfMXNfdGgzX3VsdDFtNHQzX2N1cjNfZjByXzU0ZG4zNTVffQ=="
b1,rgba,msb,xy      .. file: OpenPGP Public Key
b2,g,lsb,xy         .. text: "ET@UETPETUUT@TUUTD@PDUDDDPE"
b2,rgb,lsb,xy       .. file: OpenPGP Secret Key
b2,bgr,msb,xy       .. file: OpenPGP Public Key
b2,rgba,lsb,xy      .. file: OpenPGP Secret Key
b2,rgba,msb,xy      .. text: "CIkiiiII"
b2,abgr,lsb,xy      .. file: OpenPGP Secret Key
b2,abgr,msb,xy      .. text: "iiiaakikk"
b3,rgba,msb,xy      .. text: "#wb#wp#7p"
b3,abgr,msb,xy      .. text: "7r'wb#7p"
b4,b,lsb,xy         .. file: 0421 Alliant compact executable not stripped
```
ta thấy 1 kênh được nhét text: 
ta lấy chuỗi base64 đi decode, ta sẽ được flag 

## Flag 
```bash
picoCTF{r3d_1s_th3_ult1m4t3_cur3_f0r_54dn355_}
```

