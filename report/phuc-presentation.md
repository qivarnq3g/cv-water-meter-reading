# Phần trình bày của Phúc

Phúc trình bày cách phân tầng độ lăn, chứng cứ E1 và khảo sát E2. Bản lời nói dưới đây dự kiến khoảng bốn phút, để nhóm dùng khi tập ngày 24/11. Thời lượng và việc giao slide là đề xuất để nhóm chốt, chưa thay cho phân công người nói của cả nhóm.

## Mạch trình bày theo slide

| Slide trong PR #30 | Phần nói của Phúc | Thời lượng dự kiến |
|---|---|---:|
| 3 | Dữ liệu, thước đo và ba tầng | 60 giây |
| 5 | E1 và kết quả trên ảnh thật | 90 giây |
| 6 | E2 và cấu hình chọn trên dev_val | 60 giây |
| Chuyển phần | Giới thiệu mục đích E3/E4 cho người tiếp theo | 30 giây |

Đã đối chiếu lại bộ 14 slide tại commit `1da0593`: mười slide chính giữ số 1 tới 10, bốn slide dự phòng ở 11 tới 14. Phần Phúc vẫn dùng slide 3, 5, 6. Slide 6 hiện là bảng màu chín cấu hình tại ngưỡng 0,4, còn việc dò thêm ngưỡng dưới 0,4 nằm ở slide dự phòng 13.

Nguồn slide: [PR #30](https://github.com/qivarnq3g/cv-water-meter-reading/pull/30). Notebook đầy đủ E1 tới E4 ở [`notebooks/phuc_experiments.ipynb`](../notebooks/phuc_experiments.ipynb). Các bảng gốc đã có trên main.

## Lời nói cho slide 3

“Phần thực nghiệm dùng ảnh vùng hiển thị đồng hồ năm chữ số, kích thước 60 nhân 200. Nhóm giữ nguyên tập test gốc gồm 2.000 ảnh để đánh giá. Tập train chia thành 9.577 ảnh dựng mẫu và 2.290 ảnh chọn tham số. Trong tập dựng mẫu, nhóm chỉ lấy 6.178 ảnh không có cờ half-word, và chỉ lấy bốn ô đầu để tạo mẫu chữ số.

Để đo mức độ lăn, nhóm tìm khe nền sáng trong ô cuối qua phân bố mực theo hàng. Khe càng gần giữa ô thì điểm độ lăn càng cao. Hai ngưỡng cố định một phần ba và hai phần ba chia tập đánh giá thành 437 ảnh nhẹ, 1.156 ảnh trung bình và 407 ảnh nặng. Cờ half-word là nhãn tham khảo riêng, không phải tiêu chí trực tiếp chia ba tầng.

Cách đo vẫn có thể nhầm khoảng trống bên trong chữ số thành khe. Vì thế nhóm báo cáo giới hạn này và kiểm tra thêm bằng ảnh lăn tổng hợp ở E4.”

## Lời nói cho slide 5

“Trước hết xem baseline ở cùng vị trí chữ số cuối. Accuracy giảm từ 64,07% ở tầng nhẹ xuống 20,64% ở tầng nặng. Trong khi đó, trung bình accuracy của bốn vị trí đầu là 88,62% và 90,79%, không giảm tương ứng. Những chỉ báo về độ sáng và độ nét cũng không cho thấy tầng nặng tối hơn hoặc mờ hơn.

Kết quả này hỗ trợ nhận định khó khăn tập trung ở ô cuối đang lăn. Tuy vậy, nhóm chưa có ID loại đồng hồ để kiểm soát hết yếu tố gây nhiễu, nên không kết luận độ lăn là nguyên nhân duy nhất.

Phương pháp dải tuần hoàn tăng accuracy số cuối trên toàn tập từ 48,25% lên 54,45%, tức tăng 6,20 điểm phần trăm. Ở tầng nặng, mức tăng là 8,11 điểm phần trăm. Accuracy cả chuỗi tăng từ 37,15% lên 42,10%. Bốn số đầu giữ nguyên cách nhận dạng. KTC 95% của mức tăng toàn tập từ 4,42 tới 7,98 điểm phần trăm, McNemar p khoảng 1,1 nhân 10 mũ trừ 11. Riêng tầng nhẹ p khoảng 0,78, nên chưa có bằng chứng cải thiện. Tầng nặng vẫn chỉ đúng 28,75%, nên cần xét cả mức tăng và accuracy tuyệt đối.”

## Lời nói cho slide 6

“Để chọn tham số, nhóm thử 27 tổ hợp trên dev_val: ba bước bánh xe 54, 58, 62 pixel; ba bán kính dịch ngang 2, 6, 10 pixel; và ba ngưỡng nhãn 0,4, 0,5, 0,6.

Tiêu chí chọn là accuracy số cuối trên toàn dev_val, không chọn theo kết quả eval. Trong lưới này, cấu hình 58 pixel, dịch ngang 6 pixel và ngưỡng 0,4 đạt cao nhất, 45,41%. Slide đang hiển thị chín ô tại ngưỡng 0,4; bảng đầy đủ 27 tổ hợp có trong notebook. Nếu hỏi vì sao chọn ngưỡng ở biên, dùng slide dự phòng 13: các mức 0,3, 0,2 và 0,1 thấp hơn 0,4 trong các mức đã thử.

Ví dụ giữ hai tham số còn lại: dịch ngang từ 2 lên 6 cải thiện accuracy từ 37,64% lên 45,41%, nhưng tăng tiếp lên 10 giảm còn 43,45%. Dò rộng hơn không luôn tốt hơn vì có thêm cơ hội khớp nhầm. Đây là cách diễn giải phù hợp với số liệu, chưa phải một cơ chế đã được kiểm chứng riêng.

Sau khi chọn, nhóm giữ nguyên cấu hình và mẫu cho đánh giá ảnh thật cũng như E3/E4.”

## Câu chuyển phần

“E1 cho thấy điểm yếu tập trung ở số cuối, còn E2 xác định cấu hình trên tập phát triển. Tiếp theo, E3 tắt riêng pha trung gian để xem phần cải thiện đến từ đâu. E4 tăng pha lăn có kiểm soát để kiểm tra điểm gãy và đối chiếu các dự đoán đã viết trước thực nghiệm.”

## Nếu cần trình bày notebook

Mở [`notebooks/phuc_experiments.ipynb`](../notebooks/phuc_experiments.ipynb) trong repo. Chạy Restart & Run All trước buổi tập, sau đó dùng các mục E1, E2, E3 và E4 để chuyển tới bảng tương ứng. Không chạy lại tune/evaluate khi đang thuyết trình vì các lệnh đó cần bộ ảnh đầy đủ và ghi lại kết quả.

Nếu máy không có kernel phù hợp, dùng các bảng CSV và hình đã lưu trong repo. Notebook chỉ đọc kết quả và kiểm tra nhất quán, không phải bản ghi một lần chạy lại toàn bộ ảnh trong buổi trình bày.

## Các con số cần nhớ

| Ý nghĩa | Giá trị |
|---|---|
| Accuracy số cuối trên eval | Baseline 48,25%, đề xuất 54,45% |
| Accuracy số cuối ở tầng nặng | Baseline 20,64%, đề xuất 28,75% |
| Accuracy cả chỉ số trên eval | Baseline 37,15%, đề xuất 42,10% |
| Cấu hình chọn trong 27 tổ hợp | Pitch 58, dịch ngang 6, ngưỡng 0,4 |
| KTC 95% của mức tăng số cuối toàn eval | 4,42 tới 7,98 điểm phần trăm, McNemar p khoảng 1,1 × 10⁻¹¹ |
| KTC 95% của mức tăng ở tầng nặng | 4,25 tới 11,97 điểm phần trăm, p khoảng 6,7 × 10⁻⁵ |
| Tầng nhẹ | +0,69 điểm phần trăm, p khoảng 0,78, chưa có bằng chứng cải thiện |
| Bỏ pha trung gian ở tầng nặng | 21,38%, so với 28,75% khi đầy đủ |
| Điểm gãy E4 của baseline ±2, ±6, ±10 | Pha 0,10; 0,20; 0,30 |

Các số liệu E1/E2 lấy từ [`summary.csv`](../experiments/phuc/results/summary.csv) và [`e2_grid.csv`](../experiments/phuc/results/e2_grid.csv). E3/E4 lấy từ [`e3_summary.csv`](../experiments/quang/results/e3_summary.csv), [`e4_curve.csv`](../experiments/quang/results/e4_curve.csv) và [`e3_e4_report.json`](../experiments/quang/results/e3_e4_report.json).

Thống kê ghép cặp từ `experiments/quang/results/e3_predictions.csv`, theo công thức trong report/make_figures.py. KTC coi ảnh là đơn vị độc lập và chưa phản ánh biến thiên chọn tham số. Các phép so theo tầng chưa hiệu chỉnh nhiều kiểm định. Bốn slide dự phòng: 11 chiều quay, 12 ảnh tổng hợp, 13 ngưỡng nhãn, 14 sai số pha.

## Kết quả E4 bổ sung khi hỏi đáp

Giải thích riêng hai tiêu chí gãy. Theo định vị pha >0,25 (tiêu chí thăm dò), pha gãy khoảng 0,4 khi bước khớp và sớm về 0,3 khi bước dài hơn từ 10%. Theo tỷ lệ đọc d hoặc d+1 dưới 50% (tiêu chí định trước), quan sát đầu tiên ở +15% và -20%, nhưng KTC tại +15% còn chứa 50%. Không khẳng định ngưỡng gãy vật lý 9% đã được chứng minh. Báo cáo cập nhật dự đoán 4 thành đúng một phần dựa trên tổng hợp; kiểm tra ảnh thật vẫn chưa kết luận.
