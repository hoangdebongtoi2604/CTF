# Bộ đi kèm WU Insidogetage

Đọc `CSCV2026_Insidogetage_Writeup_VI.md` ở thư mục cha theo thứ tự. Bản WU trình bày kiểu tự điều tra từ đầu, không dùng đáp án/offset như dữ kiện khởi đầu.

## Hai chế độ khác nhau

- **Discovery:** các script gốc trong `discovery/work/`. Chạy từ thư mục `discovery`, kiểm tra hằng đường dẫn evidence trong source. Có script tự tìm hit, có script chỉ tái dựng sau khi đã định vị được dữ liệu; bảng ở chương 14 phân biệt rõ. Không chạy mọi script một lượt.
- **Replay:** `verify_case.py` đọc bytes tại offsets đã biết, kiểm tra lại kết quả. Đây không phải chương trình tự giải bài từ zero.

```powershell
$py = 'D:\ctftraining\tools\dfir\PythonTools\venv\Scripts\python.exe'
& $py .\verify_case.py `
  --mem 'D:\ctftraining\CSCV2026\fore\insidogetage\work\mem.raw' `
  --out 'C:\Users\ACER\Documents\Codex\2026-09-25\v-o-2\work\wu_recheck'
```

Các dependency có sẵn trong venv trên: `python-snappy`, `pycryptodomex`, `cryptography`, `mnemonic`. Không import mã từ XPI hoặc chạy miner để phân tích.

## Provenance

- `verification.json`: kết quả replay đã chạy thành công, gồm LiME segments, records và 43 image page mappings.
- `evidence_hashes.json`: hash các đầu vào tính khi kiểm tra lại WU, không phải biên bản thu giữ ban đầu.
- `sqlecmd/`: CSV thực tế xuất từ bản sao profile cũ. 248 visits, không có Keplr.
- `sqlecmd_run.txt`: console log lần chạy đó.
- `bstrings_payout.txt`: bốn chuỗi payout đọc từ bản miner dựng một phần.
- `dbbrowser_original.png`, `dbbrowser_no_keplr.png`: GUI đọc bản sao `places.sqlite` ở chế độ read-only.
- `dbbrowser_reconstructed.png`: GUI xem **database do analyst tạo** từ records đã carve.
- `analyst_reconstructed_records.sqlite`: không phải database Firefox gốc phục hồi đầy đủ. Bảng `provenance` ghi rõ nguồn gốc.
- `timeline_review.csv`, `timeline_gui.png`: bảng timeline tổng hợp có cả timestamp gây mâu thuẫn, không phải nguồn chứng cứ mới độc lập.
- `keplr_crypto_source.txt`: excerpt phục vụ đọc crypto flow; đối chiếu exact-version XPI nêu trong WU.
- `tool_usage.json`: phân biệt tool chạy thật, tool chỉ kiểm kê và tool không kết nối được.
- `triage_v2/`: output triage ban đầu: inventory 5.377 member, không có disk image/MFT/J, baseline Linux, 2.118 audit events và timeline command thô.
- `triage_memory_strings.txt`: output broad memory triage sau khi timeline cho thấy phải pivot sang RAM; chưa phải các hit target của từng câu.

## An toàn

`kworker1_dump.zip` bên ngoài thư mục này chứa bản ELF dựng **một phần** từ mẫu đáng ngờ. Chỉ static analysis, không double-click/chạy file. Không upload bộ evidence hoặc mnemonic lên dịch vụ công khai. Các secret trong tài liệu thuộc dữ liệu challenge và được đưa vào để tái lập lời giải.

## Ảnh trong WU

Bản Markdown dùng đường dẫn tuyệt đối để mở được ảnh trong workspace hiện tại. Trong ZIP còn có bản `CSCV2026_Insidogetage_Writeup_Portable.md` với đường dẫn tương đối, tiện chuyển sang máy khác. Nội dung hai bản như nhau, chỉ khác đường dẫn ảnh.
