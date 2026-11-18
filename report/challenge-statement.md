# Tuyên bố thách thức

## A. Bối cảnh và thách thức

### Tác vụ

Đọc chỉ số đồng hồ nước cơ loại bánh xe số từ ảnh chụp vùng hiển thị. Nhân viên ghi chỉ số chụp ảnh đồng hồ ở từng hộ, rồi chỉ số được nhập để tính tiền nước. Đọc tự động giúp giảm nhập tay và cho phép đối chiếu lại khi có khiếu nại. Chữ số cuối là chữ số đổi thường xuyên nhất, nên sai ở chữ số này làm sai chỉ số ở rất nhiều lần ghi.

### Dữ liệu

Phần nhận dạng năm chữ số của bộ Word-Wheel Water Meter Dataset (chi tiết ở mục 2 của báo cáo). Ảnh chụp thực tế khi ghi chỉ số tại Hàng Châu, Trung Quốc, đã được tác giả cắt và nắn phối cảnh về 60 x 200 điểm ảnh. Tập phát triển gồm 11.867 ảnh, tập đánh giá gồm 2.000 ảnh.

### Thách thức C: chữ số cuối đang lăn

Bánh xe số quay liên tục. Khi ảnh được chụp lúc bánh xe đang chuyển từ d sang d + 1, ô cửa sổ chỉ cho thấy phần dưới của d, khe nền giữa hai chữ số và phần trên của d + 1. Đây là một dạng che khuất do chính cơ cấu đồng hồ: khung cửa sổ che mất một phần của mỗi chữ số. Cường độ của C là pha lăn φ, tính bằng phần bước bánh xe đã đi qua (φ = 0 khi chữ số nằm giữa ô, φ = 0.5 khi hai chữ số chia đôi ô). Trên ảnh, φ được đo bằng vị trí khe nền trong ô cuối (`src/wmr/roll.py`). Thước đo này xấp xỉ 2φ và dùng để chia tập đánh giá thành ba tầng nhẹ, trung bình, nặng.

### Kiểu hạn chế F

Cách làm thông thường là chia ảnh thành năm ô bằng nhau rồi so khớp mỗi ô với mười mẫu chữ số đứng yên bằng tương quan chéo chuẩn hóa (normalized cross-correlation, NCC), cho phép trượt tối đa 6 điểm ảnh. Khi chữ số cuối lăn, không mẫu nào giống nội dung ô, và mẫu có điểm cao nhất gần như ngẫu nhiên. Trên tập đánh giá, baseline đọc đúng chữ số cuối 64.1% ở tầng nhẹ, 52.0% ở tầng trung bình và 20.6% ở tầng nặng. Lỗi ở ảnh có cờ `half-word` phần lớn ra một chữ số không liên quan: chỉ 63 trong 310 lỗi là chữ số kề bên. Bốn chữ số đầu ít khi lăn, và baseline đọc đúng chúng 85% tới 96%.

### Giả định thu hẹp

- Vùng hiển thị đã được cắt và nắn phẳng, nên góc nhìn và tỉ lệ được cố định. Tác giả bộ dữ liệu đã làm bước này, và nó không gỡ bỏ C vì việc lăn xảy ra bên trong ô cửa sổ.
- Hướng ảnh biết trước từ cờ `reversed`. Ảnh lộn ngược được xoay lại trước mọi bước.
- Chỉ xét đồng hồ năm chữ số, và năm ô có độ rộng bằng nhau.
- Ánh sáng, mờ và bẩn không được cố định. Chúng được giữ ở mức phân bố tự nhiên của dữ liệu, và E1 phải kiểm tra rằng ba tầng không khác nhau đáng kể theo các chiều này.

## B. Lý thuyết của giải pháp

### Kỹ thuật P: so khớp trên dải bánh xe tuần hoàn

Thay mười mẫu rời bằng một dải mẫu liên tục mô phỏng mặt bánh xe trải phẳng: mẫu các chữ số 0, 1, ..., 9 xếp chồng theo đúng thứ tự trên bánh xe, cách nhau một bước p, và nối vòng (sau 9 là 0). Dải dài 10p. Với ô chữ số cuối, trượt một cửa sổ cao bằng ô dọc theo dải và tính NCC ở mọi độ dời y trong [0, 10p), kèm trượt ngang nhỏ như baseline. Độ dời tốt nhất y* cho pha liên tục r = y*/p. Phần nguyên của r là chữ số đang ở ô, phần lẻ là pha lăn. Chỉ số đọc ra là d = floor(r + 1 - t) mod 10, trong đó t là ngưỡng chuyển nhãn sang chữ số kế tiếp. Ngưỡng t được chọn trên tập phát triển cho khớp quy ước gán nhãn (ảnh lăn đúng nửa được ghi chữ số nhỏ hơn).

Bước p và mẫu từng chữ số được ước lượng từ các ô đứng yên của tập phát triển. Đo sơ bộ trên `dev_val`: chữ số đứng yên cao khoảng 54 điểm ảnh, khe giữa hai chữ số khoảng 4 điểm ảnh, nên p khoảng 58 điểm ảnh, gần bằng chiều cao ô.

### Cơ chế

Đại lượng mà C phá hỏng là độ trùng khớp giữa nội dung ô và mẫu. Mẫu của baseline chỉ mô tả pha φ = 0. Nội dung ô ở pha φ là đoạn [(d + φ)p, (d + φ)p + 60) của mặt bánh xe. Với mẫu d, phần chồng lên nhau sau khi trượt tốt nhất chỉ còn chừng (1 - φ) chiều cao ô, nên NCC giảm theo φ. Phần còn lại của ô (đầu chữ số d + 1) là nhiễu đối với mẫu d. Khi φ đủ lớn, một mẫu khác có hình dạng tình cờ giống tổ hợp này sẽ thắng.

P thay đổi tập giả thuyết chứ không thay bước so khớp. Với mọi φ, nội dung ô là một đoạn liên tục của dải, nên luôn có một độ dời y mà cửa sổ trên dải trùng với ô (sai khác chỉ do nhiễu, ánh sáng và khác biệt giữa các đồng hồ). Pha lăn từ chỗ là nhiễu trở thành một tham số được tìm. P còn dùng một ràng buộc vật lý mà baseline bỏ qua: phần dưới của d luôn đi liền với phần trên của d + 1. Hai nửa được so khớp cùng nhau, nên một cặp sai thứ tự (ví dụ phần dưới của 3 với phần trên của 7) không bao giờ là giả thuyết.

Nền tảng môn học: so khớp mẫu bằng tương quan chéo chuẩn hóa, và tìm kiếm phép tịnh tiến bằng cực đại tương quan. Phần nhóm sửa là bước dựng mẫu: từ mười mẫu rời thành một dải tuần hoàn có thứ tự, và đổi kết quả từ một nhãn rời thành một pha liên tục. Vì vậy P thuộc mức 2 trên thang tính mới (thích nghi một bước của thuật toán, kèm lập luận cơ chế). Các dự đoán định lượng dưới đây nhằm đạt mức 3.

### Dự đoán điểm gãy

Viết trước khi cài đặt P. Ký hiệu s = 6 là bán kính trượt dọc của baseline, p khoảng 58 là bước bánh xe, w khoảng 5 là bề rộng nét chữ (cùng đo trên `dev_val`).

1. Baseline gãy ở φ khoảng s/p, tức khoảng 0.10. Phép trượt ±s bù được độ lăn tới s điểm ảnh. Sau đó, phần chồng lên mẫu đúng giảm dần và NCC của mẫu đúng mất ưu thế. Trên thước đo độ lăn (khoảng 2φ), điểm gãy nằm quanh 0.2, tức là ngay ở đầu tầng nhẹ. Hệ quả kiểm chứng được: tăng s thì điểm gãy dời theo tỉ lệ s/p.
2. P không gãy theo φ ở tầng nhẹ và tầng trung bình. Độ chính xác chữ số cuối của P ở hai tầng này chênh nhau không quá vài điểm phần trăm, khác với mức chênh 12 điểm của baseline.
3. Lỗi của P dồn quanh ngưỡng chuyển nhãn. Sai số định vị của đỉnh NCC cỡ nửa bề rộng nét, khoảng w/2 điểm ảnh. Ảnh có |φ - t| < w/(2p), khoảng 0.04, có thể bị đọc sang chữ số kề bên. Nếu t gần 0.5, dải rủi ro này nằm trọn trong tầng nặng. Pha của tầng nặng trải từ khoảng 0.33 tới 0.67, nên dải rủi ro chiếm khoảng 0.08/0.33, tức chừng một phần tư số ảnh của tầng. Dự đoán: độ chính xác của P ở tầng nặng thấp hơn hai tầng kia chừng 10 tới 25 điểm phần trăm, và phần lớn lỗi là lệch đúng một chữ số (d thay cho d + 1 hoặc ngược lại). Ở baseline, loại lỗi này chiếm 24% số lỗi chữ số cuối (252 trên 1.035).
4. P gãy khi bước thật của đồng hồ khác p. Dải dùng một bước p chung cho mọi đồng hồ. Nếu bước thật lệch Δp, thì ở pha lăn lớn, phần trên của d + 1 lệch Δp so với dải trong khi phần dưới của d vẫn khớp. Khi |Δp| vượt khoảng w (5 điểm ảnh, tức khoảng 9% của p), hai nửa không còn khớp cùng một y và đỉnh NCC tách đôi. Dự đoán: ở tầng nặng, độ chính xác của P giảm rõ ở các ảnh mà chiều cao chữ số (đo trên bốn chữ số đầu) lệch quá 9% so với trung vị. Ở tầng nhẹ thì không, vì khi đó gần như cả ô thuộc về một chữ số.

E4 kiểm tra dự đoán 1 và 3 bằng cách làm nặng C có kiểm soát: ghép hai ô chữ số đứng yên liên tiếp của tập phát triển thành ảnh lăn tổng hợp, quét φ từ 0 tới 0.5 với bước 0.05, giữ nguyên mọi yếu tố khác. Dự đoán 4 được kiểm tra trên ảnh thật, bằng cách chia tầng nặng theo độ lệch chiều cao chữ số.

## C. Tiêu chí kiểm chứng

### Thước đo định lượng

Độ chính xác chữ số cuối, báo cáo theo từng tầng (nhẹ 437, trung bình 1.156, nặng 407 ảnh trên tập đánh giá). Báo cáo kèm độ chính xác cả chỉ số và độ chính xác bốn chữ số đầu, để thấy P không làm hỏng các vị trí không lăn. Với lỗi chữ số cuối, báo cáo thêm tỉ lệ lỗi lệch đúng một chữ số để kiểm tra dự đoán 3. Ngưỡng t, bước p và mọi tham số khác chọn trên `dev_val`. Tập đánh giá chỉ chạy một lần cho mỗi cấu hình đã chốt.

### Baseline

So khớp mẫu chữ số đứng yên bằng NCC trên năm ô bằng nhau (`src/wmr/baseline.py`, issue #1). P dùng chung bước tiền xử lý, cách chia ô và mẫu chữ số với baseline, chỉ khác ở dải tuần hoàn và bước giải mã pha. Nhờ vậy, E3 tắt đúng thành phần xử lý C bằng một tham số: thay dải bằng mười mẫu rời thì P trở lại đúng baseline.
