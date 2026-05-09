# Beautiful Memory - BKISC Write-up
Mô tả “I left my most precious memory here”, nên hướng đầu tiên hợp lý là memory forensics. Trong thư mục challenge có chall.zip, bên trong là chall.dmp khoảng 4.19 GB.

Sau khi dùng `windows.info` thì ta biết được thời điểm dump là `2026-05-06 08:14:34+00:00`

```bash
vol3 -f chall.dmp windows.info
```

<img width="975" height="448" alt="image" src="https://github.com/user-attachments/assets/6d9fc9a3-f2ba-4c57-a0c7-6a874fcc3e9f" />

Cần biết trước khi dump có process nào chạy k.

```bash
vol3 -f chall.dmp windows.cmdline | grep -Ei "msedge.exe|DumpIt.exe|--type=renderer|--no-startup-window"
```

<img width="975" height="401" alt="image" src="https://github.com/user-attachments/assets/a86dc64f-ff2a-4d77-9846-1e608d297b31" />

```bash
vol3 -f chall.dmp windows.pslist
```

<img width="975" height="455" alt="image" src="https://github.com/user-attachments/assets/ba2ee138-e340-4d09-8ff4-0100f83538e9" />

Ta thấy được `msedge.exe` active khá sát lúc dump tức là Edge mở trước lúc dump khoảng hơn 1 phút. CÓ thể browser memory rất hay chứa form, tab, URL, clipboard-like text, cached DOM.

Ta xem command line:

```bash
vol3 -f chall.dmp windows.cmdline | grep -Ei "msedge.exe|DumpIt.exe|--type=renderer|--no-startup-window"
```

<img width="975" height="401" alt="image" src="https://github.com/user-attachments/assets/bcc501a0-3893-46b5-8f73-0f66af45f400" />

Ta tháy nó có `no-startup-window`, kahs sú.

Ta dump riêng memory của thằng Edge:

```bash
vol3 -o edge336dump -f chall.dmp windows.memmap.Memmap --pid 336 --dump > /dev/null
```

Ta extract url mà Edge đã mở từ tằng vừa dump, dạng UTF-16LE:

```bash
strings -a -el edge336dump/pid.336.dmp \
  | grep -Eao 'https?://[^[:space:]"<>]+' \
  | sed 's/[?#].*//' \
  | sort \
  | uniq -c \
  | sort -nr \
  | head -50
```

Lệnh chạy khá lâu, cho ta 1 số kết quả:

```text
    231 http://schemas.microsoft.com/win/2004/08/events/event
    150 https://th.bing.com/th
     85 https://pastebin.com/Gg4g0YBA
     56 http://www.microsoft.com/provisioning/EapCommon
     47 https://www.bing.com/search
     30 https://go.microsoft.com/fwlink/
     28 http://www.microsoft.com/provisioning/EapHostConfig
     26 http://schemas.microsoft.com/wbem/wsman/1/config/listener
     24 https://
     21 https://ntp.msn.com/edge/ntp
     18 https://login.microsoft.com
     17 https://pastebin.com/search
     17 https://pastebin.com/signup
     17 https://pastebin.com/site/login
     16 https://accounts.google.com/
     14 https://pastebin.com/
     12 http://
     12 http://www.microsoft.com/networking/OneX/v1
     12 http://www.microsoft.com/networking/WLAN/profile/v1
     11 http://en.wikipedia.org/wiki/MIT_License),
     11 https://docs.microsoft.com/typography
     11 https://docs.microsoft.com/typography/about
     11 https://sync.quantumdex.io/
      9 https://licensing.md.mp.microsoft.com/v7.0/licenses/
      8 https://accounts.youtube.com/accounts/CheckConnection
      8 https://onetag-sys.com/usync/
      8 https://www.booking.com/index.html
      7 http://microsoft.com
      7 http://schemas.microsoft.com/windows/2003/08/printing/printschemakeywords'])=substring-before(@name,':')]
      7 http://www.microsoft.com/provisioning/BaseEapConnectionPropertiesV1
      7 https://drive.google.com/drive/folders/1zMcksU1rqcwBt4agMnl8UwPNo_NlYDIg
      7 https://res.cdn.office.net/nativehost/5mttl/installer/v2/1.2026.421.500/Microsoft.OutlookForWindows_x64.msix
      7 https://www.bing.com/
      6 http://ctldl.windowsupdate.com/msdownload/update/v3/static/trustedr/en/pinrulesstl.cab
      6 http://manifests.microsoft.com/win/2006/windows/WMI
      6 http://msedge.b.tlu.dl.delivery.mp.microsoft.com/filestreamingservice/files/2132f61f-f790-4ae6-a355-8cf9a1533800
      6 http://msedge.b.tlu.dl.delivery.mp.microsoft.com/filestreamingservice/files/2b43081f-d6ff-4406-bbb9-c327fccbcb45
      6 http://msedge.b.tlu.dl.delivery.mp.microsoft.com/filestreamingservice/files/68591036-2289-4858-9f7f-9149e89c8a08
      6 http://msedge.b.tlu.dl.delivery.mp.microsoft.com/filestreamingservice/files/ca310418-5fd0-4e5d-b086-36b0e159c39e
      6 http://msedge.b.tlu.dl.delivery.mp.microsoft.com/filestreamingservice/files/e8a689a0-0b22-414f-9b05-ec38c305c524
      6 http://msedge.b.tlu.dl.delivery.mp.microsoft.com/filestreamingservice/files/fb6dd03b-99d7-4cc8-a878-91c8e655c2d3
      6 http://www.microsoft.com/provisioning/EapTtlsConnectionPropertiesV1
      6 http://www.microsoft.com/provisioning/MsPeapConnectionPropertiesV2
      6 https://ads.betweendigital.com/sspmatch-iframe
      6 https://g.live.com/odclientsettings/ProdV2
      6 https://outlook.com/\
      6 https://ww55.affinity.net/sssdomweb
      5 http://ctldl.windowsupdate.com/msdownload/update/v3/static/trustedr/en/authrootstl.cab
      5 http://ctldl.windowsupdate.com/msdownload/update/v3/static/trustedr/en/disallowedcertstl.cab
      5 http://ocsp.digicert.com/MFEwTzBNMEswSTAJBgUrDgMCGgUABBTrjrydRyt%2BApF3GSPypfHBxR5XtQQUs9tIpPmhxdiuNkHMEWNpYim8S8YCEAjTxtAB8my1oj8MfWpz%2F7Y%3D
```

Ta thấy được các url có hành vi người dùng:

```text
85 https://pastebin.com/Gg4g0YBA
47 https://www.bing.com/search
17 https://pastebin.com/search
17 https://pastebin.com/signup
17 https://pastebin.com/site/login
14 https://pastebin.com/
7  https://drive.google.com/drive/folders/1zMcksU1rqcwBt4agMnl8UwPNo_NlYDIg
```

Bing search với query `q=pastebin` và nhiều path của Pastebin như `/search`, `/signup`, `/site/login`.

Pastebin là trang nhập text, ta tìm EDGE memory có form state không

Xem context quanh pastebin:

```bash
strings -a -el edge336dump/pid.336.dmp | grep -i -C 20 "pastebin.com"
```

Lệnh này chạy hơi lâu.

Một số dòng đáng lưu ý:

```text
0xcb6c2c: Pastebin.com - Locked Paste
0xcf1740: https://pastebin.com/Gg4g0YBA
0x1661388: https://pastebin.com/Gg4g0YBA
0x1661568: https://pastebin.com/Gg4g0YBA
0x16615b0: https://pastebin.com/Gg4g0YBA
...
0x1664958: Unlock The Paste
0x1664ac8: Enter password
0x1664b00: PostPasswordVerificationForm[password]
0x1664b68: postpasswordverificationform-password
0x1664bd0: PostPasswordVerificationForm[password]
0x1704358: WorkUnit|31|2112|1005|Tab: Pastebin.com - Locked Paste
0x1f0af54: https://www.bing.com/search?q=pastebin&...
0x1f0b208: ?% Blink serialized form state version 10
0x1f0b2dc: textarea
0x1f0b6d4: https://pastebin.com/signup
0x1f0b724: https://pastebin.com/signup
0x1f0b828: ?% Blink serialized form state version 10
0x1f0b89c: https://pastebin.com/search [q ] #0
0x1f0b97c: https://pastebin.com/signup [_csrf-frontend SignupForm[username] ] #0
0x1f0ba44: SignupForm[email]
0x1f0bac4: SignupForm[username]
0x1f0bb44: real_flag_is_here
```

User thật sự có tab Pastebin, không phải chỉ có URL rác.

Tab cụ thể là `Pastebin.com - Locked Paste`.

URL cụ thể là `https://pastebin.com/Gg4g0YBA`.

Page có form unlock password: `Enter password`, `PostPasswordVerificationForm[password]`.

Có artifact của Chromium form state: `Blink serialized form state version 10`.

Có `textarea`, tức là dữ liệu nhập form có khả năng nằm trong memory.

Có `WorkUnit|31|2112|...|Tab: Pastebin.com - Locked Paste`, tức renderer/tab liên quan là PID `2112`.

Sau khi thấy Pastebin có form, mình gom các artifact liên quan đến form state, field name, textarea, và flag format:

```bash
strings -a -el edge336dump/pid.336.dmp \
  | grep -Ei "Blink serialized form state|textarea|[A-Za-z]+Form\\[[^]]+\\]|BKISC\\{|real_flag_is_here" -C 5
```

Ta ra được 1 số output:

```text
https://pastebin.com/search [q ] #0
SignupForm[username]
real_flag_is_here
SignupForm[verifyCode]
```

Bước tiếp theo là tìm form state của Pastebin trong dump gốc bằng chính artifact vừa phát hiện.

Ta dùng script sau:

```bash
cat > find_paste_form_context.py <<'PY'
import mmap
import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "chall.dmp"

anchors = [
    "PostForm[text]",
    "PostForm[password]",
    "PostForm[name]",
    "Blink serialized form state",
    "BKISC{",
]

keywords = [
    "pastebin",
    "Blink",
    "PostForm",
    "PasswordVerificationForm",
    "SignupForm",
    "textarea",
    "BKISC",
    "flag",
    "password",
    "csrf",
    "expiration",
]

def show_context(mm, center, radius=3500):
    start = max(0, center - radius)
    end = min(len(mm), center + radius)
    blob = mm[start:end]
    rows = []

    for m in re.finditer(rb"[\x20-\x7e]{4,}", blob):
        s = m.group().decode("latin1", "replace")
        if any(k.lower() in s.lower() for k in keywords):
            rows.append((start + m.start(), "ascii", s[:400]))

    for m in re.finditer(rb"(?:[\x20-\x7e]\x00){4,}", blob):
        s = m.group().decode("utf-16le", "replace")
        if any(k.lower() in s.lower() for k in keywords):
            rows.append((start + m.start(), "utf16", s[:400]))

    for off, enc, s in sorted(rows):
        print(f"{off:#x} {enc}: {s}")

with open(path, "rb") as f:
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

    seen = set()

    for anchor in anchors:
        for enc in ("utf-16le", "utf-8"):
            pat = anchor.encode(enc)
            pos = 0

            while True:
                hit = mm.find(pat, pos)
                if hit < 0:
                    break

                pos = hit + 1
                bucket = hit // 0x1000

                if bucket in seen:
                    continue

                seen.add(bucket)
                print(f"\n=== hit {anchor!r} as {enc} at {hit:#x} ===")
                show_context(mm, hit)

    mm.close()
PY

python3 find_paste_form_context.py chall.dmp
```

Output quan trọng sẽ ra block này:

<img width="881" height="429" alt="image" src="https://github.com/user-attachments/assets/2ecc2f10-a70c-4af9-bd03-7db932556819" />


Ta sẽ thấy được flag ngay sau `textarea`:

```text
BKISC{W3ll_M3mory_is_Str0nk_right_?}
```
