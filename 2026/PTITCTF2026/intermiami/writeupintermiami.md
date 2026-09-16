# Crypto : Intermiami

## Scenario : Lúc đang nói chuyện với Messi, anh ấy có nói với tôi là Inter... gì đó thì mất kết nối, tôi nghĩ là anh ấy muốn rời Barcelona
1.Đọc server (1).py

File được cung cấp chỉ là lớp TCP wrapper. Nó import cipher thật từ:

```python
from algorithm import init_cipher
from setup import BULK_LIMIT, FLAG, HOST, PORT, TIMEOUT_SECONDS
```
Phần cần phân tích là giao thức:

```python
p = CIPHER.get_pair(p)
...
challenge_plaintext = CIPHER.random_challenge_plaintext()
...
CIPHER.verify(challenge_plaintext, submitted)
```

Server công khai:

```text
q = 170141183460469231731687303715884105727
available pairs = 50001
```

Giá trị `q` là số nguyên tố Mersenne:

```text
q = 2^127 - 1
```

Vì vậy các phép tính của cipher làm việc trên trường hữu hạn `F_q`.

## 2. Vai trò của `RandomPairOrder`

`RandomPairOrder` chỉ xáo trộn thứ tự các plaintext:

```python
value = self.position
self.position += 1
...
return value      # luôn nằm trong [0, 50000]
```

Mỗi connection cuối cùng vẫn trả đủ đúng các giá trị plaintext:

```text
0, 1, 2, ..., 50000
```

Thứ tự ngẫu nhiên không giúp bảo vệ cipher vì server trả cả `p` lẫn `c`. Chỉ cần gọi mục `1` đủ `50001` lần rồi lưu các cặp `(p, c)` theo `p`.

Trong deployment này `BULK_LIMIT` thực tế khiến mỗi request trả một cặp, nên script gửi:

```python
sock.sendall(b"1\n" * (n + 1))
```

Request thừa dùng để nhận marker `No more pairs for this connection.`.

## 3. Nhận ra nội suy Lagrange

Gọi ciphertext thu được là `f(p)`. Challenge cho đúng `N = 50001` điểm trên trường `F_q`:

```text
f(0), f(1), ..., f(50000)
```

Đây là dấu hiệu của một đa thức ẩn có bậc nhỏ hơn `N`. Với `N` điểm phân biệt, đa thức được xác định duy nhất; không cần biết các hệ số bí mật.

Hint “Inter...” của đề trỏ tới **interpolation**, cụ thể là Lagrange interpolation.

Server sau đó đưa một plaintext mới `t` và yêu cầu gửi `f(t)`. Ta chỉ cần đánh giá đa thức tại `t`.

## 4. Công thức

Với `x_i = i`, `y_i = f(i)`, đa thức Lagrange là:

```text
f(t) = Σ y_i · L_i(t)  mod q
```

trong đó:

```text
L_i(t) = Π(j != i) (t-j)/(i-j)
```

Đặt:

```text
P(t) = Π(j=0..N-1) (t-j)
```

thì:

```text
Π(j != i)(t-j) = P(t)/(t-i)
```

Mẫu số có dạng đặc biệt vì các `x_i` liên tiếp:

```text
Π(j != i)(i-j)
  = (-1)^(N-1-i) · i! · (N-1-i)!
```

Do `q` là số nguyên tố, nghịch đảo modulo dùng Fermat:

```python
inverse(a) = pow(a, q - 2, q)
```

Precompute `fact[i]` và `inv_fact[i]` để mỗi trọng số Lagrange tính nhanh. Độ phức tạp là `O(N log q)` do cần nghịch đảo modulo cho các `t-i`; bộ nhớ `O(N)`.

Nếu `t` tình cờ nằm trong `[0, N-1]`, trả thẳng `y[t]` để tránh chia cho 0.