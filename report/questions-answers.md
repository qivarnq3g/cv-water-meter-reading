# Câu hỏi và trả lời khi bảo vệ đề tài

Các câu trả lời bám kết quả E1 tới E4 đã lưu trong kho. Phúc ưu tiên luyện các câu 1 tới 9, đồng thời nắm E3/E4 để giải thích toàn bộ quy trình khi được hỏi.

## 1 Thách thức cụ thể là gì

Khi bánh xe số chuyển tiếp, ô cuối có thể chứa phần của hai chữ số liên tiếp. Mẫu baseline mô tả một chữ số nguyên vẹn nên có thể khớp nhầm với tổ hợp nét. Nhóm nghiên cứu ảnh vùng đọc năm chữ số đã cắt sẵn, chưa giải quyết phát hiện đồng hồ từ ảnh toàn cảnh.

## 2 Vì sao baseline có tìm dịch chuyển mà vẫn sai

Baseline chỉ cho phép dịch nhỏ quanh mẫu đứng yên. Khi hai chữ số cùng hiện trong ô, dịch một mẫu nguyên vẹn không mô tả được cả tổ hợp. Trên ảnh thật, baseline số cuối giảm từ 64,07% ở tầng nhẹ xuống 20,64% ở tầng nặng.

## 3 Thước đo độ lăn tính thế nào và có dùng nhãn không

Nhóm cân bằng histogram, nhị phân hóa thích nghi, lấy ô cuối và bỏ 10% mỗi bên. Tính lượng mực theo hàng, làm trơn rồi chọn hàng ít mực nhất, cách hai mép ít nhất 5 pixel. Điểm R bằng khoảng cách từ hàng đó đến mép gần nhất, chia cho nửa chiều cao ô. Hàm đo chỉ dùng ảnh. Nhãn half-word dùng để đối chiếu trên tập phát triển.

Với chiều cao 60 và lề 5 pixel, giá trị nhỏ nhất thực tế khoảng 0,17. R gần 0,17 vẫn có thể thuộc tầng nhẹ. Khoảng trống của hình dạng chữ số có thể làm khe đo sai.

## 4 Half-word có phải ba tầng độ lăn không

Half-word là cờ nhị phân do bộ dữ liệu cung cấp. Nhóm tự tính R từ ảnh và chia ba tầng bằng ngưỡng 1/3 và 2/3. Tầng eval có 437, 1.156 và 407 ảnh. R là proxy mức lăn, không phải pha vật lý đo chính xác trên mọi đồng hồ.

## 5 Chứng cứ nào cho thấy lỗi tập trung ở độ lăn

Khi số cuối giảm mạnh giữa tầng nhẹ và nặng, trung bình accuracy bốn số đầu không giảm tương ứng. Độ sáng và phương sai Laplacian trung bình ở tầng nặng cũng không thấp hơn tầng nhẹ. Các đối chứng này hỗ trợ giả thuyết khó khăn tập trung ở ô cuối. Vì chưa có ID loại đồng hồ và kiểm định tương đương nhiễu, nhóm chưa loại bỏ mọi giải thích khác.

## 6 Mẫu lấy từ đâu và có rò rỉ nhãn đánh giá không

Mẫu chữ số lấy từ bốn vị trí đầu của 6.178 ảnh không half-word trong dev_fit. Dev_val dùng để chọn tham số. Eval giữ nguyên 2.000 ảnh test gốc. Nhãn chỉ số eval dùng để chấm điểm. Có một giả định dùng thông tin từ nhãn lúc đọc ảnh: cờ reversed cho biết ảnh cần xoay 180 độ. Cần công bố giả định này, không gọi hệ thống là hoàn toàn tự động từ ảnh bất kỳ.

## 7 Vì sao chọn tham số 58 6 và 0,4

Trong lưới 27 tổ hợp trên dev_val, cấu hình pitch 58, max_shift 6, threshold 0,4 đạt accuracy số cuối cao nhất, 45,41%. Nhóm chọn theo toàn dev_val rồi giữ nguyên khi chạy eval. Ba giá trị trong lưới không chứng minh cấu hình tối ưu toàn cục. Báo cáo còn ghi nhận dò thêm ngưỡng dưới 0,4 trên dev_val; lệnh tune hiện tái tạo lưới 27 tổ hợp gốc.

## 8 Độ chính xác 45,41% trên dev_val và 54,45% trên eval có mâu thuẫn không

Hai tập có phân bố độ khó khác nhau. Dev_val có 836/2.290 ảnh half-word, khoảng 36,5%, trong khi eval có 355/2.000, khoảng 17,8%. Điểm eval cao hơn không tự chứng minh rò rỉ dữ liệu. Mọi quyết định chọn tham số phải giữ trên dev_val và công bố vai trò từng tập.

## 9 Phương pháp cải thiện bao nhiêu

Accuracy số cuối toàn eval tăng 48,25% lên 54,45%, tức 6,20 điểm phần trăm. Tầng nặng tăng 20,64% lên 28,75%, tức 8,11 điểm phần trăm. Cả chỉ số tăng 37,15% lên 42,10%, tức 4,95 điểm phần trăm. Ghép cặp theo tên ảnh cho KTC Wald 95% của hiệu toàn eval từ 4,42 tới 7,98 điểm phần trăm, McNemar chính xác p khoảng 1,1 × 10⁻¹¹ (230 ảnh chỉ đề xuất đúng và 106 ảnh chỉ baseline đúng). Tầng nặng: KTC 4,25 tới 11,97 điểm, p khoảng 6,7 × 10⁻⁵. Tầng nhẹ tăng 0,69 điểm, KTC -2,58 tới 3,95, p khoảng 0,78 nên chưa có bằng chứng cải thiện ở mức ý nghĩa 0,05. Không suy ra tương đương hoặc không gây hại từ kết quả không có ý nghĩa. Phép so coi ảnh là đơn vị độc lập, chưa hiệu chỉnh nhiều kiểm định theo tầng và không phản ánh biến thiên chọn tham số. Công thức và thống kê trong report/make_figures.py được đối chiếu lại từ e3_predictions.csv; notebook notebooks/phuc_experiments.ipynb đã thêm ô tính lại trực tiếp.

## 10 Phương pháp thay đổi đại lượng nào trong ảnh

Phương pháp mở rộng tập mẫu có thể khớp ở ô cuối. Thay mười ảnh chữ số rời bằng dải tuần hoàn chứa các mẫu 0 tới 9 và tìm cửa sổ có NCC cao nhất trên dải. Vị trí cửa sổ cho pha liên tục rồi ngưỡng giải mã pha thành nhãn. Bốn vị trí đầu giữ nguyên baseline.

## 11 Tắt enabled và continuous khác nhau thế nào

`enabled=False` trả về baseline cùng max_shift. `continuous=False` vẫn dùng dải nhưng chỉ giữ pha cách tâm chữ số không quá max_shift, bỏ các pha giữa hai chữ số. E3 so ba phiên bản để phân biệt thay đổi cấu trúc dải với đóng góp của pha trung gian.

Trên tầng nặng, bỏ pha trung gian đạt 21,38%, gần baseline 20,64% và thấp hơn đề xuất đầy đủ 28,75%. Tầng nhẹ lại có bản bỏ pha đạt 65,90%, cao hơn đề xuất 64,76%, nên không nói pha liên tục luôn tốt hơn ở mọi tầng.

## 12 E4 đo gì và điểm gãy là gì

E4 ghép 165 cặp ô từ dev_val và quét pha từ 0 tới 0,5, bước 0,05. Tiêu chí trên đường cong là tỉ lệ đọc ra d hoặc (d+1) mod 10. Điểm gãy theo quy ước thực nghiệm là pha đầu tiên có tỉ lệ này dưới 50%. Baseline bán kính 2, 6, 10 gãy ở 0,10, 0,20, 0,30. Không so trực tiếp tiêu chí E4 với accuracy nhãn thật của E1/E3.

## 13 Đề xuất có không bao giờ gãy không

Trong miền pha tổng hợp đã khảo sát, tỉ lệ đọc ra d hoặc d+1 của đề xuất chưa xuống dưới 50%. Tuy nhiên sai số pha trung vị tăng từ khoảng 0,128 ở pha 0,30 lên 0,707 ở pha 0,50. Trên ảnh thật tầng nặng cũng chỉ đúng 28,75%. Kết quả không chứng minh hệ thống hoạt động tốt ở mọi mức lăn.

## 14 Dự đoán nào được ủng hộ và dự đoán nào chưa đúng

Điểm gãy baseline dịch đúng chiều khi tăng bán kính nhưng xuất hiện muộn hơn s/p. Đề xuất giữ trên 50% theo tiêu chí tổng hợp trong miền khảo sát, nhưng không phẳng theo tầng trên ảnh thật. Dự đoán phần lớn lỗi lệch một chữ số không được ủng hộ: tầng nặng chỉ 73/290 lỗi, khoảng 25,17%. Kiểm tra ảnh thật về chiều cao vẫn chưa kết luận được vì chỉ 18 ảnh tầng nặng thuộc nhóm xa. Phép quét lệch bước tổng hợp bổ sung cho thấy suy giảm định vị sớm hơn khi bước dài hơn từ 10%, nên báo cáo cập nhật dự đoán 4 thành đúng một phần, không coi ngưỡng 9% đã được xác nhận chính xác.

## 15 Chiều quay của bánh xe đã xác định được chưa

Chưa. Kiểm tra 836 ảnh half-word dev_val cho NCC trung bình dải xuôi khoảng 0,4203 và dải ngược 0,4212. Hai giá trị gần nhau. Không dùng phép thử này để khẳng định dải đã mô tả đúng chiều chuyển động vật lý của mọi đồng hồ.

## 16 Vì sao không dùng mô hình OCR hoặc mạng học sâu

Phạm vi bài tập yêu cầu thành phần xử lý thách thức do nhóm xây dựng, còn mô hình dựng sẵn chỉ dùng như tiện ích hoặc baseline. Nhóm thích nghi bước dựng mẫu và tìm pha của so khớp NCC để giải thích cơ chế và kiểm tra bằng E3/E4. Chưa có thực nghiệm so sánh OCR hay mạng học sâu trong kết quả hiện tại, nên không kết luận phương pháp tốt hơn chúng.

## 17 Có thể chứng minh 165 cặp là các mẫu độc lập không

Không. E4 dùng lại ô từ một kho nhỏ, trong đó số 7 chỉ có 7 ô nguồn. Hai ô của một cặp còn có thể đến từ hai đồng hồ khác nhau. Các cặp giúp kiểm tra cơ chế trên cách tổng hợp đã định, không thay thế đánh giá độc lập trên ảnh thật.

## 18 Notebook chạy được có nghĩa là tái lập toàn bộ thí nghiệm chưa

Notebook đọc CSV, JSON và hình đã lưu, tính lại bảng/đồ thị và kiểm tra nhất quán. Restart & Run All xác nhận quy trình trình bày kết quả hoạt động. Để tái lập toàn bộ trên ảnh cần chạy các script E1/E2/E3/E4 với bộ dữ liệu đầy đủ và cấu hình tương ứng.

## 19 Nên cải thiện tiếp ở đâu

Kết quả gợi ý kiểm tra mẫu bị nhòe và khác kiểu chữ, chiều quay và pitch chung. Đây là hướng phát triển, chưa phải nguyên nhân lỗi đã chứng minh. Một vòng cải tiến tiếp theo phải chọn tham số trên tập phát triển và công bố việc tập eval hiện tại đã được xem.

## Nguồn để đối chiếu khi tập

- [`report/experimental-setup.md`](experimental-setup.md): tập dữ liệu, thước đo và cách chạy.
- [`experiments/phuc/results/summary.csv`](../experiments/phuc/results/summary.csv) và [`e2_grid.csv`](../experiments/phuc/results/e2_grid.csv): E1/E2.
- [`experiments/quang/README.md`](../experiments/quang/README.md), [`e3_summary.csv`](../experiments/quang/results/e3_summary.csv), [`e4_curve.csv`](../experiments/quang/results/e4_curve.csv): E3/E4.
- [`src/wmr/roll.py`](../src/wmr/roll.py) và [`src/wmr/proposed.py`](../src/wmr/proposed.py): thước đo và cơ chế.

## Slide dự phòng khi trả lời

Đối chiếu bản 14 slide của PR #30 tại commit `1da0593`: slide 11 về chiều quay, slide 12 về giới hạn ảnh tổng hợp, slide 13 về ngưỡng 0,4 và slide 14 về sai số pha. Mười slide chính giữ số 1 tới 10. Kiểm lại số slide nếu nhóm chỉnh cấu trúc trước buổi bảo vệ.

## 20 Kết quả E4 bổ sung thay đổi kết luận gì

Phép quét trên 165 bộ ba giữ nguyên cấu hình mô hình và thay bước thật từ -20% tới +20%. Nếu lấy trung vị sai số pha >0,25 làm tiêu chí, P gãy khoảng pha 0,4 khi bước khớp, 0,3 khi bước dài hơn từ 10%, và cả ở pha nhỏ khi bước ngắn hơn từ 15%. Tiêu chí 0,25 được chọn sau khi xem phép quét ban đầu, nên cần gọi là thăm dò.

Theo tiêu chí định trước đọc ra d hoặc d+1 dưới 50%, lần đầu quan sát ở +15% và -20%. Giá trị 49,09% tại +15% có KTC 41,6 tới 56,7%, chưa phân biệt chắc chắn với 50%. Phép co giãn đồng thời thay bước và cỡ chữ; các bộ ba dùng lại ô nguồn. Dự đoán 4 chuyển thành đúng một phần nhờ phép tổng hợp, còn kết quả ảnh thật vẫn chưa kết luận.
