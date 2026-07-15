# Phantom

## Thông tin thử thách 

### Đơn giản là thằng tác giả đã vứt 1 cái link github đéo có gì cả, và chúng ta phải tìm cái commit ẩn thông qua sha của nó 

Bài này có rất nhiều cách giải, có cách để dùng tool và có cách để bruteforce sha256 chay, cách này chạy khá lâu, tuy nhiên mình sẽ gửi lại các link youtube để mọi người tham khảo cho việc giải bài này 

- https://www.youtube.com/watch?v=EH3tenVGk60 : Link này để hiểu sơ qua về cách các repo ẩn hoạt động và tại sao có thể tìm ra chúng(về mặt lí thuyết)

- https://trufflesecurity.com/blog/anyone-can-access-deleted-and-private-repo-data-github : tiếp tục là 1 link giải thích về repo bị xóa và ẩn 

- https://trufflesecurity.com/blog/trufflehog-now-finds-all-deleted-and-private-commits-on-github : giải thích về tool để tìm các commit đã bị xóa 

- https://github.com/trufflesecurity/trufflehog : đường dẫn tải tool trufflehog 

TruffleHog cơ bản là tool scan secret. Nó tìm token/API key/password bị lộ trong Git repo, file, S3, GitHub org, Docker image, v.v.


Trong bài này mình dùng phần đặc biệt của nó: GitHub object discovery.
Cách hoạt động chung:

Nhận source

Ví dụ repo GitHub:
```bash
trufflehog github --repo https://github.com/user/repo.git
```
Hoặc mode experimental:
```
trufflehog github-experimental --repo https://github.com/user/
```
```
repo.git --object-discovery
```
Thu thập dữ liệu
Với Git repo bình thường, nó clone/fetch repo rồi đọc:
commit history
file content
diff/patch
deleted files trong lịch sử Git

Chạy detector
Nó có nhiều detector cho secret, ví dụ:
GitHub token
AWS key
Slack token
Stripe key
private key
generic high entropy string

Verify secret

Nếu có thể, nó gọi API của service tương ứng để check token còn sống không. Ví dụ thấy GitHub token thì gọi GitHub API để biết token valid hay revoked.

Output

Nó báo secret, file/commit chứa secret, verified hay unverified.

Riêng mode --object-discovery hoạt động khác hơn.

Nó dựa trên bug/behavior trong bài Truffle Security: GitHub vẫn giữ nhiều Git object thuộc deleted/private fork trong cùng repository network. Nếu biết SHA commit thì vẫn mở được:
https://github.com/owner/repo/commit/<sha>

Nhưng vấn đề là mình không biết SHA.

TruffleHog giải quyết bằng cách enumerate short SHA qua GitHub GraphQL:
```
query {
  repository(owner: "datxmilanista-png", name: "echoes") {
    object(expression: "262a") {
      ... on Commit {
        oid
        message
      }
    }
  }
}
```
Nó thử nhiều prefix kiểu:
0000

0001

0002

...

ffff

Nếu prefix không match object nào, GitHub trả null.

Nếu prefix match commit hidden, GitHub trả full SHA, và sau khi có sha thì ta sẽ có link commit ẩn đó, đơn giản là vậy. 

Cách này sẽ cần các bạn phải gen 1 cái token của github nên cẩn thận tí nhé :v 


