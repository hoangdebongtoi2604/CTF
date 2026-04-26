## Phân tích

Đề bài cho mình một ảnh chụp từ camera giao thông trực tiếp.

Ở Mỹ, các camera kiểu này thường nằm trên website của DOT, tức Department of Transportation của từng bang.

Nhìn kỹ ảnh đề bài, mình rút ra được vài đặc điểm:

- đường 2 làn, nhìn giống highway ở Mỹ
- địa hình rất trống trải
- camera đặt cố định bên đường
- có biển cảnh báo màu vàng bên đường
- gần như không có nhà cửa hay khu dân cư nào xung quanh

Từ mấy dấu hiệu này, mình đoán khu vực trong ảnh có thể nằm ở miền Tây nước Mỹ, kiểu Wyoming, Colorado, Utah, Montana,... Nói chung là mấy bang có nhiều đoạn highway chạy qua vùng high plains, khô và vắng người.

Lúc này mình vẫn chưa biết chính xác là bang nào cả. Thế nên hướng làm hợp lý là đi tìm các website camera giao thông công khai của các bang miền Tây nước Mỹ trước đã :vvv

Một số keyword ban đầu mình dùng:

```text
state DOT traffic cameras
511 road cameras
highway web cameras
western US traffic cameras
```

Sau đó mình thử thu hẹp dần theo các bang có cảnh quan giống ảnh. Wyoming là một hướng khá đáng nghi, vì bang này có rất nhiều camera đường bộ đặt ở những khu vực trống trải, khô, ít nhà cửa, nhìn khá giống ảnh đề bài.

## Các bước tra cứu
### Bước 1: Tìm hệ thống camera giao thông của Wyoming

Mình bắt đầu tìm các từ khóa liên quan đến camera đường bộ của Wyoming:

```text
Wyoming traffic cameras
Wyoming 511 web cameras
WYDOT web cameras
WYOROAD web cameras
```

Trong đó:

- `WYDOT` là Wyoming Department of Transportation
- `WYOROAD` là hệ thống thông tin đường bộ / camera của Wyoming

Các keyword này dẫn đến trang camera của WYDOT / WYOROAD.

Một trang rất quan trọng là danh sách camera các tuyến không phải Interstate:

```text
https://www.wyoroad.info/Highway/webcameras/all?route=NonInterstateCameras
```

Lý do mình mở trang này là vì ảnh đề bài không giống một đường Interstate lớn. Đường trong ảnh chỉ có 2 làn, vắng xe, chạy qua khu vực trống trải, nên khả năng cao nó nằm trên US Highway hoặc State Highway hơn là Interstate. :>>>

### Bước 2: Dò danh sách Non-Interstate Routes

Trong trang Non-Interstate Routes, WYDOT liệt kê rất nhiều camera theo tuyến đường và vị trí.

Ở bước này mình chưa biết town nào, nên không thể search thẳng tên town được. Cách làm là dò từng camera có mô tả / vị trí có vẻ giống ảnh đề bài, rồi mở ra so khung cảnh.

- đường 2 làn
- đường vắng
- địa hình khô, trống trải
- ít hoặc không có nhà dân

Trong quá trình dò cái đống camera kia, mình thấy một dòng khá đáng chú ý:

```text
US287/US30 | Hanna Junction | 3.11 miles west of Hanna Junction (mm 249.6)
```

Link :

```text
https://www.wyoroad.info/Highway/webcameras/all?route=NonInterstateCameras
```

Dòng này đáng chú ý vì `US287/US30` là kiểu highway đúng với ảnh, còn `Hanna Junction` nghe giống một điểm giao đường có camera giao thông cố định. Thế là mình mở thử camera này để kiểm tra tiếp.

### Bước 3: Mở trực tiếp camera Hanna Junction

Từ dòng `Hanna Junction`, mình mở trang camera riêng:

```text
https://www.wyoroad.info/highway/webcameras/view?site=US30HannaJct
```

Trang này ghi rõ camera là:

```text
US287/US30 Hanna Junction - mm 249.60
```

Các góc camera trên trang gồm:

```text
US 30 Hanna Junction - West
US 30 Hanna Junction - East
US 30 Hanna Junction - Road Surface
```

Đến đây mình bắt đầu so ảnh đề bài với các góc camera trên trang.

Các điểm khớp khá rõ:

- cùng kiểu đường 2 làn
- cùng kiểu địa hình khô, trống trải
- có đồi thấp / núi ở xa
- camera đặt cố định bên đường
- góc nhìn và mặt đường rất giống ảnh đề bài

Đến đoạn này thì hướng đi gần như đúng rồi, nhìn phát kiểu “à đây rồi chứ còn đéo đâu nữa” =)))

### Bước 4: Kiểm tra lại bằng route US30 và US287

Để chắc hơn, mình kiểm tra thêm bằng danh sách camera theo từng route.

Vì camera được ghi là:

```text
US287/US30 Hanna Junction
```

nên mình kiểm tra route US30:

```text
https://www.wyoroad.info/pls/Browse/WRR.CameraRoutesResults?SelectedRoute=US30
```

và route US287:

```text
https://www.wyoroad.info/pls/Browse/WRR.CameraRoutesResults?SelectedRoute=US287
```

Kết quả là các trang route cũng dẫn về camera Hanna Junction / khu vực US287-US30. Lúc này có thể chốt vị trí camera là đúng, không phải đoán mò nữa :3

## Xác định thị trấn gần nhất

Đề bài hỏi:

```text
the name of the nearest town
```

Tức là đề không hỏi tên camera, không hỏi tên đường, cũng không hỏi milepost. Đề hỏi thị trấn gần nhất.

Camera nằm ở:

```text
US287/US30 Hanna Junction - mm 249.60
```

Trong danh sách WYDOT, vị trí này được mô tả là:

```text
3.11 miles west of Hanna Junction
```

Tên camera và mô tả đều xoay quanh `Hanna Junction`. Khu vực này nằm gần Hanna, Wyoming, nên town gần nhất cần lấy là:

```text
Hanna, WY
```

Thế là sau một vòng mò camera hơi vl, đáp án cuối cùng là:

```text
UMDCTF{Hanna, WY}
```

## Flag

```bash
UMDCTF{Hanna, WY}
```

## Tài liệu tham khảo

- Camera trực tiếp Hanna Junction của WYDOT / WYOROAD:

```text
https://www.wyoroad.info/highway/webcameras/view?site=US30HannaJct
```

- Popup camera Hanna Junction:

```text
https://www.wyoroad.info/highway/webcameras/view?popUp=true&site=US30HannaJct
```

- Danh sách camera Non-Interstate Routes của WYDOT:

```text
https://www.wyoroad.info/Highway/webcameras/all?route=NonInterstateCameras
```

- Danh sách camera theo tuyến US30:

```text
https://www.wyoroad.info/pls/Browse/WRR.CameraRoutesResults?SelectedRoute=US30
```

- Danh sách camera theo tuyến US287:

```text
https://www.wyoroad.info/pls/Browse/WRR.CameraRoutesResults?SelectedRoute=US287
```

