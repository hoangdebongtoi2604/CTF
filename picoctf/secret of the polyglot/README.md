# Secret of the polyglot 

Ta thử mở file pdf thì chỉ thấy vài kí tự của flag, thử mở để xem byte bằng HxD 
<img width="709" height="497" alt="image" src="https://github.com/user-attachments/assets/4cbccc29-fd49-4fd6-97df-be11f4a97ac4" />
Ta thấy được chunk IHDR, đặc trưng của PNG
<img width="570" height="278" alt="image" src="https://github.com/user-attachments/assets/00704725-e883-4bf7-8305-93b4a30ce9fc" />
Chunk IEND của PNG, theo sau đó là file pdf được gắn vào

=> Ảnh gốc là 1 file png, bị thay đổi và nhét thêm 1 file pdf vào sau chunk IEND.

Ta đổi đuôi file từ pdf sang png để lấy flag 
---
## Flag 
```bash
picoCTF{f1u3n7_1n_pn9_&_pdf_1f991f77}
```
