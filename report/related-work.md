# 3. Công trình liên quan

Đọc chỉ số đồng hồ từ ảnh thường gồm định vị vùng hiển thị, chuẩn hóa hình học và nhận dạng chỉ số. Với đồng hồ nước cơ bánh xe số, một ô có thể chứa đồng thời hai phần của hai chữ số liên tiếp khi bánh xe đang chuyển số. Vì vậy, nhận dạng chữ số đứng yên chưa đủ để giải quyết thách thức chữ số cuối đang lăn mà nhóm lựa chọn. Mục này xem xét ba công trình về đọc chỉ số đồng hồ, cùng nguồn dữ liệu và cơ sở so khớp mẫu, để xác định phần nhóm kế thừa và phần điều chỉnh trong phạm vi bài tập lớn.

## 3.1. Bộ Word-Wheel và các mô hình kiểm chứng của Zhao và cộng sự

Cách làm. Zhao và cộng sự công bố bộ Word-Wheel cho phân đoạn vùng đọc, nhận dạng chỉ số và phân loại điều kiện ảnh. Ảnh được thu thập trong quá trình ghi chỉ số tại Hàng Châu; vùng nhận dạng được nắn về 60 × 200 điểm ảnh. Tác giả kiểm chứng nhận dạng bằng CNN, VGG16, ResNet và DenseNet [4].

Kết quả chính. Bảng 5 của bài báo ghi DenseNet đạt accuracy 98,15%; khi cho phép sai một chữ số, giá trị là 99,80%. Hai tiêu chí này khác nhau. Bảng không tách kết quả theo mức độ lăn, nên các con số trên chưa mô tả riêng hiệu quả xử lý chữ số chuyển tiếp [4].

Nhóm kế thừa và làm khác. Nhóm sử dụng ảnh vùng đọc đã được chuẩn hóa và nhãn chỉ số của bộ dữ liệu. Phạm vi được thu hẹp vào đồng hồ năm chữ số, với hướng ảnh được sửa theo cờ `reversed`. Nhóm chọn so khớp mẫu bằng tương quan chéo chuẩn hóa (normalized cross-correlation, NCC) làm baseline và tự xây dựng dải bánh xe tuần hoàn cho ô cuối. Việc chia ảnh theo cường độ lăn giúp kiểm tra trực tiếp thách thức đã nêu ở mục 1. Kết quả học sâu trong bài báo là bối cảnh tham khảo; chỉ so sánh hiệu quả phương pháp của nhóm khi cùng dữ liệu, tiền xử lý và thước đo.

Bản dữ liệu trên Dryad. Tác giả tổ chức ảnh và nhãn thành hai phần `detection` và `recognition`, với tập huấn luyện và tập kiểm tra riêng. Sản phẩm dữ liệu phục vụ nhận dạng năm chữ số gồm 11.867 ảnh huấn luyện và 2.000 ảnh kiểm tra, kèm nhãn chỉ số [1]. Nhóm kế thừa tập kiểm tra gốc làm `eval`, còn tập huấn luyện được chia thành `dev_fit` để dựng mẫu và `dev_val` để chọn tham số. Bản dữ liệu [1] và bài báo [4] thuộc cùng một công trình; ba công trình đọc chỉ số được xem xét ở đây là Zhao, Hong và Laroca.

## 3.2. Hệ thống đọc đồng hồ nước của Hong và cộng sự

Cách làm. Hong và cộng sự kết hợp YOLO3, căn chỉnh hướng và định vị chữ số bằng ràng buộc bố cục. Để biểu diễn chữ số đang lăn, tác giả dùng phân bố xác suất tuần hoàn (Circle Probability Distribution, CPD), xử lý cả chuyển tiếp 9 -> 0 [5].

Kết quả chính. Trên bộ dữ liệu riêng gồm 9.500 ảnh huấn luyện và 500 ảnh kiểm tra, cấu hình Basic + OA + SG đạt tỷ lệ lỗi chữ số 3,79%, so với 24,32% của Basic trong Bảng 3. OA là căn chỉnh hướng, SG là hướng dẫn bằng bố cục không gian. Đây là lỗi tính trên từng chữ số, không phải tỷ lệ đọc sai toàn bộ chỉ số; phép so sánh này cũng chưa tách riêng đóng góp của CPD [5].

Nhóm kế thừa và làm khác. Công trình này hỗ trợ lựa chọn mô hình hóa trạng thái chuyển số theo vòng 0-9. Nhóm cụ thể hóa ý tưởng tuần hoàn bằng dải ảnh mẫu xếp theo thứ tự chữ số, rồi tìm cửa sổ khớp nhất bằng NCC để ước lượng pha lăn. Tham số giải mã pha thành nhãn được chọn trên tập phát triển. Phương pháp hiện có của nhóm dùng phép so khớp trực tiếp, còn nghiên cứu [5] học biểu diễn xác suất bằng mạng. Nhóm chỉ nghiên cứu ô cuối của ảnh vùng đọc đã chuẩn hóa; phát hiện toàn mặt đồng hồ và đọc kim nằm ngoài phạm vi thực nghiệm hiện tại.

## 3.3. Hệ thống đọc chỉ số trong điều kiện thực tế của Laroca và cộng sự

Cách làm. Laroca và cộng sự đề xuất chuỗi ba mạng: Fast-YOLOv4-SmallObj định vị bộ đếm, CDCC-NET dự đoán tọa độ bốn góc vùng bộ đếm và phân loại khả năng đọc, Fast-OCR nhận dạng. Bộ Copel-AMR gồm 12.500 ảnh đồng hồ điện thực tế, trong đó 2.500 ảnh hỏng hoặc không đọc được [6].

Kết quả chính. Trên phần đồng hồ đọc được của Copel-AMR, hệ thống đạt tỷ lệ đúng cả chỉ số 96,98%, so với 95,43% khi bỏ nắn vùng đọc. Khi loại 15% kết quả có độ tin cậy thấp, tỷ lệ trên phần được giữ lại đạt 99,24% (Bảng 7-8); giá trị này cần được hiểu cùng tỷ lệ loại bỏ [6].

Nhóm kế thừa và làm khác. Nhóm vận dụng cách phân tích theo từng thành phần: cố định đầu vào và baseline, rồi kiểm tra tác động của thành phần xử lý thách thức. Ở dự án này, vùng đọc đã được cắt và nắn sẵn; phép kiểm chứng tập trung vào việc thay mẫu đứng yên bằng dải tuần hoàn tại ô cuối. Các mức độ lăn được báo cáo kèm số ảnh, và độ chính xác cả chỉ số được báo cáo bên cạnh độ chính xác chữ số cuối. Phương pháp hiện tại trả kết quả cho mọi ảnh `eval`, nên mọi phép đối chiếu với hệ thống có cơ chế từ chối phải nêu rõ phạm vi ảnh được tính.

## 3.4. Cơ sở so khớp mẫu bằng NCC của Lewis

Cách làm. Lewis trình bày phép tính NCC với chuẩn hóa theo trung bình và năng lượng của mẫu cùng vùng ảnh. Công trình sử dụng các bảng tổng tích lũy của ảnh và bình phương ảnh để tính phần chuẩn hóa hiệu quả, kết hợp với phép tương quan [7].

Kết quả chính. Kết quả chính là cách tính NCC nhanh; đây là tài liệu phương pháp chung, không cung cấp độ chính xác đọc đồng hồ [7].

Nhóm kế thừa và làm khác. Nhóm dùng NCC làm điểm tương đồng cho cả baseline và phương pháp đề xuất. Với baseline, mỗi ô được đối chiếu với mười mẫu chữ số đứng yên trong phạm vi dịch chuyển nhỏ. Khi ô cuối chứa hai phần chữ số đang lăn, tập mẫu này có thể thiếu giả thuyết phù hợp. Nhóm mở rộng tập giả thuyết thành các cửa sổ của dải tuần hoàn 0-9, đồng thời giữ cách tính điểm. Mã hiện tại tính trực tiếp NCC bằng OpenCV/NumPy; phần nhóm kế thừa từ [7] là cơ sở so khớp, không phải triển khai tối ưu bằng bảng tổng tích lũy hay FFT.

## Tài liệu tham khảo

Xem [danh sách tài liệu tham khảo chung](references.md).
