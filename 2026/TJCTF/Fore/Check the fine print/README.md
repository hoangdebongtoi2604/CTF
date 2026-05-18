# Đề bài :

<img width="981" height="267" alt="image" src="https://github.com/user-attachments/assets/96ca716c-e63d-417e-85a5-5fbc3c227b90" />


Đề cho ta 1 file png, ta test thử với binwalk, ta sẽ thấy được 1 file zip với 248 ảnh bên trong
```bash
binwalk logo.png
```
Output:
```bash
┌──(chuatebongtoi2604㉿chuatebongtoi2604)-[/mnt/d/ctftraining/tjctf/fore/checkthefileprint]
└─$ binwalk logo.png

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
0             0x0             PNG image, 150 x 150, 8-bit/color RGBA, non-interlaced
41            0x29            Zlib compressed data, best compression
14276         0x37C4          Zip archive data, at least v2.0 to extract, compressed size: 92, uncompressed size: 92, name: 001.png
14405         0x3845          Zip archive data, at least v2.0 to extract, compressed size: 103, uncompressed size: 103, name: 002.png
14545         0x38D1          Zip archive data, at least v2.0 to extract, compressed size: 88, uncompressed size: 88, name: 003.png
14670         0x394E          Zip archive data, at least v2.0 to extract, compressed size: 101, uncompressed size: 101, name: 004.png
14808         0x39D8          Zip archive data, at least v2.0 to extract, compressed size: 95, uncompressed size: 95, name: 005.png
14940         0x3A5C          Zip archive data, at least v2.0 to extract, compressed size: 102, uncompressed size: 102, name: 006.png
15079         0x3AE7          Zip archive data, at least v2.0 to extract, compressed size: 96, uncompressed size: 96, name: 007.png
15212         0x3B6C          Zip archive data, at least v2.0 to extract, compressed size: 88, uncompressed size: 88, name: 008.png
15337         0x3BE9          Zip archive data, at least v2.0 to extract, compressed size: 102, uncompressed size: 102, name: 009.png
15476         0x3C74          Zip archive data, at least v2.0 to extract, compressed size: 115, uncompressed size: 115, name: 010.png
15628         0x3D0C          Zip archive data, at least v2.0 to extract, compressed size: 98, uncompressed size: 98, name: 011.png
15763         0x3D93          Zip archive data, at least v2.0 to extract, compressed size: 112, uncompressed size: 112, name: 012.png
15912         0x3E28          Zip archive data, at least v2.0 to extract, compressed size: 103, uncompressed size: 103, name: 013.png
16052         0x3EB4          Zip archive data, at least v2.0 to extract, compressed size: 108, uncompressed size: 108, name: 014.png
16197         0x3F45          Zip archive data, at least v2.0 to extract, compressed size: 103, uncompressed size: 103, name: 015.png
16337         0x3FD1          Zip archive data, at least v2.0 to extract, compressed size: 108, uncompressed size: 108, name: 016.png
16482         0x4062          Zip archive data, at least v2.0 to extract, compressed size: 107, uncompressed size: 107, name: 017.png
16626         0x40F2          Zip archive data, at least v2.0 to extract, compressed size: 105, uncompressed size: 105, name: 018.png
16768         0x4180          Zip archive data, at least v2.0 to extract, compressed size: 110, uncompressed size: 110, name: 019.png
16915         0x4213          Zip archive data, at least v2.0 to extract, compressed size: 119, uncompressed size: 119, name: 020.png
17071         0x42AF          Zip archive data, at least v2.0 to extract, compressed size: 111, uncompressed size: 111, name: 021.png
17219         0x4343          Zip archive data, at least v2.0 to extract, compressed size: 112, uncompressed size: 112, name: 022.png
17368         0x43D8          Zip archive data, at least v2.0 to extract, compressed size: 111, uncompressed size: 111, name: 023.png
17516         0x446C          Zip archive data, at least v2.0 to extract, compressed size: 113, uncompressed size: 113, name: 024.png
17666         0x4502          Zip archive data, at least v2.0 to extract, compressed size: 111, uncompressed size: 111, name: 025.png
17814         0x4596          Zip archive data, at least v2.0 to extract, compressed size: 118, uncompressed size: 118, name: 026.png
17969         0x4631          Zip archive data, at least v2.0 to extract, compressed size: 113, uncompressed size: 113, name: 027.png
18119         0x46C7          Zip archive data, at least v2.0 to extract, compressed size: 106, uncompressed size: 106, name: 028.png
18262         0x4756          Zip archive data, at least v2.0 to extract, compressed size: 111, uncompressed size: 111, name: 029.png
18410         0x47EA          Zip archive data, at least v2.0 to extract, compressed size: 109, uncompressed size: 109, name: 030.png
18556         0x487C          Zip archive data, at least v2.0 to extract, compressed size: 101, uncompressed size: 101, name: 031.png
18694         0x4906          Zip archive data, at least v2.0 to extract, compressed size: 114, uncompressed size: 114, name: 032.png
18845         0x499D          Zip archive data, at least v2.0 to extract, compressed size: 97, uncompressed size: 97, name: 033.png
18979         0x4A23          Zip archive data, at least v2.0 to extract, compressed size: 108, uncompressed size: 108, name: 034.png
19124         0x4AB4          Zip archive data, at least v2.0 to extract, compressed size: 105, uncompressed size: 105, name: 035.png
19266         0x4B42          Zip archive data, at least v2.0 to extract, compressed size: 107, uncompressed size: 107, name: 036.png
19410         0x4BD2          Zip archive data, at least v2.0 to extract, compressed size: 109, uncompressed size: 109, name: 037.png
19556         0x4C64          Zip archive data, at least v2.0 to extract, compressed size: 94, uncompressed size: 94, name: 038.png
19687         0x4CE7          Zip archive data, at least v2.0 to extract, compressed size: 108, uncompressed size: 108, name: 039.png
19832         0x4D78          Zip archive data, at least v2.0 to extract, compressed size: 118, uncompressed size: 118, name: 040.png
19987         0x4E13          Zip archive data, at least v2.0 to extract, compressed size: 107, uncompressed size: 107, name: 041.png
20131         0x4EA3          Zip archive data, at least v2.0 to extract, compressed size: 121, uncompressed size: 121, name: 042.png
20289         0x4F41          Zip archive data, at least v2.0 to extract, compressed size: 112, uncompressed size: 112, name: 043.png
20438         0x4FD6          Zip archive data, at least v2.0 to extract, compressed size: 116, uncompressed size: 116, name: 044.png
20591         0x506F          Zip archive data, at least v2.0 to extract, compressed size: 114, uncompressed size: 114, name: 045.png
20742         0x5106          Zip archive data, at least v2.0 to extract, compressed size: 118, uncompressed size: 118, name: 046.png
20897         0x51A1          Zip archive data, at least v2.0 to extract, compressed size: 113, uncompressed size: 113, name: 047.png
21047         0x5237          Zip archive data, at least v2.0 to extract, compressed size: 110, uncompressed size: 110, name: 048.png
21194         0x52CA          Zip archive data, at least v2.0 to extract, compressed size: 118, uncompressed size: 118, name: 049.png
21349         0x5365          Zip archive data, at least v2.0 to extract, compressed size: 112, uncompressed size: 112, name: 050.png
21498         0x53FA          Zip archive data, at least v2.0 to extract, compressed size: 103, uncompressed size: 103, name: 051.png
21638         0x5486          Zip archive data, at least v2.0 to extract, compressed size: 110, uncompressed size: 110, name: 052.png
21785         0x5519          Zip archive data, at least v2.0 to extract, compressed size: 106, uncompressed size: 106, name: 053.png
21928         0x55A8          Zip archive data, at least v2.0 to extract, compressed size: 109, uncompressed size: 109, name: 054.png
22074         0x563A          Zip archive data, at least v2.0 to extract, compressed size: 99, uncompressed size: 99, name: 055.png
22210         0x56C2          Zip archive data, at least v2.0 to extract, compressed size: 105, uncompressed size: 105, name: 056.png
22352         0x5750          Zip archive data, at least v2.0 to extract, compressed size: 106, uncompressed size: 106, name: 057.png
22495         0x57DF          Zip archive data, at least v2.0 to extract, compressed size: 101, uncompressed size: 101, name: 058.png
22633         0x5869          Zip archive data, at least v2.0 to extract, compressed size: 105, uncompressed size: 105, name: 059.png
22775         0x58F7          Zip archive data, at least v2.0 to extract, compressed size: 125, uncompressed size: 125, name: 060.png
22937         0x5999          Zip archive data, at least v2.0 to extract, compressed size: 107, uncompressed size: 107, name: 061.png
23081         0x5A29          Zip archive data, at least v2.0 to extract, compressed size: 119, uncompressed size: 119, name: 062.png
23237         0x5AC5          Zip archive data, at least v2.0 to extract, compressed size: 109, uncompressed size: 109, name: 063.png
23383         0x5B57          Zip archive data, at least v2.0 to extract, compressed size: 112, uncompressed size: 112, name: 064.png
23532         0x5BEC          Zip archive data, at least v2.0 to extract, compressed size: 108, uncompressed size: 108, name: 065.png
23677         0x5C7D          Zip archive data, at least v2.0 to extract, compressed size: 110, uncompressed size: 110, name: 066.png
23824         0x5D10          Zip archive data, at least v2.0 to extract, compressed size: 113, uncompressed size: 113, name: 067.png
23974         0x5DA6          Zip archive data, at least v2.0 to extract, compressed size: 111, uncompressed size: 111, name: 068.png
24122         0x5E3A          Zip archive data, at least v2.0 to extract, compressed size: 115, uncompressed size: 115, name: 069.png
24274         0x5ED2          Zip archive data, at least v2.0 to extract, compressed size: 111, uncompressed size: 111, name: 070.png
24422         0x5F66          Zip archive data, at least v2.0 to extract, compressed size: 105, uncompressed size: 105, name: 071.png
24564         0x5FF4          Zip archive data, at least v2.0 to extract, compressed size: 109, uncompressed size: 109, name: 072.png
24710         0x6086          Zip archive data, at least v2.0 to extract, compressed size: 105, uncompressed size: 105, name: 073.png
24852         0x6114          Zip archive data, at least v2.0 to extract, compressed size: 107, uncompressed size: 107, name: 074.png
24996         0x61A4          Zip archive data, at least v2.0 to extract, compressed size: 105, uncompressed size: 105, name: 075.png
25138         0x6232          Zip archive data, at least v2.0 to extract, compressed size: 107, uncompressed size: 107, name: 076.png
25282         0x62C2          Zip archive data, at least v2.0 to extract, compressed size: 99, uncompressed size: 99, name: 077.png
25418         0x634A          Zip archive data, at least v2.0 to extract, compressed size: 105, uncompressed size: 105, name: 078.png
25560         0x63D8          Zip archive data, at least v2.0 to extract, compressed size: 113, uncompressed size: 113, name: 079.png
25710         0x646E          Zip archive data, at least v2.0 to extract, compressed size: 108, uncompressed size: 108, name: 080.png
25855         0x64FF          Zip archive data, at least v2.0 to extract, compressed size: 102, uncompressed size: 102, name: 081.png
25994         0x658A          Zip archive data, at least v2.0 to extract, compressed size: 109, uncompressed size: 109, name: 082.png
26140         0x661C          Zip archive data, at least v2.0 to extract, compressed size: 98, uncompressed size: 98, name: 083.png
26275         0x66A3          Zip archive data, at least v2.0 to extract, compressed size: 109, uncompressed size: 109, name: 084.png
26421         0x6735          Zip archive data, at least v2.0 to extract, compressed size: 104, uncompressed size: 104, name: 085.png
26562         0x67C2          Zip archive data, at least v2.0 to extract, compressed size: 109, uncompressed size: 109, name: 086.png
26708         0x6854          Zip archive data, at least v2.0 to extract, compressed size: 109, uncompressed size: 109, name: 087.png
26854         0x68E6          Zip archive data, at least v2.0 to extract, compressed size: 89, uncompressed size: 89, name: 088.png
26980         0x6964          Zip archive data, at least v2.0 to extract, compressed size: 105, uncompressed size: 105, name: 089.png
27122         0x69F2          Zip archive data, at least v2.0 to extract, compressed size: 115, uncompressed size: 115, name: 090.png
27274         0x6A8A          Zip archive data, at least v2.0 to extract, compressed size: 109, uncompressed size: 109, name: 091.png
27420         0x6B1C          Zip archive data, at least v2.0 to extract, compressed size: 112, uncompressed size: 112, name: 092.png
27569         0x6BB1          Zip archive data, at least v2.0 to extract, compressed size: 109, uncompressed size: 109, name: 093.png
27715         0x6C43          Zip archive data, at least v2.0 to extract, compressed size: 112, uncompressed size: 112, name: 094.png
27864         0x6CD8          Zip archive data, at least v2.0 to extract, compressed size: 112, uncompressed size: 112, name: 095.png
28013         0x6D6D          Zip archive data, at least v2.0 to extract, compressed size: 114, uncompressed size: 114, name: 096.png
28164         0x6E04          Zip archive data, at least v2.0 to extract, compressed size: 113, uncompressed size: 113, name: 097.png
28314         0x6E9A          Zip archive data, at least v2.0 to extract, compressed size: 108, uncompressed size: 108, name: 098.png
28459         0x6F2B          Zip archive data, at least v2.0 to extract, compressed size: 110, uncompressed size: 110, name: 099.png
28606         0x6FBE          Zip archive data, at least v2.0 to extract, compressed size: 120, uncompressed size: 120, name: 100.png
28763         0x705B          Zip archive data, at least v2.0 to extract, compressed size: 112, uncompressed size: 112, name: 101.png
28912         0x70F0          Zip archive data, at least v2.0 to extract, compressed size: 124, uncompressed size: 124, name: 102.png
29073         0x7191          Zip archive data, at least v2.0 to extract, compressed size: 119, uncompressed size: 119, name: 103.png
29229         0x722D          Zip archive data, at least v2.0 to extract, compressed size: 123, uncompressed size: 123, name: 104.png
29389         0x72CD          Zip archive data, at least v2.0 to extract, compressed size: 123, uncompressed size: 123, name: 105.png
29549         0x736D          Zip archive data, at least v2.0 to extract, compressed size: 121, uncompressed size: 121, name: 106.png
29707         0x740B          Zip archive data, at least v2.0 to extract, compressed size: 123, uncompressed size: 123, name: 107.png
29867         0x74AB          Zip archive data, at least v2.0 to extract, compressed size: 116, uncompressed size: 116, name: 108.png
30020         0x7544          Zip archive data, at least v2.0 to extract, compressed size: 122, uncompressed size: 122, name: 109.png
30179         0x75E3          Zip archive data, at least v2.0 to extract, compressed size: 117, uncompressed size: 117, name: 110.png
30333         0x767D          Zip archive data, at least v2.0 to extract, compressed size: 101, uncompressed size: 101, name: 111.png
30471         0x7707          Zip archive data, at least v2.0 to extract, compressed size: 117, uncompressed size: 117, name: 112.png
30625         0x77A1          Zip archive data, at least v2.0 to extract, compressed size: 110, uncompressed size: 110, name: 113.png
30772         0x7834          Zip archive data, at least v2.0 to extract, compressed size: 115, uncompressed size: 115, name: 114.png
30924         0x78CC          Zip archive data, at least v2.0 to extract, compressed size: 109, uncompressed size: 109, name: 115.png
31070         0x795E          Zip archive data, at least v2.0 to extract, compressed size: 108, uncompressed size: 108, name: 116.png
31215         0x79EF          Zip archive data, at least v2.0 to extract, compressed size: 115, uncompressed size: 115, name: 117.png
31367         0x7A87          Zip archive data, at least v2.0 to extract, compressed size: 109, uncompressed size: 109, name: 118.png
31513         0x7B19          Zip archive data, at least v2.0 to extract, compressed size: 116, uncompressed size: 116, name: 119.png
31666         0x7BB2          Zip archive data, at least v2.0 to extract, compressed size: 123, uncompressed size: 123, name: 120.png
31826         0x7C52          Zip archive data, at least v2.0 to extract, compressed size: 120, uncompressed size: 120, name: 121.png
31983         0x7CEF          Zip archive data, at least v2.0 to extract, compressed size: 120, uncompressed size: 120, name: 122.png
32140         0x7D8C          Zip archive data, at least v2.0 to extract, compressed size: 119, uncompressed size: 119, name: 123.png
32296         0x7E28          Zip archive data, at least v2.0 to extract, compressed size: 122, uncompressed size: 122, name: 124.png
32455         0x7EC7          Zip archive data, at least v2.0 to extract, compressed size: 115, uncompressed size: 115, name: 125.png
32607         0x7F5F          Zip archive data, at least v2.0 to extract, compressed size: 121, uncompressed size: 121, name: 126.png
32765         0x7FFD          Zip archive data, at least v2.0 to extract, compressed size: 117, uncompressed size: 117, name: 127.png
32919         0x8097          Zip archive data, at least v2.0 to extract, compressed size: 115, uncompressed size: 115, name: 128.png
33071         0x812F          Zip archive data, at least v2.0 to extract, compressed size: 118, uncompressed size: 118, name: 129.png
33226         0x81CA          Zip archive data, at least v2.0 to extract, compressed size: 118, uncompressed size: 118, name: 130.png
33381         0x8265          Zip archive data, at least v2.0 to extract, compressed size: 114, uncompressed size: 114, name: 131.png
33532         0x82FC          Zip archive data, at least v2.0 to extract, compressed size: 123, uncompressed size: 123, name: 132.png
33692         0x839C          Zip archive data, at least v2.0 to extract, compressed size: 107, uncompressed size: 107, name: 133.png
33836         0x842C          Zip archive data, at least v2.0 to extract, compressed size: 118, uncompressed size: 118, name: 134.png
33991         0x84C7          Zip archive data, at least v2.0 to extract, compressed size: 110, uncompressed size: 110, name: 135.png
34138         0x855A          Zip archive data, at least v2.0 to extract, compressed size: 118, uncompressed size: 118, name: 136.png
34293         0x85F5          Zip archive data, at least v2.0 to extract, compressed size: 118, uncompressed size: 118, name: 137.png
34448         0x8690          Zip archive data, at least v2.0 to extract, compressed size: 108, uncompressed size: 108, name: 138.png
34593         0x8721          Zip archive data, at least v2.0 to extract, compressed size: 117, uncompressed size: 117, name: 139.png
34747         0x87BB          Zip archive data, at least v2.0 to extract, compressed size: 127, uncompressed size: 127, name: 140.png
34911         0x885F          Zip archive data, at least v2.0 to extract, compressed size: 119, uncompressed size: 119, name: 141.png
35067         0x88FB          Zip archive data, at least v2.0 to extract, compressed size: 126, uncompressed size: 126, name: 142.png
35230         0x899E          Zip archive data, at least v2.0 to extract, compressed size: 121, uncompressed size: 121, name: 143.png
35388         0x8A3C          Zip archive data, at least v2.0 to extract, compressed size: 122, uncompressed size: 122, name: 144.png
35547         0x8ADB          Zip archive data, at least v2.0 to extract, compressed size: 120, uncompressed size: 120, name: 145.png
35704         0x8B78          Zip archive data, at least v2.0 to extract, compressed size: 123, uncompressed size: 123, name: 146.png
35864         0x8C18          Zip archive data, at least v2.0 to extract, compressed size: 123, uncompressed size: 123, name: 147.png
36024         0x8CB8          Zip archive data, at least v2.0 to extract, compressed size: 120, uncompressed size: 120, name: 148.png
36181         0x8D55          Zip archive data, at least v2.0 to extract, compressed size: 123, uncompressed size: 123, name: 149.png
36341         0x8DF5          Zip archive data, at least v2.0 to extract, compressed size: 123, uncompressed size: 123, name: 150.png
36501         0x8E95          Zip archive data, at least v2.0 to extract, compressed size: 113, uncompressed size: 113, name: 151.png
36651         0x8F2B          Zip archive data, at least v2.0 to extract, compressed size: 119, uncompressed size: 119, name: 152.png
36807         0x8FC7          Zip archive data, at least v2.0 to extract, compressed size: 117, uncompressed size: 117, name: 153.png
36961         0x9061          Zip archive data, at least v2.0 to extract, compressed size: 124, uncompressed size: 124, name: 154.png
37122         0x9102          Zip archive data, at least v2.0 to extract, compressed size: 108, uncompressed size: 108, name: 155.png
37267         0x9193          Zip archive data, at least v2.0 to extract, compressed size: 114, uncompressed size: 114, name: 156.png
37418         0x922A          Zip archive data, at least v2.0 to extract, compressed size: 115, uncompressed size: 115, name: 157.png
37570         0x92C2          Zip archive data, at least v2.0 to extract, compressed size: 113, uncompressed size: 113, name: 158.png
37720         0x9358          Zip archive data, at least v2.0 to extract, compressed size: 115, uncompressed size: 115, name: 159.png
37872         0x93F0          Zip archive data, at least v2.0 to extract, compressed size: 124, uncompressed size: 124, name: 160.png
38033         0x9491          Zip archive data, at least v2.0 to extract, compressed size: 112, uncompressed size: 112, name: 161.png
38182         0x9526          Zip archive data, at least v2.0 to extract, compressed size: 123, uncompressed size: 123, name: 162.png
38342         0x95C6          Zip archive data, at least v2.0 to extract, compressed size: 115, uncompressed size: 115, name: 163.png
38494         0x965E          Zip archive data, at least v2.0 to extract, compressed size: 123, uncompressed size: 123, name: 164.png
38654         0x96FE          Zip archive data, at least v2.0 to extract, compressed size: 116, uncompressed size: 116, name: 165.png
38807         0x9797          Zip archive data, at least v2.0 to extract, compressed size: 113, uncompressed size: 113, name: 166.png
38957         0x982D          Zip archive data, at least v2.0 to extract, compressed size: 118, uncompressed size: 118, name: 167.png
39112         0x98C8          Zip archive data, at least v2.0 to extract, compressed size: 117, uncompressed size: 117, name: 168.png
39266         0x9962          Zip archive data, at least v2.0 to extract, compressed size: 117, uncompressed size: 117, name: 169.png
39420         0x99FC          Zip archive data, at least v2.0 to extract, compressed size: 123, uncompressed size: 123, name: 170.png
39580         0x9A9C          Zip archive data, at least v2.0 to extract, compressed size: 111, uncompressed size: 111, name: 171.png
39728         0x9B30          Zip archive data, at least v2.0 to extract, compressed size: 121, uncompressed size: 121, name: 172.png
39886         0x9BCE          Zip archive data, at least v2.0 to extract, compressed size: 118, uncompressed size: 118, name: 173.png
40041         0x9C69          Zip archive data, at least v2.0 to extract, compressed size: 117, uncompressed size: 117, name: 174.png
40195         0x9D03          Zip archive data, at least v2.0 to extract, compressed size: 112, uncompressed size: 112, name: 175.png
40344         0x9D98          Zip archive data, at least v2.0 to extract, compressed size: 115, uncompressed size: 115, name: 176.png
40496         0x9E30          Zip archive data, at least v2.0 to extract, compressed size: 109, uncompressed size: 109, name: 177.png
40642         0x9EC2          Zip archive data, at least v2.0 to extract, compressed size: 118, uncompressed size: 118, name: 178.png
40797         0x9F5D          Zip archive data, at least v2.0 to extract, compressed size: 124, uncompressed size: 124, name: 179.png
40958         0x9FFE          Zip archive data, at least v2.0 to extract, compressed size: 117, uncompressed size: 117, name: 180.png
41112         0xA098          Zip archive data, at least v2.0 to extract, compressed size: 108, uncompressed size: 108, name: 181.png
41257         0xA129          Zip archive data, at least v2.0 to extract, compressed size: 120, uncompressed size: 120, name: 182.png
41414         0xA1C6          Zip archive data, at least v2.0 to extract, compressed size: 111, uncompressed size: 111, name: 183.png
41562         0xA25A          Zip archive data, at least v2.0 to extract, compressed size: 118, uncompressed size: 118, name: 184.png
41717         0xA2F5          Zip archive data, at least v2.0 to extract, compressed size: 111, uncompressed size: 111, name: 185.png
41865         0xA389          Zip archive data, at least v2.0 to extract, compressed size: 114, uncompressed size: 114, name: 186.png
42016         0xA420          Zip archive data, at least v2.0 to extract, compressed size: 115, uncompressed size: 115, name: 187.png
42168         0xA4B8          Zip archive data, at least v2.0 to extract, compressed size: 107, uncompressed size: 107, name: 188.png
42312         0xA548          Zip archive data, at least v2.0 to extract, compressed size: 113, uncompressed size: 113, name: 189.png
42462         0xA5DE          Zip archive data, at least v2.0 to extract, compressed size: 126, uncompressed size: 126, name: 190.png
42625         0xA681          Zip archive data, at least v2.0 to extract, compressed size: 115, uncompressed size: 115, name: 191.png
42777         0xA719          Zip archive data, at least v2.0 to extract, compressed size: 123, uncompressed size: 123, name: 192.png
42937         0xA7B9          Zip archive data, at least v2.0 to extract, compressed size: 117, uncompressed size: 117, name: 193.png
43091         0xA853          Zip archive data, at least v2.0 to extract, compressed size: 123, uncompressed size: 123, name: 194.png
43251         0xA8F3          Zip archive data, at least v2.0 to extract, compressed size: 118, uncompressed size: 118, name: 195.png
43406         0xA98E          Zip archive data, at least v2.0 to extract, compressed size: 123, uncompressed size: 123, name: 196.png
43566         0xAA2E          Zip archive data, at least v2.0 to extract, compressed size: 119, uncompressed size: 119, name: 197.png
43722         0xAACA          Zip archive data, at least v2.0 to extract, compressed size: 116, uncompressed size: 116, name: 198.png
43875         0xAB63          Zip archive data, at least v2.0 to extract, compressed size: 123, uncompressed size: 123, name: 199.png
44035         0xAC03          Zip archive data, at least v2.0 to extract, compressed size: 121, uncompressed size: 121, name: 200.png
44193         0xACA1          Zip archive data, at least v2.0 to extract, compressed size: 126, uncompressed size: 126, name: 201.png
44356         0xAD44          Zip archive data, at least v2.0 to extract, compressed size: 128, uncompressed size: 128, name: 202.png
44521         0xADE9          Zip archive data, at least v2.0 to extract, compressed size: 125, uncompressed size: 125, name: 203.png
44683         0xAE8B          Zip archive data, at least v2.0 to extract, compressed size: 129, uncompressed size: 129, name: 204.png
44849         0xAF31          Zip archive data, at least v2.0 to extract, compressed size: 127, uncompressed size: 127, name: 205.png
45013         0xAFD5          Zip archive data, at least v2.0 to extract, compressed size: 128, uncompressed size: 128, name: 206.png
45178         0xB07A          Zip archive data, at least v2.0 to extract, compressed size: 127, uncompressed size: 127, name: 207.png
45342         0xB11E          Zip archive data, at least v2.0 to extract, compressed size: 121, uncompressed size: 121, name: 208.png
45500         0xB1BC          Zip archive data, at least v2.0 to extract, compressed size: 126, uncompressed size: 126, name: 209.png
45663         0xB25F          Zip archive data, at least v2.0 to extract, compressed size: 128, uncompressed size: 128, name: 210.png
45828         0xB304          Zip archive data, at least v2.0 to extract, compressed size: 121, uncompressed size: 121, name: 211.png
45986         0xB3A2          Zip archive data, at least v2.0 to extract, compressed size: 126, uncompressed size: 126, name: 212.png
46149         0xB445          Zip archive data, at least v2.0 to extract, compressed size: 120, uncompressed size: 120, name: 213.png
46306         0xB4E2          Zip archive data, at least v2.0 to extract, compressed size: 128, uncompressed size: 128, name: 214.png
46471         0xB587          Zip archive data, at least v2.0 to extract, compressed size: 122, uncompressed size: 122, name: 215.png
46630         0xB626          Zip archive data, at least v2.0 to extract, compressed size: 123, uncompressed size: 123, name: 216.png
46790         0xB6C6          Zip archive data, at least v2.0 to extract, compressed size: 121, uncompressed size: 121, name: 217.png
46948         0xB764          Zip archive data, at least v2.0 to extract, compressed size: 116, uncompressed size: 116, name: 218.png
47101         0xB7FD          Zip archive data, at least v2.0 to extract, compressed size: 123, uncompressed size: 123, name: 219.png
47261         0xB89D          Zip archive data, at least v2.0 to extract, compressed size: 125, uncompressed size: 125, name: 220.png
47423         0xB93F          Zip archive data, at least v2.0 to extract, compressed size: 123, uncompressed size: 123, name: 221.png
47583         0xB9DF          Zip archive data, at least v2.0 to extract, compressed size: 115, uncompressed size: 115, name: 222.png
47735         0xBA77          Zip archive data, at least v2.0 to extract, compressed size: 118, uncompressed size: 118, name: 223.png
47890         0xBB12          Zip archive data, at least v2.0 to extract, compressed size: 125, uncompressed size: 125, name: 224.png
48052         0xBBB4          Zip archive data, at least v2.0 to extract, compressed size: 119, uncompressed size: 119, name: 225.png
48208         0xBC50          Zip archive data, at least v2.0 to extract, compressed size: 125, uncompressed size: 125, name: 226.png
48370         0xBCF2          Zip archive data, at least v2.0 to extract, compressed size: 119, uncompressed size: 119, name: 227.png
48526         0xBD8E          Zip archive data, at least v2.0 to extract, compressed size: 115, uncompressed size: 115, name: 228.png
48678         0xBE26          Zip archive data, at least v2.0 to extract, compressed size: 120, uncompressed size: 120, name: 229.png
48835         0xBEC3          Zip archive data, at least v2.0 to extract, compressed size: 122, uncompressed size: 122, name: 230.png
48994         0xBF62          Zip archive data, at least v2.0 to extract, compressed size: 123, uncompressed size: 123, name: 231.png
49154         0xC002          Zip archive data, at least v2.0 to extract, compressed size: 128, uncompressed size: 128, name: 232.png
49319         0xC0A7          Zip archive data, at least v2.0 to extract, compressed size: 114, uncompressed size: 114, name: 233.png
49470         0xC13E          Zip archive data, at least v2.0 to extract, compressed size: 125, uncompressed size: 125, name: 234.png
49632         0xC1E0          Zip archive data, at least v2.0 to extract, compressed size: 118, uncompressed size: 118, name: 235.png
49787         0xC27B          Zip archive data, at least v2.0 to extract, compressed size: 123, uncompressed size: 123, name: 236.png
49947         0xC31B          Zip archive data, at least v2.0 to extract, compressed size: 119, uncompressed size: 119, name: 237.png
50103         0xC3B7          Zip archive data, at least v2.0 to extract, compressed size: 116, uncompressed size: 116, name: 238.png
50256         0xC450          Zip archive data, at least v2.0 to extract, compressed size: 121, uncompressed size: 121, name: 239.png
50414         0xC4EE          Zip archive data, at least v2.0 to extract, compressed size: 128, uncompressed size: 128, name: 240.png
50579         0xC593          Zip archive data, at least v2.0 to extract, compressed size: 118, uncompressed size: 118, name: 241.png
50734         0xC62E          Zip archive data, at least v2.0 to extract, compressed size: 126, uncompressed size: 126, name: 242.png
50897         0xC6D1          Zip archive data, at least v2.0 to extract, compressed size: 121, uncompressed size: 121, name: 243.png
51055         0xC76F          Zip archive data, at least v2.0 to extract, compressed size: 119, uncompressed size: 119, name: 244.png
51211         0xC80B          Zip archive data, at least v2.0 to extract, compressed size: 121, uncompressed size: 121, name: 245.png
51369         0xC8A9          Zip archive data, at least v2.0 to extract, compressed size: 125, uncompressed size: 125, name: 246.png
51531         0xC94B          Zip archive data, at least v2.0 to extract, compressed size: 123, uncompressed size: 123, name: 247.png
51691         0xC9EB          Zip archive data, at least v2.0 to extract, compressed size: 123, uncompressed size: 123, name: 248.png
64995         0xFDE3          End of Zip archive, footer length: 22
```

---
Sau đấy ta extract file zip này ra bằng binwalk, hoặc có thể copy toàn bộ byte đằng sau IEND của bức ảnh, lưu thành 1 file zip r giải nén để lấy 248 bức ảnh 

Ta mở từng ảnh để xem byte. 

Sau khi soi kĩ thì ta nhận ra các bức ảnh chỉ lệch nhau đúng 1 byte tại offset 0x10A 

IDHR của png có cấu trúc 
```bash
width
height
bit depth
color type
compression method
filter method
interlace method
```
IHDR của ảnh 1 : 
```bash
49 48 44 52 00 00 00 13 00 00 00 09 08 02 00 00 00
```
<img width="680" height="356" alt="image" src="https://github.com/user-attachments/assets/9314b36f-456a-46a9-bd0e-f54084924e93" />
IHDR của ảnh 2: 
```bash
49 48 44 52 00 00 00 13 00 00 00 09 08 02 01 00 00
```
Chỉ khác 1 byte, và các ảnh sau cũng như vậy. chỉ là 0 và 1 

Byte sau 08 02 chính là compression method.

Vậy mỗi file png nhỏ đang giấu 1 bit 
```
compression method = 0 -> bit 0
compression method = 1 -> bit 1
```
Ghép bit theo thứ tự file

Đọc lần lượt từ:
```bash
001.png -> 248.png
```
Lấy byte compression method của từng file.

8 bit đầu:
```bash
01110100
```
Đổi sang ASCII:
```bash
01110100 = 0x74 = t
```
8 bit tiếp theo:
```bash
01101010
```
Đổi sang ASCII:

01101010 = 0x6a = j

Ta bắt đầu thấy được flag format dạng tjctf{....}

Script giải :
```bash
from pathlib import Path

folder = Path(".")
pngs = sorted(folder.glob("*.png"))

bits = []

for p in pngs:
    data = p.read_bytes()

    # Check PNG signature
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        continue

    # PNG layout:
    # 0x00 - 0x07: PNG signature
    # 0x08 - 0x0B: IHDR length
    # 0x0C - 0x0F: chunk type = IHDR
    # 0x10 ...     : IHDR data
    #
    # IHDR data:
    # width 4 bytes
    # height 4 bytes
    # bit depth 1 byte
    # color type 1 byte
    # compression method 1 byte  <-- offset 0x1A toàn file

    if data[12:16] != b"IHDR":
        print(f"[!] {p.name}: first chunk is not IHDR")
        continue

    compression_method = data[0x1A]

    if compression_method not in (0, 1):
        print(f"[!] {p.name}: strange bit = {compression_method}")

    bits.append(str(compression_method))

bitstream = "".join(bits)

print("[+] PNG files:", len(pngs))
print("[+] Bits:", len(bitstream))
print("[+] First 32 bits:", bitstream[:32])

out = ""

for i in range(0, len(bitstream), 8):
    byte = bitstream[i:i+8]
    if len(byte) < 8:
        break
    out += chr(int(byte, 2))

print("[+] Decoded:")
print(out)
```
flag ra được sau 32 bits:

---
## Flag 
```bash
tjctf{wow_you_actually_read_it}
```











