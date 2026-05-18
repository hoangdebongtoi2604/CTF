# Đề bài 

<img width="999" height="368" alt="image" src="https://github.com/user-attachments/assets/dc0191a8-26d7-436a-958b-e906b85b1942" />

Mở ảnh lên thấy toàn là màu xám 

Ta soi metadata chi tiết bằng imagemagick 
```bash
identify -verbose chall.png | less
```

Kết quả trả về 
<img width="534" height="577" alt="image" src="https://github.com/user-attachments/assets/fbd6db0c-fbf4-44f2-ac40-c6ce19d5dc23" />

Các điểm đáng chú ý:
```bash
Geometry: 1888x1888
Depth: 8-bit
Type: GrayscaleAlpha
Alpha: 255
```
ảnh chỉ toàn kênh màu xám và alpha thì k thay đổi (255) 

Ta dùng lệnh check giữa các kênh màu với nhau 
```bash
magick chall.png -separate channels/channel_%d.png
```

Kết quả chỉ trả về đúng 1 channel, như vậy tất cả các kênh màu đều giống nhau 

Đề bài tên triplets, vậy có lẽ ta sẽ phải ghép kênh màu gray thành kiểu gì đấy, có lẽ là đã bị đổi tất cả kênh rgb chỉ thành 1 kênh gray

Mà 1 pixel của ảnh lại được tạo bởi 3 kênh rgb, như vậy có thể 3 pixel grayscale liên tiếp = 1 pixel RGB của ảnh gốc.

Ta lấy chuỗi byte của kênh gray từ ảnh hiện tại.
```bash
magick chall.png -alpha off -colorspace Gray -depth 8 gray:gray.bin
```
Kết quả trả về cho ta 1 file bin Ta có một raw grayscale stream dài 3564544 byte.

Như vậy ta đã có được toàn bộ bytes của ảnh, từ đây ta tiến hành phục dựng ảnh cũ theo các kênh rgb

Để phục dựng ảnh ta cần biết 4 thứ 
width
height
depth
format

Và ta đã biết được :
```bash
depth = 8-bit
format = RGB
```
H ta đi tính height và width của ảnh gốc

Với mỗi width ứng viên w, height sẽ được tính theo cấu trúc raw RGB:

1 pixel RGB = 3 bytes
1 hàng có w pixel = w * 3 bytes
height = floor(total_bytes / (3 * w))

Với:
N = 3564544
thì:
h = floor(N / (3 * w))

Đến đây thì khá khê, vì mình k biết phải tiếp tục thế nào để tìm widght và height của ảnh gốc, tuy nhiên cảm ơn Gemini Pro đã viết script cho mình để bruteforce tính khả thi của width và height

```bash
cat > solve_triplets.sh << 'EOF'
#!/usr/bin/env bash
set -euo pipefail

INPUT="${1:-chall.png}"
MIN_W="${2:-500}"
MAX_W="${3:-4000}"

echo "[+] Input: $INPUT"

if [ ! -f "$INPUT" ]; then
    echo "[!] Không thấy file $INPUT"
    exit 1
fi

# Chọn ImageMagick command phù hợp WSL
if command -v magick >/dev/null 2>&1; then
    IM=(magick)
elif command -v convert >/dev/null 2>&1; then
    IM=(convert)
else
    echo "[!] Không thấy ImageMagick."
    echo "    Cài bằng:"
    echo "    sudo apt update && sudo apt install -y imagemagick"
    exit 1
fi

# Check numpy
if ! python3 - << 'PY' >/dev/null 2>&1
import numpy
PY
then
    echo "[!] Thiếu numpy."
    echo "    Cài bằng:"
    echo "    sudo apt install -y python3-numpy"
    exit 1
fi

echo "[+] File info:"
file "$INPUT"

echo
echo "[+] Extract raw grayscale stream -> gray.bin"
"${IM[@]}" "$INPUT" -alpha off -colorspace Gray -depth 8 gray:gray.bin

if [ ! -s gray.bin ]; then
    echo "[!] Không tạo được gray.bin"
    exit 1
fi

N=$(wc -c < gray.bin | tr -d ' ')
echo "[+] gray.bin size: $N bytes"

echo
echo "[+] Scan width range: $MIN_W -> $MAX_W"
echo "[+] Metric: MAE giữa ảnh và chính nó khi dịch xuống 1 pixel"
echo "[+] Width có MAE thấp nhất = row stride hợp lý nhất"

python3 - "$MIN_W" "$MAX_W" << 'PY'
import sys
import numpy as np

min_w = int(sys.argv[1])
max_w = int(sys.argv[2])

data = np.fromfile("gray.bin", dtype=np.uint8)
N = data.size

rows = []

for w in range(min_w, max_w + 1):
    h = N // (3 * w)

    # Height quá thấp thì không đủ hàng để so sánh
    if h < 100:
        continue

    used = w * h * 3
    remain = N - used

    arr = data[:used].reshape(h, w, 3)

    # So sánh hàng y với hàng y+1.
    # Width đúng thì các hàng align tốt hơn => diff thấp hơn.
    diff = np.abs(arr[1:].astype(np.int16) - arr[:-1].astype(np.int16))
    score = float(diff.mean() / 255.0)

    rows.append((score, w, h, remain))

rows.sort()

with open("width_scores.txt", "w", encoding="utf-8") as f:
    for score, w, h, remain in rows:
        f.write(f"{w} {h} {remain} {score:.9f}\n")

best_score, best_w, best_h, best_remain = rows[0]

with open("best_candidate.txt", "w", encoding="utf-8") as f:
    f.write(f"{best_w} {best_h} {best_remain} {best_score:.9f}\n")

print("[+] Top 20 width candidates:")
print("width height remain score")
for score, w, h, remain in rows[:20]:
    print(f"{w} {h} {remain} {score:.9f}")
PY

read BEST_W BEST_H BEST_REMAIN BEST_SCORE < best_candidate.txt

echo
echo "[+] Best candidate:"
echo "    width  = $BEST_W"
echo "    height = $BEST_H"
echo "    remain = $BEST_REMAIN bytes"
echo "    score  = $BEST_SCORE"

RECOVERED="recovered_${BEST_W}x${BEST_H}.png"

echo
echo "[+] Recover raw RGB image -> $RECOVERED"
"${IM[@]}" -size "${BEST_W}x${BEST_H}" -depth 8 rgb:gray.bin "$RECOVERED"

echo "[+] Crop and enhance flag area -> flag_crop.png"
"${IM[@]}" "$RECOVERED" \
    -crop 850x170+0+0 \
    -resize 300% \
    -colorspace Gray \
    -auto-level \
    -sharpen 0x1 \
    flag_crop.png

echo
echo "[+] Done."
echo "[+] Output files:"
echo "    gray.bin"
echo "    width_scores.txt"
echo "    best_candidate.txt"
echo "    $RECOVERED"
echo "    flag_crop.png"

echo
echo "[+] Mở ảnh trên Windows:"
echo "    explorer.exe $RECOVERED"
echo "    explorer.exe flag_crop.png"
EOF

chmod +x solve_triplets.sh
./solve_triplets.sh
```
script này sẽ chạy khá lâu, theo mình đọc script thì nó sẽ check height width khả thi nhất để ra được ảnh, điểm càng thấp thì width đấy sẽ càng hợp lí cho ảnh, từ đó tìm ra height 

Ta ra được width loanh quanh khoảng 2000 và height 594, từ đó có thể khôi phục dễ dàng lại ảnh 
```bash
magick -size 2000x594 -depth 8 rgb:gray.bin recovered.png
```
Mở recovered.png và ta có flag 
<img width="2000" height="594" alt="recovered" src="https://github.com/user-attachments/assets/c475b44e-e649-4cc7-8587-8d1792788186" />

---
## Flag
```bash
tjctf{my_1m3g3_b3c3m3_bl3ck_&_wh1t3}
```
