# My eye burn write up : 

## Author : LâmVBT

### Scenario :
```
anon hasn't been outside in years, so he put the sun in his keyboard. find the flag he types to bring it out.

```
Ta được cung cấp 1 file klc, thử mở file klc này lên 

Các section chính của file là:

- SHIFTSTATE: các trạng thái phím normal, Shift và Ctrl.
- LAYOUT: ánh xạ virtual-key sang mã Unicode.
- DEADKEY: bảng chuyển trạng thái của dead key.

Điểm quan trọng là hậu tố @. Một output như 02d0@ không được xuất ra ngay như ký tự bình thường; nó trở thành dead-key state mới để phím tiếp theo tiếp tục được tra trong bảng DEADKEY.

Ta bắt đầu đi tìm phím khởi đầu

Trong phần LAYOUT có dòng:

```text
29  OEM_3  0  0060@  007e  -1
```

Ở trạng thái normal, OEM_3 là phím backtick. Mã 0060@ cho biết phím này đưa layout vào dead-key state U+0060 thay vì kết thúc bằng một ký tự hiển thị.

Do đó, bắt đầu phân tích bằng state:

```text
U+0060
```

Mỗi dòng được đọc theo dạng:

~~~text
current_state  +  input_character  ->  next_state
~~~

Các mã input/output đều là hexadecimal Unicode. Lần theo từ U+0060 cho kết quả:

| Bước | State hiện tại | Phím nhập | State tiếp theo |
|---:|---|---|---|
| 1 | U+0060 | s (0073) | U+02D0@ |
| 2 | U+02D0 | u (0075) | U+02ED@ |
| 3 | U+02ED | n (006E) | U+02B4@ |
| 4 | U+02B4 | { (007B) | U+02EF@ |
| 5 | U+02EF | p (0070) | U+02BA@ |
| 6 | U+02BA | r (0072) | U+02C9@ |
| 7 | U+02C9 | a (0061) | U+02D3@ |
| 8 | U+02D3 | i (0069) | U+02E9@ |
| 9 | U+02E9 | s (0073) | U+02BD@ |
| 10 | U+02BD | e (0065) | U+02CD@ |
| 11 | U+02CD | t (0074) | U+02E4@ |
| 12 | U+02E4 | h (0068) | U+02D8@ |
| 13 | U+02D8 | e (0065) | U+02EE@ |
| 14 | U+02EE | s (0073) | U+02D4@ |
| 15 | U+02D4 | u (0075) | U+02E1@ |
| 16 | U+02E1 | n (006E) | U+02B0@ |
| 17 | U+02B0 | } (007D) | U+2600 |

Ghép các phím ở cột Phím nhập:

```text
sun{praisethesun}
```




