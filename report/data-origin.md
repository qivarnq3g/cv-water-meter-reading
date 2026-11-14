# 2. Nguồn gốc dữ liệu
## 2.1. Nguồn công bố và giấy phép sử dụng
Nhóm sử dụng bộ **Word-Wheel Water Meter Dataset**, được Shunyi Zhao, Yibo Gao, Fei Liu, Yuxuan Zhang và Jonghui Li công bố trên Dryad với tên *A comprehensive dataset for word-wheel water meter reading under challenging conditions*. Bộ dữ liệu có DOI **10.5061/dryad.7d7wm3860**, ngày công bố 30/01/2026; metadata DOI ghi nhận phiên bản 8 [1], [2]. Đây là dữ liệu ảnh đồng hồ nước cơ bánh xe số phục vụ các tác vụ phát hiện/phân đoạn vùng đọc, nhận dạng chỉ số và phân loại điều kiện ảnh [1].

Giấy phép của **bộ dữ liệu trên Dryad** là **Creative Commons Zero v1.0 Universal (CC0-1.0)**. Thông tin này được kiểm tra trực tiếp qua trường `license` trong API chính thức của Dryad, có giá trị `https://spdx.org/licenses/CC0-1.0.html` [2]. Theo bản mô tả CC0 của Creative Commons, dữ liệu có thể được sao chép, chỉnh sửa và phân phối lại, kể cả cho mục đích thương mại, trong phạm vi quyền tác giả và quyền liên quan được từ bỏ theo công cụ này [3].

## 2.2. Bối cảnh thu thập và điều kiện chụp
Theo mô tả của tác giả trên Dryad, ảnh được thu thập trong quá trình nhân viên ghi chỉ số đồng hồ thủ công tại **Hàng Châu (Hangzhou), Trung Quốc**. Hệ thống cấp nước tại đây có nhiều đồng hồ truyền thống với tuổi sử dụng khác nhau; ảnh phản ánh điều kiện vận hành thực tế, với biến thiên về góc chụp, mức che khuất và biến dạng quan sát được [1].

Bài báo mô tả dữ liệu nêu các tình huống ảnh rõ, mờ, mặt đồng hồ bẩn, đất che phủ, thiếu sáng và phản xạ. Các vùng đọc có thể bị xoay ngược hoặc có chữ số đang chuyển tiếp giữa hai số [4]. Những tình huống này có thể xuất hiện đồng thời trong một ảnh.

## 2.3. Quy mô và cấu trúc bộ dữ liệu gốc
Tác giả tổ chức dữ liệu thành hai phần `detection` và `recognition`. Bảng 2.1 ghi **quy mô do tác giả công bố**, lấy từ README trên Dryad [1].

**Bảng 2.1. Quy mô công bố của bộ dữ liệu gốc [1].**

| Thành phần | Train gốc | Test gốc | Tổng | Định dạng và kích thước |
|---|---:|---:|---:|---|
| Phát hiện/phân đoạn vùng đọc (`detection`) | 32.714 | 13.398 | 46.112 | PNG; 512 × 512 điểm ảnh |
| Nhận dạng năm chữ số (`recognition_5-digit`) | 11.867 | 2.000 | 13.867 | JPG; cao 60 × rộng 200 điểm ảnh |
| Nhận dạng sáu chữ số (`recognition_6-digit`) | 2.555 | 400 | 2.955 | JPG; cao 60 × rộng 200 điểm ảnh |

Phần `detection` cung cấp ảnh đồng hồ, mặt nạ vùng đọc và nhãn điều kiện ảnh. Phần `recognition` cung cấp ảnh vùng đọc cùng nhãn chỉ số; các vùng này được tạo từ quá trình xử lý ảnh đồng hồ rồi chọn lọc để xây tập nhận dạng [1], [4]. Vì vậy, không cộng các hàng trong bảng để suy ra số lần chụp hoặc số đồng hồ độc lập.

Nhóm sử dụng **phần nhận dạng năm chữ số**. Quy mô dữ liệu gốc khả dụng cho phạm vi này là 13.867 ảnh.

## 2.4. Cách xây dựng dữ liệu và gán nhãn
Nhãn tham chiếu do nhóm tác giả cung cấp sẵn. Mục *Author contributions* của bài báo xác nhận **Yibo Gao phụ trách gán nhãn**, **Jonghui Li phụ trách thu thập dữ liệu**, **Shunyi Zhao phụ trách xây dựng bộ dữ liệu**, và **Yuxuan Zhang phụ trách phân tích dữ liệu và kiểm soát chất lượng** [4].

Theo tác giả, các ảnh không hợp lệ được loại thủ công. Với phần phát hiện/phân đoạn, vùng đọc được đánh dấu bằng tứ giác trong LabelMe rồi chuyển thành mặt nạ nhị phân: vùng đọc màu trắng, nền màu đen. Nhãn điều kiện ảnh được mã hóa đa nhãn nhị phân (*multi-hot*), cho phép nhiều thuộc tính cùng có giá trị `1` trên một ảnh [4].

Với phần nhận dạng, tác giả chọn các vùng đọc đại diện, gồm cả ảnh khó, rồi biến đổi phối cảnh về hình chữ nhật. Tệp CSV chứa tên ảnh, chuỗi chỉ số và ba cờ nhị phân mô tả tình huống nhận dạng [4]. Cấu trúc nhãn được mô tả trong Bảng 2.2 [1], [4].

**Bảng 2.2. Cấu trúc nhãn nhận dạng.**

| Cột | Nội dung | Cách sử dụng trong dự án |
|---|---|---|
| 1 | Tên tệp ảnh | Ghép đúng ảnh với dòng nhãn tương ứng. |
| 2 | Chuỗi chỉ số gồm năm hoặc sáu chữ số | Giữ dạng chuỗi để bảo toàn số 0 ở đầu; dùng làm nhãn tham chiếu. |
| 3 | `reversed` | Cờ ảnh vùng đọc bị ngược; mã đọc dữ liệu hiện dùng cờ này để xoay ảnh 180 độ. |
| 4 | `half-word` | Cờ có chữ số đang lăn/chuyển tiếp, chỉ hiện một phần của hai chữ số. |
| 5 | `six-digit` | Cờ đồng hồ sáu chữ số; phạm vi hiện tại sử dụng phần năm chữ số. |

Các cờ dùng giá trị `1` khi có thuộc tính tương ứng và `0` khi không có. Tệp nhãn gốc đang có trong dự án **không có dòng tiêu đề**; thứ tự cột được diễn giải theo mô tả nguồn. Các tệp danh sách chia tập do nhóm tạo trong `experiments/splits` có dòng tiêu đề riêng, theo cấu trúc của `src/wmr/dataset.py`.

Việc dùng cờ `reversed` để xoay ảnh là giả định thu hẹp hiện có của mã nguồn: hướng ảnh được biết từ nhãn tham chiếu. Giả định này cần được giữ nhất quán khi so sánh baseline với phương pháp đề xuất.

## 2.5. Các tập dữ liệu sử dụng trong thực nghiệm - chờ issue #1
**Nguồn cập nhật:** [issue #1 - Đọc dữ liệu, chia tập phát triển và tập đánh giá](https://github.com/qivarnq3g/cv-water-meter-reading/issues/1), README dự án và các danh sách trong `experiments/splits`.

Thiết kế hiện có sử dụng tập train gốc năm chữ số làm tập phát triển, chia tiếp thành phần dựng mẫu (`dev_fit`) và phần chọn tham số (`dev_val`). Tập test gốc năm chữ số được giữ làm tập đánh giá (`eval`). Mã chia tập hiện gán ảnh theo mã băm SHA-1 của tên ảnh để có thể tái tạo. Bảng 2.3 chừa chỗ theo phạm vi issue #4; số ảnh sẽ được lấy từ kết quả issue #1 và đối chiếu các CSV trước khi ghép báo cáo.

**Bảng 2.3. Số ảnh thực tế của từng tập - chờ xác nhận từ issue #1.**

| Tập của dự án | Tập gốc | Danh sách ảnh hiện có | Số ảnh | Số ảnh `half-word` |
|---|---|---|---|---|
| Phát triển, phần dựng mẫu | Train năm chữ số | `experiments/splits/dev_fit.csv` | **[CHỜ ISSUE #1]** | **[CHỜ ISSUE #1]** |
| Phát triển, phần chọn tham số | Train năm chữ số | `experiments/splits/dev_val.csv` | **[CHỜ ISSUE #1]** | **[CHỜ ISSUE #1]** |
| Đánh giá | Test năm chữ số | `experiments/splits/eval.csv` | **[CHỜ ISSUE #1]** | **[CHỜ ISSUE #1]** |

Khi cập nhật, cần xác nhận các tập không trùng ảnh; mọi quyết định chọn tham số phải dựa trên tập phát triển. Tập đánh giá được dùng để báo cáo kết quả sau khi phương pháp và tham số đã được chốt.

## 2.6. Thước đo độ lăn và phân tầng tập đánh giá - chờ issue #3
**Nguồn cập nhật:** [issue #3 - Thước đo độ lăn của chữ số cuối và chia ba tầng](https://github.com/qivarnq3g/cv-water-meter-reading/issues/3). Theo issue này, định nghĩa, tiêu chí chia tầng, số ảnh và minh họa sẽ được ghi trong `experiments`.

- **Định nghĩa thước đo trực tiếp trên ảnh:** [CHỜ ISSUE #3: công thức, vùng ảnh dùng để đo, đơn vị hoặc miền giá trị].
- **Diễn giải cường độ:** [CHỜ ISSUE #3: giá trị tăng/giảm biểu thị mức khó như thế nào].
- **Cách xác định ngưỡng:** [CHỜ ISSUE #3: cơ sở chọn ngưỡng và quy tắc xử lý giá trị nằm trên biên].
- **Tệp mô tả phân tầng:** [CHỜ ISSUE #3: đường dẫn chính xác trong `experiments`].

**Bảng 2.4. Phân tầng cường độ lăn trên tập đánh giá - chờ issue #3.**

| Tầng | Tiêu chí theo thước đo độ lăn | Số ảnh đánh giá | Ảnh minh họa |
|---|---|---|---|
| Nhẹ | **[CHỜ ISSUE #3]** | **[CHỜ ISSUE #3]** | **[CHỜ ISSUE #3]** |
| Trung bình | **[CHỜ ISSUE #3]** | **[CHỜ ISSUE #3]** | **[CHỜ ISSUE #3]** |
| Nặng | **[CHỜ ISSUE #3]** | **[CHỜ ISSUE #3]** | **[CHỜ ISSUE #3]** |

Khi hoàn thiện bảng, cần nêu cách xử lý ảnh không đo được hoặc không đủ điều kiện; tổng số ảnh của các tầng phải khớp quy mô tập đánh giá được dùng, hoặc có giải thích rõ phần loại trừ. Các thí nghiệm E1-E4 sẽ dùng tiêu chí phân tầng nhất quán và báo cáo chỉ số theo từng tầng kèm số ảnh, thay vì chỉ đưa trung bình toàn tập.

## Tài liệu tham khảo của mục này
[1] S. Zhao, Y. Gao, F. Liu, Y. Zhang, and J. Li, “A comprehensive dataset for word-wheel water meter reading under challenging conditions,” Dryad, ver. 8, Jan. 30, 2026, [Dataset], doi: [10.5061/dryad.7d7wm3860](https://doi.org/10.5061/dryad.7d7wm3860). Accessed: Nov. 14, 2026. [Online]. Available: https://datadryad.org/dataset/doi:10.5061/dryad.7d7wm3860.

[2] Dryad, “Dataset metadata: doi:10.5061/dryad.7d7wm3860,” Dryad REST API. Accessed: Nov. 14, 2026. [Online]. Available: https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.7d7wm3860.

[3] Creative Commons, “CC0 1.0 Universal.” Accessed: Nov. 14, 2026. [Online]. Available: https://creativecommons.org/publicdomain/zero/1.0/.

[4] S. Zhao, Y. Gao, F. Liu, Y. Zhang, and J. Li, “A Comprehensive Dataset for Word-Wheel Water Meter Reading Under Challenging Conditions,” *Scientific Data*, vol. 13, Art. no. 479, Feb. 2026, doi: [10.1038/s41597-026-06809-z](https://doi.org/10.1038/s41597-026-06809-z). Accessed: Nov. 14, 2026. [Online]. Available: https://www.nature.com/articles/s41597-026-06809-z.
