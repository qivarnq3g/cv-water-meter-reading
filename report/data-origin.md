# 2. Nguồn gốc dữ liệu
## 2.1. Nguồn công bố và giấy phép sử dụng

Nhóm sử dụng bộ Word-Wheel Water Meter Dataset, được Shunyi Zhao, Yibo Gao, Fei Liu, Yuxuan Zhang và Jonghui Li công bố trên Dryad với tên "A comprehensive dataset for word-wheel water meter reading under challenging conditions". Bộ dữ liệu có DOI 10.5061/dryad.7d7wm3860, ngày công bố 30/01/2026; metadata DOI ghi nhận phiên bản 8 [1], [2]. Đây là dữ liệu ảnh đồng hồ nước cơ bánh xe số phục vụ các tác vụ phát hiện/phân đoạn vùng đọc, nhận dạng chỉ số và phân loại điều kiện ảnh [1].

Giấy phép của bộ dữ liệu trên Dryad là Creative Commons Zero v1.0 Universal (CC0-1.0). Thông tin này được kiểm tra trực tiếp qua trường `license` trong API chính thức của Dryad, có giá trị `https://spdx.org/licenses/CC0-1.0.html` [2]. Theo bản mô tả CC0 của Creative Commons, dữ liệu có thể được sao chép, chỉnh sửa và phân phối lại, kể cả cho mục đích thương mại, trong phạm vi quyền tác giả và quyền liên quan được từ bỏ theo công cụ này [3].

## 2.2. Bối cảnh thu thập và điều kiện chụp

Theo mô tả của tác giả trên Dryad, ảnh được thu thập trong quá trình nhân viên ghi chỉ số đồng hồ thủ công tại Hàng Châu (Hangzhou), Trung Quốc. Hệ thống cấp nước tại đây có nhiều đồng hồ truyền thống với tuổi sử dụng khác nhau; ảnh phản ánh điều kiện vận hành thực tế, với biến thiên về góc chụp, mức che khuất và biến dạng quan sát được [1].

Bài báo mô tả dữ liệu nêu các tình huống ảnh rõ, mờ, mặt đồng hồ bẩn, đất che phủ, thiếu sáng và phản xạ. Các vùng đọc có thể bị xoay ngược hoặc có chữ số đang chuyển tiếp giữa hai số [4]. Những tình huống này có thể xuất hiện đồng thời trong một ảnh.

## 2.3. Quy mô và cấu trúc bộ dữ liệu gốc

Tác giả tổ chức dữ liệu thành hai phần `detection` và `recognition`. Bảng 2.1 ghi quy mô do tác giả công bố, lấy từ README trên Dryad [1].

Bảng 2.1. Quy mô công bố của bộ dữ liệu gốc [1].

| Thành phần | Tập huấn luyện gốc | Tập kiểm tra gốc | Tổng | Định dạng và kích thước |
|---|---:|---:|---:|---|
| Phát hiện/phân đoạn vùng đọc (`detection`) | 32.714 | 13.398 | 46.112 | PNG; 512 × 512 điểm ảnh |
| Nhận dạng năm chữ số (`recognition_5-digit`) | 11.867 | 2.000 | 13.867 | JPG; cao 60 × rộng 200 điểm ảnh |
| Nhận dạng sáu chữ số (`recognition_6-digit`) | 2.555 | 400 | 2.955 | JPG; cao 60 × rộng 200 điểm ảnh |

Phần `detection` cung cấp ảnh đồng hồ, mặt nạ vùng đọc và nhãn điều kiện ảnh. Phần `recognition` cung cấp ảnh vùng đọc cùng nhãn chỉ số; các vùng này được tạo từ quá trình xử lý ảnh đồng hồ rồi chọn lọc để xây tập nhận dạng [1], [4]. Vì vậy, không cộng các hàng trong bảng để suy ra số lần chụp hoặc số đồng hồ độc lập.

Nhóm sử dụng phần nhận dạng năm chữ số. Quy mô dữ liệu gốc khả dụng cho phạm vi này là 13.867 ảnh.

## 2.4. Cách xây dựng dữ liệu và gán nhãn

Nhãn tham chiếu do nhóm tác giả cung cấp sẵn. Mục "Author contributions" của bài báo xác nhận Yibo Gao phụ trách gán nhãn, Jonghui Li phụ trách thu thập dữ liệu, Shunyi Zhao phụ trách xây dựng bộ dữ liệu, và Yuxuan Zhang phụ trách phân tích dữ liệu và kiểm soát chất lượng [4].

Theo tác giả, các ảnh không hợp lệ được loại thủ công. Với phần phát hiện/phân đoạn, vùng đọc được đánh dấu bằng tứ giác trong LabelMe rồi chuyển thành mặt nạ nhị phân: vùng đọc màu trắng, nền màu đen. Nhãn điều kiện ảnh được mã hóa đa nhãn nhị phân (multi-hot), cho phép nhiều thuộc tính cùng có giá trị `1` trên một ảnh [4].

Với phần nhận dạng, tác giả chọn các vùng đọc đại diện, gồm cả ảnh khó, rồi biến đổi phối cảnh về hình chữ nhật. Tệp CSV chứa tên ảnh, chuỗi chỉ số và ba cờ nhị phân mô tả tình huống nhận dạng [4]. Cấu trúc nhãn được mô tả trong Bảng 2.2 [1], [4].

Bảng 2.2. Cấu trúc nhãn nhận dạng.

| Cột | Nội dung | Cách sử dụng trong dự án |
|---|---|---|
| 1 | Tên tệp ảnh | Ghép đúng ảnh với dòng nhãn tương ứng. |
| 2 | Chuỗi chỉ số gồm năm hoặc sáu chữ số | Giữ dạng chuỗi để bảo toàn số 0 ở đầu; dùng làm nhãn tham chiếu. |
| 3 | `reversed` | Cờ ảnh vùng đọc bị ngược; mã đọc dữ liệu hiện dùng cờ này để xoay ảnh 180 độ. |
| 4 | `half-word` | Cờ có chữ số đang lăn/chuyển tiếp, chỉ hiện một phần của hai chữ số. |
| 5 | `six-digit` | Cờ đồng hồ sáu chữ số; phạm vi hiện tại sử dụng phần năm chữ số. |

Các cờ dùng giá trị `1` khi có thuộc tính tương ứng và `0` khi không có. Tệp nhãn gốc đang có trong dự án không có dòng tiêu đề; thứ tự cột được diễn giải theo mô tả nguồn. Các tệp danh sách chia tập do nhóm tạo trong `experiments/splits` có dòng tiêu đề riêng, theo cấu trúc của `src/wmr/dataset.py`.

Việc dùng cờ `reversed` để xoay ảnh là giả định thu hẹp hiện có của mã nguồn: hướng ảnh được biết từ nhãn tham chiếu. Giả định này cần được giữ nhất quán khi so sánh baseline với phương pháp đề xuất.

## 2.5. Các tập dữ liệu sử dụng trong thực nghiệm

Nguồn cập nhật: [issue #1 - Đọc dữ liệu, chia tập phát triển và tập đánh giá](https://github.com/qivarnq3g/cv-water-meter-reading/issues/1), README dự án và các danh sách trong `experiments/splits`.

Thiết kế hiện có sử dụng tập huấn luyện gốc năm chữ số làm tập phát triển, chia tiếp thành phần dựng mẫu (`dev_fit`) và phần chọn tham số (`dev_val`). Tập kiểm tra gốc năm chữ số được giữ làm tập đánh giá (`eval`). Mã chia tập hiện gán ảnh theo mã băm SHA-1 của tên ảnh để có thể tái tạo. Bảng 2.3 thống kê số ảnh và số ảnh có cờ `half-word` trực tiếp từ các tệp CSV của kết quả chia tập.

Bảng 2.3. Số ảnh thực tế của từng tập.

| Tập của dự án | Tập gốc | Danh sách ảnh hiện có | Số ảnh | Số ảnh `half-word` |
|---|---|---|---|---|
| Phát triển, phần dựng mẫu | Tập huấn luyện gốc năm chữ số | `experiments/splits/dev_fit.csv` | 9.577 | 3.399 |
| Phát triển, phần chọn tham số | Tập huấn luyện gốc năm chữ số | `experiments/splits/dev_val.csv` | 2.290 | 836 |
| Đánh giá | Tập kiểm tra gốc năm chữ số | `experiments/splits/eval.csv` | 2.000 | 355 |

Tổng số ảnh của `dev_fit` và `dev_val` là 9.577 + 2.290 = 11.867, khớp tập huấn luyện gốc năm chữ số ở Bảng 2.1; `eval` có 2.000 ảnh, khớp tập kiểm tra gốc. Đối chiếu tên ảnh và tập gốc cho thấy ba danh sách không trùng mẫu. Mọi quyết định chọn tham số phải dựa trên tập phát triển. Tập đánh giá được dùng để báo cáo kết quả sau khi phương pháp và tham số đã được chốt.

## 2.6. Thước đo độ lăn và phân tầng tập đánh giá

Phần này tổng hợp kết quả của issue #3 từ [mã đo độ lăn](../src/wmr/roll.py), [mô tả phương pháp](../experiments/roll/README.md), [danh sách phân tầng](../experiments/roll/eval_roll.csv) và hình minh họa đã có trong dự án. Cường độ thách thức được đo từ vị trí khe nền giữa hai chữ số liên tiếp trong ô cuối, rồi dùng để chia tập đánh giá thành ba tầng nhẹ, trung bình và nặng.

### 2.6.1. Định nghĩa và cách tính thước đo

Khi chữ số gần trạng thái đứng yên, khe nền thường nằm gần mép trên hoặc mép dưới của ô cửa sổ. Khi bánh xe lăn gần nửa bước, khe tiến về giữa ô và hai phần chữ số cùng xuất hiện rõ. Vì vậy, khoảng cách từ khe tới mép gần nhất được dùng làm đại lượng xấp xỉ mức độ lăn.

Đầu vào là ảnh xám vùng đọc năm chữ số, cao 60 × rộng 200 điểm ảnh, đã xoay về hướng đọc theo cờ `reversed` như mô tả ở mục 2.4. Quy trình trong `src/wmr/roll.py` gồm:

1. Cân bằng histogram, sau đó nhị phân hóa thích nghi theo trung bình cục bộ với cửa sổ 15 × 15 điểm ảnh và hằng số trừ 8. Mặt nạ thu được có giá trị 1 ở nét mực và 0 ở nền.
2. Lấy ô chữ số cuối, tương ứng một phần năm chiều rộng ảnh, rồi bỏ 10% ở mỗi bên của ô để giảm ảnh hưởng của vạch khung. Với ảnh rộng 200 điểm ảnh, vùng đo gồm các cột 164-195 theo chỉ số bắt đầu từ 0, rộng 32 điểm ảnh.
3. Tính tỉ lệ điểm mực trên từng hàng của vùng đo và làm trơn dọc bằng bộ lọc Gauss với σ = 1,5 điểm ảnh, thu được hồ sơ hàng `p(y)`.
4. Chọn hàng có giá trị `p(y)` nhỏ nhất làm vị trí khe, sau khi bỏ 5 hàng ở mỗi mép trên và dưới. Nếu nhiều hàng cùng đạt cực tiểu, mã chọn hàng đầu tiên theo chiều từ trên xuống.

Gọi `H` là chiều cao ảnh, `y*` là chỉ số hàng của khe, với hàng đầu tiên có chỉ số 0. Công thức đúng theo mã triển khai là:

$$
y^{*}=\underset{y\in\{5,\ldots,H-6\}}{\operatorname{arg\,min}}\;p(y),
\qquad
R=\frac{\min\bigl(y^{*},\,H-1-y^{*}\bigr)}{(H-1)/2}.
$$

`R` không có đơn vị và nằm trong [0, 1]. Giá trị nhỏ biểu thị khe gần mép, tương ứng mức lăn nhẹ; giá trị lớn biểu thị khe gần giữa ô, tương ứng mức lăn gần nửa bước. Do bỏ biên và sử dụng tọa độ hàng rời rạc, với ảnh cao 60 điểm ảnh, giá trị nhỏ nhất có thể đạt là 10/59 ≈ 0,1695 và lớn nhất là 58/59 ≈ 0,9831. Đây cũng là miền giá trị quan sát được trong tệp phân tầng hiện có. `R` là thước đo xấp xỉ trên ảnh, không phải góc quay hay pha lăn được đo trực tiếp từ cơ cấu đồng hồ.

### 2.6.2. Ngưỡng và quy tắc chia tầng

Hai ngưỡng cố định là 1/3 và 2/3, chia miền độ lăn chuẩn hóa thành ba khoảng. Theo mô tả của issue #3, ngưỡng được đặt theo ý nghĩa hình học của vị trí khe, không chọn theo phân vị để cân bằng số ảnh và không dò theo kết quả trên tập đánh giá. Quy tắc biên thống nhất với hàm `roll_tier`: `R = 1/3` thuộc tầng trung bình, `R = 2/3` thuộc tầng nặng.

Điểm `R` được tính từ ảnh, không dùng nhãn chỉ số hoặc cờ `half-word`; cờ `reversed` chỉ phục vụ giả định biết trước hướng ảnh. Cờ `half-word` được dùng để mô tả thành phần của từng tầng trong Bảng 2.4. Vì một cờ nhị phân và một phép đo liên tục có ý nghĩa khác nhau, tầng nặng không đồng nhất với nhóm ảnh có cờ `half-word`.

### 2.6.3. Phân bố tập đánh giá và hình minh họa

Bảng 2.4 được thống kê bằng cách ghép `experiments/roll/eval_roll.csv` với `experiments/splits/eval.csv` theo tên ảnh. Phần trăm trong cột số ảnh đánh giá tính trên toàn bộ 2.000 ảnh; phần trăm `half-word` tính trong từng tầng.

Bảng 2.4. Phân tầng cường độ lăn trên tập đánh giá.

| Tầng | Điều kiện | Số ảnh đánh giá | Ảnh có cờ `half-word` | Ảnh minh họa |
|---|---|---:|---:|---|
| Nhẹ (`light`) | 0 ≤ R < 1/3 | 437 (21,85%) | 27 (6,2%) | Hàng 1 của Hình 2.1 |
| Trung bình (`medium`) | 1/3 ≤ R < 2/3 | 1.156 (57,80%) | 89 (7,7%) | Hàng 2 của Hình 2.1 |
| Nặng (`heavy`) | 2/3 ≤ R ≤ 1 | 407 (20,35%) | 239 (58,7%) | Hàng 3 của Hình 2.1 |
| Tổng | Toàn bộ tập đánh giá | 2.000 (100,00%) | 355 (17,8%) | - |

Tệp phân tầng có đủ 2.000 tên ảnh duy nhất, khớp hoàn toàn danh sách `eval`; tổng ba tầng là 437 + 1.156 + 407 = 2.000. Không có ảnh bị loại khỏi bảng. Tổng số ảnh `half-word` là 27 + 89 + 239 = 355, khớp Bảng 2.3. Tỉ lệ `half-word` cao hơn ở tầng nặng là một dấu hiệu phù hợp với mục đích của phép đo, nhưng chưa đủ để khẳng định mọi ảnh đều được phân tầng đúng về mặt vật lý.

Hình 2.1. Sáu ảnh minh họa cho mỗi tầng: hàng trên là nhẹ, hàng giữa là trung bình, hàng dưới là nặng. Số phía trên mỗi ảnh là điểm độ lăn `R`, làm tròn đến hai chữ số thập phân. Hình nằm tại `report/figures/roll-tiers.png` và được tạo bằng cách lấy mẫu ngẫu nhiên trong từng tầng với seed 0, rồi sắp các ảnh đã chọn theo điểm tăng dần.

### 2.6.4. Giới hạn và khả năng tái tạo

Phép đo giả định hàng ít nét mực nhất là khe giữa hai chữ số. Khoảng trống bên trong một chữ số, ánh sáng không đều, nét mờ hoặc vạch khung còn sót có thể làm sai vị trí khe. Hình 2.1 có ví dụ chỉ số `02549` (`test1780.jpg`) được xếp tầng nặng với `R = 0,8136`, dù chữ số cuối trông gần trạng thái đứng yên. Vì vậy, các tầng cần được hiểu là phân tầng theo thước đo ảnh; việc kiểm tra ảnh và các yếu tố gây nhiễu vẫn cần thiết khi diễn giải kết quả E1-E4.

Chương trình hiện tại gán tầng cho mọi ảnh đọc được có chiều cao đủ để bỏ biên, chưa có cờ riêng để nhận biết phép đo khe không đáng tin cậy. Nếu ảnh bị thiếu, không giải mã được hoặc quá thấp để tìm khe, chương trình báo lỗi và dừng; không tự bỏ ảnh hay gán điểm thay thế. Trên danh sách kết quả hiện có, mọi ảnh đều có điểm hợp lệ và nhãn tầng phù hợp với hai ngưỡng.

Mỗi dòng trong `experiments/roll/eval_roll.csv` lưu ba trường `name`, `roll` và `tier`. Điểm được ghi với bốn chữ số thập phân, còn nhãn tầng được tính từ giá trị chưa làm tròn. Có thể tái tạo từ thư mục gốc dự án bằng lệnh dưới đây sau khi cài các thư viện và giải nén dữ liệu theo README:

```powershell
$env:PYTHONPATH = "src"
python experiments/make_roll_tiers.py --data-root data
```

Nếu dữ liệu nằm ở nơi khác, thay `data` bằng thư mục chứa `Word-Wheel_Water_Meter_Dataset`.

E1, E3 và phần E4 kiểm tra độ lệch chiều cao chữ số trên ảnh thật dùng thống nhất cách phân tầng của tập `eval`. E2 phân tầng riêng trên `dev_val` bằng cùng phép đo `R` và hai ngưỡng 1/3, 2/3. Phần ảnh lăn tổng hợp của E4 được tạo từ `dev_val`, phân tích theo pha lăn điều khiển φ và đồng thời ghi nhận độ lăn `R` đo được. Các phép so sánh baseline với phương pháp đề xuất trong từng thí nghiệm dùng cùng tập ảnh và thước đo; kết quả phân tầng được báo cáo kèm số ảnh mỗi tầng.

## Tài liệu tham khảo

Xem [danh sách tài liệu tham khảo chung](references.md).
