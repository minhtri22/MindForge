# Nhật ký nghiên cứu Lõi mô hình

> **Chỉ được nối thêm.**
>
> Không sửa, xóa, sắp xếp lại hoặc viết đè các mục cũ. Nếu cần đính chính, phải thêm một mục mới ở cuối tài liệu.

## 2026-09-19 — Khởi tạo MK-0

Đã mở nhánh `research/model_core` từ trạng thái MKS-1 đã đóng và xác nhận đầy đủ bằng chứng cục bộ.

Đã tạo đúng sáu tài liệu quản trị, không thay đổi mã nguồn mô hình, dữ liệu, phép thử, quy trình tự động hay kết quả thực nghiệm.

Các mã cam kết tạo MK-0:

- `c73e060cabd86e75a5d32671d6d3d6071caf8a8e`
- `b78037d24671bcc1e5888ddd03518cdf9764ed8e`
- `c7f47633b243a93d77a26f82c1481fe68a17093d`
- `1bb1a3cf0e30b579f4b0b7c843fe69447b18db0e`
- `db0a0f482488451a4e9b82cf627a93c2705d45bf`
- `d6e3c50abdb8606afa9615db221f45e49de3db81`

Trạng thái khoa học: MK-0 hoàn tất; MK-1 chưa mở; chưa cho phép huấn luyện.

## 2026-09-19 — Đổi tên nhánh nghiên cứu

Đã chuyển nhánh làm việc chính sang `research/model_core` để tránh nhầm với khái niệm nhân chạy của MindForge.

Các mã cam kết liên quan:

- `f1d4649ff633ae64ce3cbdcdf54bfe646a5accef`
- `81f67242e004a1f388bbf5c2a69e23091d5af56d`
- `dd4b3a9d45fb40c86885b97811eb4704430a119b`

Không có thay đổi khoa học.

## 2026-09-19 — Rà soát lại CQG J3.13

Đã kiểm tra trạng thái mới nhất của CQG J3.13 và xác nhận lần chạy tự động chính đã hoàn tất thành công.

Nguồn đối chiếu:

- mã cam kết đăng ký trước: `e362ee1cd4234fd2394cbcf8e8e824ea5b14d095`
- mã cam kết chạy J3.13: `708a8e7be594a456c7f362ec079264748d471a2b`
- mã cam kết ghi dấu nguồn gốc: `43d85631d1515aa1b5b09cc549571fe2286a1b28`
- mã băm đăng ký trước: `b772752801f5e0dee814920462cced1ce5b22ba8c2c5af2a8a4d4675a75247f6`
- mã băm gói kết quả: `78b95030e049925ead4645e055858f5f1b99257d0a2d84f701a5513cc80deb85`
- số lần chạy: `35441487604`

Kết quả chính:

- giá trị tuyệt đối có thể được khôi phục từ trạng thái quan sát với sai số số học rất nhỏ;
- biến đổi thang đo riêng không đạt cổng;
- phân rã biểu diễn riêng không đạt cổng;
- kết hợp hai cơ chế cũng không đạt cổng;
- cả bốn nhánh đều không đạt cổng giá trị tuyệt đối;
- điểm nghẽn hiện nghiêng về lớp học hiện tại, không còn ủng hộ giả thuyết rằng giá trị tuyệt đối vốn không thể nhận dạng từ trạng thái quan sát.

Đã cập nhật tài liệu phụ thuộc với các mã cam kết:

- `25280a45c4d0d0519aca212896bf3f9d9f555cdc`
- `1af8c935e694007f29c96eed11eb6d50414c0f8d`
- `403d091a15b5d6ac4d9443635a7e8939ea1243af`

Trạng thái khoa học: kết quả chạy J3.13 đã đủ để thu hẹp hướng MK-1, nhưng CQG chưa có báo cáo và mục nhật ký chính thức sau chạy. Vì vậy chưa mở MK-1 và chưa cho phép huấn luyện.


## 2026-09-19 — Chuyển phụ thuộc từ J3.13 sang J3.14

Đã kiểm tra lại CQG và xác nhận J3.13 đã được đóng chính thức.

Các mã cam kết chính của J3.13:

- báo cáo xác nhận: `008a49f77a99cc7a022412c40f53fa0f32ddb2c9`
- khóa nguồn gốc: `52c2666df2a24d65b7ed79ef63d93177a941ce70`
- kết quả chính thức: `5f98364df5951fd31e44dfd2406b44fec00e0094`
- ghi bằng chứng vào nhật ký: `ce077cd007608df3a98d39f584b9321f998af46d`

J3.14 đã được đăng ký trước để phân biệt ba khả năng còn lại:

- thiếu dữ liệu;
- lớp hàm hoặc thiên kiến học chưa phù hợp;
- cần thiên kiến hợp thành rõ ràng.

Mã cam kết đăng ký trước ban đầu: `a0c9898ef236a816f5279057580fb9db61cf83d8`.

Mã băm đăng ký trước hiện hành sau sửa khả thi trước kết quả:
`d4cc4b504fb1a4e4933d17f4475ec083410c9b7db890262acb839d545847e238`.

Đã ghi nhận sửa lỗi độ chính xác lưu trữ PHI trước khi có kết quả xác nhận. Mã cam kết sửa:
`6b08dc51841bef0d9cacec68dfb367184d8ca3ba`.

Lần chạy sửa hiện hành:
`35453882566`.

Tại thời điểm kiểm tra:

- kiểm tra toàn vẹn đã đạt;
- toàn bộ dữ liệu huấn luyện mới đã thu đủ;
- toàn bộ dữ liệu xác nhận mới đã thu đủ;
- nhánh hợp thành C240 đã huấn luyện xong;
- các nhánh còn lại chưa hoàn tất toàn bộ;
- chưa có kết luận khoa học J3.14.

Đã cập nhật phụ thuộc của Lõi mô hình để chờ kết luận J3.14 thay vì chờ J3.13.

Các mã cam kết cập nhật:

- `1d99da6b6880fe465839de0aba56bf59dff98ff3`
- `cb95b3fe1269503adae9a6909e854364a9bd6c32`
- `fae6f1279048dcdb14dc345f459c1fcde560d81b`

Trạng thái khoa học: MK-1 vẫn chưa mở và chưa cho phép huấn luyện. Kết quả J3.14 có thể trực tiếp loại bớt các phương án về lượng dữ liệu, lớp hàm hoặc cấu trúc hợp thành trước khi khóa thiết kế MK-1.
