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


## 2026-09-21 — Kiểm tra khả thi cân bằng B0-DIRECT và M1-Z

Đã kiểm tra khả năng tạo so sánh công bằng giữa B0-DIRECT và M1-Z sau khi dựng lại B0 đạt.

Kết quả:

`MATCHING_FEASIBILITY_REVISE`

Phần khả thi:

- cân bằng số tham số là khả thi về mặt đại số;
- với cùng trạng thái ẩn rộng 320, tổng số tham số của một đầu ra tuyến tính gộp và nhiều đầu ra tuyến tính tách nhóm bằng nhau nếu tổng số chiều đầu ra bằng nhau.

Ba vấn đề chặn cài đặt được phát hiện trước mọi dữ liệu khoa học:

1. nếu B0-DIRECT và M1-Z cùng dự đoán đúng một vector mục tiêu bằng các phép chiếu tuyến tính tương đương, H1b không còn là một can thiệp khoa học có thể nhận dạng;
2. Z2 chưa khóa đầy đủ các ô giá trị, mặt nạ và chuẩn hóa;
3. Z4 chưa khóa cách tạo nút quan hệ mà không dùng nhãn vàng.

Ngoài ra, tokenizer và mảng token Phase-2 lịch sử không nằm trong cây Git hiện tại; điều này không làm B0 thất bại nhưng phải được xử lý rõ trước huấn luyện.

Tài liệu rà soát:

`6f802ea2592de68e784a7419970116fb72652d9b`

Trạng thái: khóa cài đặt MK-1 bị chặn cho tới khi sửa đăng ký trước bằng một phụ lục trước kết quả. Chưa tạo dữ liệu khoa học và chưa cài đặt M1-Z.


## 2026-09-21 — Sửa đăng ký trước và kiểm tra lại MK-1

Rà soát khả năng cân bằng phát hiện thiết kế so sánh ban đầu có thể tương đương về mặt hàm, nên chưa được phép cài đặt.

Đã khóa phụ lục sửa trước mọi dữ liệu và kết quả:

`4d8e9a8e9e22e17ee35270991e027526600296bf`

Phụ lục khóa lại:

- nhánh trực tiếp học trạng thái chuẩn C;
- nhánh có cấu trúc học Z rồi ghép xác định về C;
- Z có 70 đầu ra cố định;
- C có 34 đầu ra cố định;
- chênh lệch số tham số hai nhánh khoảng 0,112%;
- bộ tách từ chỉ được học từ tập huấn luyện sau khi dữ liệu được phép tạo.

Trong kiểm tra tài liệu tiếp theo đã phát hiện và sửa trước kết quả:

- sai mã băm tham chiếu tài liệu dựng lại B0: `1d07b6deb9c531d8fa439be8debc972353141628`;
- mở rộng kiểm tra độ ổn định và khả năng nhận dạng sang C: `1c69881687d0764e589f57c4fa44c3bee68a4fdb`, `f34554a3530125ced88cedcb04e737f5f4c5fb92`, `599b4ed777c50239db3ae34c75163be4fad5f007`;
- sửa ánh xạ cổng độ ổn định: `b0e97fbd6fe0c87bfc050e6fd37601511011e158`;
- khóa cách xử lý trường hợp không thể nhận dạng duy nhất: `1f03e3855b4f77a07c6f375c50a782d0c485a00b`.

Kiểm tra không-khoa-học cho phụ lục đạt tại:

`238d9f7c9f7d242eb7bff455fd0f46b13eb4cf43`

Đăng ký trước chính được cập nhật trạng thái đạt tại:

`9be308126c9914d59adc8b1e46c6781b4a52568c`

Trạng thái:

- phụ lục đăng ký trước: đạt kiểm tra;
- dựng lại B0: đạt;
- chưa cài đặt mô hình MK-1;
- chưa tạo dữ liệu khoa học;
- chưa huấn luyện.

Cổng tiếp theo là khóa cài đặt MK-1.


## 2026-09-21 — Khóa cách xử lý bộ tách từ trước cài đặt

Kiểm tra lịch sử xác nhận checkpoint Phase-2 còn tồn tại nhưng bộ tách từ và mảng token gốc không có trong cây Git hiện tại cũng như tại đúng mã cam kết huấn luyện `159b5b793af1c18edcc3ebec5a4bd1fca5af0ea5`.

Vì vậy checkpoint lịch sử chỉ được dùng làm bằng chứng tương thích, không dùng làm khởi tạo khoa học với một bộ tách từ mới.

Đã khóa phụ lục thứ hai tại:

`f78e6bff990d1d0ef1956ff5a0c3054d95e958bf`

Quy tắc mới:

- bộ tách từ chỉ học từ bề mặt của tập huấn luyện;
- cả hai nhánh dùng đúng một artifact;
- kích thước thực tế được phép từ 258 đến 16.384;
- kích thước từ vựng của B0 vẫn cố định 16.384;
- không được thêm token giả chỉ để lấp đủ kích thước.

Kiểm tra không-khoa-học của phụ lục đạt tại:

`bbc92b10029022d86b96c9379fe651ea20e710e5`

Đăng ký trước chính được cập nhật tại:

`1f7dfbb353b68617e1522cd3ee47bb0ca83d950f`

Trạng thái: đăng ký trước đã qua toàn bộ kiểm tra; chưa tạo dữ liệu khoa học, chưa huấn luyện. Cổng kế tiếp là khóa cài đặt.


## 2026-09-21 — Khóa cài đặt và ZERO-FRESH PREFLIGHT của MK-1

Sau khi B0 và hai phụ lục đăng ký trước đã qua kiểm tra, đã hoàn tất cài đặt MK-1 trong đúng phạm vi đã khóa.

Các phần chính đã được cài đặt:

- tách trạng thái ẩn B0 nhưng giữ nguyên đường sinh logits;
- B0-DIRECT: đầu ra C 34 chiều;
- M1-Z: đầu ra Z 70 chiều;
- loss theo từng họ Z;
- bộ ghép xác định R(Z) -> C;
- hợp đồng dữ liệu/cảnh xác định;
- lịch lấy mẫu ghép cặp;
- trainer 5.000 bước đã khóa nhưng chưa chạy khoa học;
- bộ metric H1a/H1b/H1c;
- H1c chỉ dùng các trường PIT-v3 có tương ứng ngữ nghĩa chính xác;
- preflight chỉ dùng fixture giả lập.

Trong tự rà soát trước manifest đã phát hiện và sửa một leakage implementation: renderer ban đầu in gần như tên target ra văn bản. Leakage được loại bỏ tại:

`4b24d07e33714c48b4b022f3849f03572b563ac3`

Không có dữ liệu khoa học nào được tạo trước hoặc trong sửa đổi này.

Khóa cài đặt cuối được bind bằng manifest Git blob/SHA-256. Manifest PASS cuối trước trigger tại:

`9f68e1e9175c48731d59b41bdd09294789ed1f9a`

Do connector không có hành động workflow_dispatch, đã dùng một trigger một-lần chỉ theo đúng path:

`model_kernel/mk1/ZERO_FRESH_TRIGGER_v0.1.md`

Workflow được bind lại, kiểm tra hash lại, và chỉ cho chạy khi manifest có `IMPLEMENTATION_LOCK_MANIFEST_PASS` cùng marker trigger chính xác.

Các run tự động xảy ra trước manifest:

- `35528445838`
- `35528568383`
- `35528581759`
- `35528608614`
- `35528655281`
- `35528657593`

đều bị loại khỏi evidence bất kể conclusion.

Canonical ZERO-FRESH run duy nhất được adjudicate:

- run: `35529006429`
- head: `22d8c7cf813f114a3573adad5a358e4a926fb0d9`
- tests: `14 passed in 2.73s`
- artifact id: `10610537857`
- artifact ZIP SHA-256: `2ca801ce739f4aa16ac267c0ab8acee5c915dc5058050e435d0542e4bf952708`

Kết quả preflight:

- B0 parameters = `10,339,200`: đạt;
- hidden-state exact-logit parity: đạt;
- B0-DIRECT parameters = `10,350,114`: đạt;
- M1-Z parameters = `10,361,670`: đạt;
- chênh lệch tham số = `0.001115264238293634` (~0,111526%): đạt ngưỡng <=1%;
- tensor slices: đạt;
- zero readout initialization: đạt;
- recomposer identities: đạt;
- `gold_fixture_C == R(gold_fixture_Z)`: đạt;
- direct synthetic loss finite: đạt;
- M1-Z synthetic loss finite: đạt;
- paired synthetic schedule: đạt;
- synthetic tokenizer contract: đạt;
- scientific namespace touched: false;
- scientific seed touched: false;
- scientific data created: false.

Formal verdict:

`ZERO_FRESH_PREFLIGHT_PASS`

Tài liệu đóng cổng:

- commit: `463475128574ee1738267eca4436fc8613fe9e18`
- blob: `b9acbce69bebe8a812ba558140a089cd315846b1`

Ý nghĩa khoa học: cổng này chỉ chứng minh implementation và plumbing phù hợp với hợp đồng đã khóa. Nó không cung cấp bằng chứng rằng Z học được, M1-Z tốt hơn B0-DIRECT, hay tốt hơn D-PIT.

Trạng thái sau cổng:

- B0 reconstruction: PASS;
- implementation lock manifest: PASS;
- canonical zero-fresh preflight: PASS;
- dữ liệu khoa học: chưa materialize;
- tokenizer khoa học: chưa fit;
- scientific training: chưa chạy.

Cổng kế tiếp đúng khoa học là materialize các namespace đã đăng ký chỉ để chạy các audit trước huấn luyện: split/integrity, target stability/margin, observable identifiability, coverage/support, renderer isolation, TRAIN-only tokenizer freeze và input-length contract. Huấn luyện vẫn bị chặn cho đến khi toàn bộ các cổng này đạt.


## 2026-09-21 — Sửa bộ sinh trước dữ liệu và materialize tập khoa học

Trước lần materialize đầu tiên, rà soát tĩnh phát hiện bộ sinh cũ sẽ tạo trùng cảnh giữa các tập và thiếu support cho một số lớp mục tiêu. Vì chưa có dữ liệu khoa học nào được tạo, đã khóa phụ lục sửa trước kết quả tại:

`9d9df52e3b03fc9cf92e3bbd6c602bdeb497bc58`

Các sửa chính:

- dùng một ordinal chung không reset giữa TRAIN, VALIDATION và PRISTINE_CONFIRMATORY;
- sửa lịch primitive/quantifier/temporal/scope để tất cả lớp chính có support;
- cho phép conflict và resolution cùng tồn tại để `resolves_conflict` có lớp dương;
- dùng lịch scalar xác định và duy nhất trên 3.000 cảnh;
- loại quan hệ scope contextual khỏi H1c khi PIT-v3 không có nhãn tương ứng chính xác.

Đã khóa registry khả năng nhận dạng từ input hiện tại tại:

`d069ae6ad4421aecb20384e224e75de4ab8387ac`

Manifest cài đặt V2 đã qua rà soát hash. Lần chạy zero-fresh v0.2 đầu:

`35553272015`

không hợp lệ do guard CI còn trỏ file trigger v0.1; nó dừng trước test/preflight và không tạo bằng chứng khoa học.

Đã sửa wiring tại:

`075a563920e2ae2600b79006104d1cc90f1089c9`

và reauthorize V2 tại:

`28cb51a3748710c70b3d37f11b24986e38bc3f17`.

Canonical zero-fresh v0.2 hợp lệ:

- run: `35553426498`;
- head: `9158031d43b5e4c05e11e672a75485f216a304dd`;
- test: `16 passed`;
- artifact: `10619885524`;
- mã băm ZIP: `37a5050c581e1934740334b573110cebc5ac32bdd0760e8bac620b99750053b1`;
- support dự kiến tối thiểu đều vượt cổng;
- không chạm namespace khoa học, seed khoa học hay dữ liệu khoa học.

Sau PASS đó đã materialize đúng một lần tại run:

`35553551910`

head:

`13f60afec53252b0ddd0ca7d333f7af2afb1be41`

Artifact khoa học canonical:

- id: `10619711251`;
- mã băm ZIP: `b32084d85c3fd259ef66cdfbd9aed8fb7a48bd2efdea7affbbd6ac1d864dd997`.

Kết quả dữ liệu:

- TRAIN: 2.000 cảnh / 4.000 surface, SHA-256 `5bf1b1b5a193ce46baee9aee97e7e03a1e8c2f66bee8216c30cf518a6fb1468a`;
- VALIDATION: 400 cảnh / 800 surface, SHA-256 `8c1eed22186d43b3311c7bbb63edfce7ba13880a11c528529bc411b9062a1495`;
- PRISTINE_CONFIRMATORY: 600 cảnh / 1.200 surface, SHA-256 `5902fec0e68c296d7fa7463f37f7f0acb4b287718030516d3b67d71f96fc78f6`.

Audit thực tế:

- raw-text duplicate: 0;
- canonical-Z duplicate: 0;
- lỗi bất biến giữa surface: 0;
- lỗi phục hồi Z độc lập từ input_text: 0;
- lỗi ghép C độc lập: 0;
- lỗi ghép C bằng R đã khóa: 0;
- cảnh mơ hồ: 0;
- đọc thông tin cấm: 0;
- support tối thiểu TRAIN: 180 cho lớp phẳng, 500 cho Z4 cell, 400 cho C1 cell, 500 cho C5 cell;
- support tối thiểu confirmatory: 54, 150, 120, 150 tương ứng;
- multi-factor confirmatory: 1,0;
- H1c scope-relation coverage chính xác: 0,719;
- scientific tokenizer fitted: false;
- scientific training executed: false.

Formal verdict:

`SCIENTIFIC_MATERIALIZATION_AND_DATA_AUDIT_PASS`

Tài liệu đóng cổng:

`38132025530a20cd3d27bc4cc2b9b4b7ab4be525`

Trạng thái: ba namespace khoa học đã spent và frozen; không được regenerate âm thầm. Cổng tiếp theo là fit đúng một tokenizer từ TRAIN input_text בלבד, khóa hash và audit tokenized inputs. Huấn luyện vẫn bị chặn.
