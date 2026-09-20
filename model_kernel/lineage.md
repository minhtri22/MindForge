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


## 2026-09-21 — Cập nhật phụ thuộc CQG và KCL trước MK-1

Đã rà soát lại hai nguồn phụ thuộc trực tiếp cho nghiên cứu biểu diễn.

CQG đã đóng chuỗi biểu diễn đến J3.16. Kết quả chính:

- J3.14: các biện pháp tăng dữ liệu và đổi lớp học tổng quát không đủ theo cổng đã khóa;
- J3.15: lỗi tương quan thứ hạng của nhánh cấu trúc là bệnh lý số học gần hòa, không phải đảo thứ tự có ý nghĩa;
- J3.16: biểu diễn quan sát có cấu trúc được xác nhận trên tập mới.

Các mốc CQG dùng để đối chiếu:

- J3.15 báo cáo: `110e93ef94e0e4ab6bb03221a6c52a387f9994d6`
- J3.15 bằng chứng chính thức: `4f4407a6bc7832c3b093963758e46e18e8f37004`
- J3.16 báo cáo: `314e08ce9385022b08ccaba887d4a6d6149a54e3`
- J3.16 kết quả chính thức: `edbc04aa09ab9493fed296a34826d3cf13600d94`
- J3.16 bằng chứng chính thức: `181758a70bac6477a88ee463cc8bc9c88e5a4c27`

KCL đã đóng chuỗi 6.5.9.x bằng đánh giá hội tụ chính thức tại nhánh `research/kernel-cl`, đầu nhánh:

`a9159ae8f17693453e7b6378c92deb5effc4a56f`

Mã băm nội dung đánh giá hội tụ:

`a0cba485b5f59c8c60ae5806cb24e394edee4bef`

Kết luận được kế thừa ở mức ràng buộc thiết kế:

- kiểm tra độ ổn định của mục tiêu trước khi học;
- kiểm tra khả năng nhận dạng từ dữ liệu quan sát trước khi dự đoán;
- giữ các thành phần cơ chế riêng trước khi gộp;
- không đồng nhất biểu diễn với điều khiển;
- không mở chuỗi cứu hộ vô hạn sau một kết quả âm sạch.

Đã cập nhật quản trị Lõi mô hình bằng các mã cam kết:

- `3c1a346b16db4ee8bc39f18fa2e79e495f0dcc6f`
- `83a011698f00c617dc72088aebdf6b1403ad43d4`
- `ae3a9abed6f1015cec896c050704e4106f56ace0`

Trạng thái khoa học sau bước này:

- MK-0 vẫn đóng;
- MK-1 được phép mở ở mức đặc tả và đăng ký trước;
- chưa cho phép sửa mã mô hình;
- chưa cho phép tạo dữ liệu thực nghiệm;
- chưa cho phép huấn luyện.


## 2026-09-21 — Khóa đặc tả và đăng ký trước MK-1

Đã mở MK-1 ở mức đặc tả và đăng ký trước בלבד; chưa sửa mã mô hình, chưa tạo dữ liệu khoa học và chưa huấn luyện.

Đã khóa các tài liệu:

- bản thể mục tiêu: `cea1d38707e65fbf48cfcab738d0804ffedba088`
- kiểm tra độ ổn định và biên mục tiêu: `ab724f00ac5afe689629038482b38e78e3e9161c`
- hợp đồng khả năng nhận dạng từ dữ liệu quan sát: `5bc835dd26442a7c7b264ecffc8b9fa5c9f7f790`
- cấu trúc Z phân rã: `b6888922e8577be8e8463dd8838a2114c4d2d791`
- đường cơ sở và cân bằng tài nguyên: `72c309cc9a326772788e82f853b5da68e828b819`
- chia tập, đánh giá và điều kiện bác bỏ: `4abe33d448dff09a13027fcd23ee89882ed7d8cc`
- ứng viên đăng ký trước ban đầu: `c3822b4f7c7dfa5fc6e0e9b514014873162f8814`

Kiểm tra không-khoa-học phát hiện hai vấn đề trước khi chạy thực nghiệm:

- trạng thái J3.14 cũ và ký tự xuống dòng bị ghi sai trong lộ trình;
- công thức đánh giá Z2 còn để hở một bậc tự do cho giai đoạn cài đặt.

Đã sửa trước mọi dữ liệu và kết quả khoa học:

- sửa lộ trình: `d89a7a4ec49edaf006fc589e18c5e88729c2757b`
- khóa công thức chuẩn hóa và cổng Z2: `75dcb4771c2535a57ebaf5432a43a23672ee1dab`
- gắn lại mã băm tài liệu đánh giá vào đăng ký trước: `4395a3ab87acfd4a68ef103c3a28d7d7cc223abc`

Kiểm tra không-khoa-học đạt. Mã cam kết:

`e2331e2b1c9462d5067718f5cfbf5b46cb96ce9d`

Đăng ký trước sau kiểm tra được khóa tại:

`90594c5ec25dc203573d4194dab55ef71381a831`

Đã cập nhật cổng phụ thuộc và lộ trình:

- `bd96016d1ece0f9811212b2eac4caa4dde5c36ad`
- `c09f12d783fbc663e0b2fc0416eaa256cbc68781`

Trạng thái khoa học:

- MK-1 đã đăng ký trước;
- kiểm tra không-khoa-học đã đạt;
- chưa cho phép tạo dữ liệu khoa học;
- chưa cho phép cài đặt nhánh mô hình MK-1;
- chưa cho phép huấn luyện.

Cổng kế tiếp là dựng lại chính xác B0, khóa ánh xạ cài đặt và kiểm tra trước khi dùng dữ liệu mới.


## 2026-09-21 — Đính chính câu mở đầu mục trước

Câu mở đầu của mục ngay trước được hiểu là:

Đã mở MK-1 chỉ ở mức đặc tả và đăng ký trước; chưa sửa mã mô hình, chưa tạo dữ liệu khoa học và chưa huấn luyện.

Đính chính này chỉ sửa lỗi gõ chữ, không thay đổi nội dung khoa học, trạng thái hay cổng thực hiện.


## 2026-09-21 — Dựng lại B0 trên nhánh Lõi mô hình

Đã chạy cổng dựng lại B0 trên nhánh `research/model_core`.

Lần chạy đầu:

- số lần chạy: `35526242084`
- mã cam kết: `015780ae7f2bf786b92dc18e62938a3beeb7258d`
- trạng thái: không hợp lệ do môi trường kiểm thử không nhận đường dẫn gói cục bộ;
- không tạo kết quả dựng lại B0 và không tạo bằng chứng khoa học.

Đã sửa duy nhất đường dẫn nhập gói cục bộ tại:

`6f54872d0825f07a3394747576c537ca447c999b`

Lần chạy hợp lệ:

- số lần chạy: `35526336632`
- trạng thái: đạt;
- gói bằng chứng: `10609797460`
- mã băm gói bằng chứng: `e2a87f0871c8b8c6a55493f8b186221d0dd41705aac4eb70be1bf2a5e82ca632`

Kết quả chính:

- cấu hình B0 khớp hợp đồng đã khóa;
- số tham số: `10,339,200`;
- hợp đồng chạy TokenModel: đạt;
- checkpoint lịch sử có mã băm `6561fa2b354b317cf173faaa5a5cc236a4584cb047df3afdb2871dabae01778e`;
- khôi phục model: đạt;
- khôi phục optimizer: đạt;
- sai lệch lặp đánh giá: `0.0`;
- sinh tham lam lặp lại chính xác: đạt.

Giới hạn: tokenizer và dữ liệu token Phase-2 lịch sử không nằm trong cây Git hiện tại, vì vậy lần chạy này không tuyên bố tái tạo lại chỉ số Phase-2 lịch sử. Phần đánh giá và sinh chỉ kiểm tra tính quyết định hiện tại bằng dữ liệu giả lập không-khoa-học.

Tài liệu đóng cổng:

`c96f6962504bba5fa3ffe5d3f0efb260fa19ca1f`

Trạng thái khoa học: dựng lại B0 đạt. Chưa tạo dữ liệu MK-1 và chưa huấn luyện. Cổng tiếp theo là kiểm tra khả thi cân bằng B0-DIRECT với M1-Z.
