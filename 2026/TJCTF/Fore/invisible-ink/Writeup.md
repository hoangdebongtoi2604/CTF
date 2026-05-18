# Đề bài 
<img width="945" height="248" alt="image" src="https://github.com/user-attachments/assets/5859c3a4-af82-42a2-969d-9afae16a6500" />

Mở file pdf ta thấy vài dòng linh tinh, theo đề là invisble ink nên ta có thể ctrl a để chọn toàn bộ và paste ra ngoài, hoặc có thể dùng pdftotext 

Output ra như sau 
```bash
 pdftotext chall.pdf -
Roses are red, violets are blue,
CTFs are fun, finding flags is new.
From web to crypto, we break the code,
On the path to root, we lighten the load.

There’s nothing here lol why are you looking


Ok fine here’s the password: DBf8nEBgwRhZ
```
nó cho ta 1 cái password, ta có thể dự đoán có file zip ẩn bên trong, extract ra bằng mật khẩu bên trên 

có thể dùng binwalk để tự kiểm chứng pdf chứa file zip 

payload 
```
unzip -P 'DBf8nEBgwRhZ' chall.pdf -d out
```
Ta được 1 ảnh flag bị xoáy

Ta lên lunapic, hoặc có thể dùng tool khác cũng đc

Ta chỉnh độ xoáy xuống khoảng -220, từ đó có thể nhận được flag 

<img width="1538" height="891" alt="image" src="https://github.com/user-attachments/assets/c370fd93-1d54-4ce3-9fdd-3ba6f1fe75dc" />

---
# Flag 
```bash
tjctf{p0lygl0t_files_4r3_50_c00l}
```

