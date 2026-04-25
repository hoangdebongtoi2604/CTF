## Phân tích

Đề bài cho một ảnh chụp từ camera giao thông trực tiếp. Vì đề có cụm:

```text
live traffic cam
```

-> tìm trong các trang camera giao thông công khai.

Từ ảnh đề bài, ta rút ra các đặc điểm sau:

- đường 2 làn, kẻ vạch kiểu đường cao tốc ở Mỹ
- địa hình khô, trống trải, giống vùng high plains / miền Tây nước Mỹ
- có đồi thấp và núi ở xa
- camera đặt cố định bên đường
- ảnh có chất lượng và góc nhìn giống camera giao thông của DOT
- có biển cảnh báo màu vàng bên đường

Từ các dấu hiệu này, mình tập trung tìm trong các website camera giao thông của các bang miền Tây nước Mỹ, đặc biệt là các trang kiểu:

```text
state DOT traffic cameras
511 road cameras
highway web cameras
```

Trong đó, Wyoming là một hướng rất hợp lý vì bang này có nhiều camera đường bộ đặt ở các khu vực trống trải, khô, ít nhà cửa, rất giống ảnh đề bài.

## Các bước tra cứu

### Bước 1: Tìm trang camera giao thông của Wyoming

Mình tìm với các từ khóa kiểu:

```text
Wyoming traffic cameras
Wyoming 511 web cameras
WYDOT web cameras
WYOROAD web cameras
```

Kết quả dẫn đến hệ thống camera của WYDOT / WYOROAD.

Trang danh sách camera các tuyến không phải Interstate:

```text
https://www.wyoroad.info/Highway/webcameras/all?route=NonInterstateCameras
```

Trang này liệt kê rất nhiều camera của WYDOT theo dạng:

```text
Route | Camera | Location
```

### Bước 2: Dò trong danh sách Non-Interstate Routes

Trong trang Non-Interstate Routes, mình tìm các camera có khung cảnh giống ảnh:

- đường vắng
- địa hình khô
- vùng đồi thấp
- camera nhìn dọc theo đường
- không có nhà cửa hoặc thành phố lớn xung quanh

Có một dòng đáng chú ý:

```text
US287/US30 | Hanna Junction | 3.11 miles west of Hanna Junction (mm 249.6)
```

Link danh sách kiểm chứng:

```text
https://www.wyoroad.info/Highway/webcameras/all?route=NonInterstateCameras
```

### Bước 3: Mở trực tiếp camera Hanna Junction

Từ dòng `Hanna Junction`, mình mở trang camera riêng:

```text
https://www.wyoroad.info/highway/webcameras/view?site=US30HannaJct
```

Trang này ghi rõ:

```text
US287/US30 Hanna Junction - mm 249.60
```

Các góc camera trên trang gồm:

```text
US 30 Hanna Junction - West
US 30 Hanna Junction - East
US 30 Hanna Junction - Road Surface
```

Các góc nhìn này khớp với ảnh đề bài: đường 2 làn, địa hình khô trống trải, đồi thấp phía xa và camera đặt cố định bên đường.

### Bước 4: Kiểm tra bằng trang route US30 / US287

Vì camera nằm trên đoạn giao giữa US287 và US30, có thể kiểm tra thêm bằng các trang camera theo route:

```text
https://www.wyoroad.info/pls/Browse/WRR.CameraRoutesResults?SelectedRoute=US30
```

```text
https://www.wyoroad.info/pls/Browse/WRR.CameraRoutesResults?SelectedRoute=US287
```

Cả hai hướng kiểm tra đều dẫn về camera Hanna Junction / khu vực US287-US30.

## Tìm vị trí camera

Sau khi đối chiếu ảnh với các camera đường bộ, camera khớp với trang WYDOT / WYOROAD của bang Wyoming.

Camera chính xác là:

```text
US287/US30 Hanna Junction - mm 249.60
```

Link camera trực tiếp:

```text
https://www.wyoroad.info/highway/webcameras/view?site=US30HannaJct
```

Link popup của cùng camera:

```text
https://www.wyoroad.info/highway/webcameras/view?popUp=true&site=US30HannaJct
```

Link danh sách camera Non-Interstate Routes:

```text
https://www.wyoroad.info/Highway/webcameras/all?route=NonInterstateCameras
```

Khung cảnh trong ảnh đề bài khớp với khu vực Hanna Junction.
***
```bash
UMDCTF{Hanna, WY}
```

