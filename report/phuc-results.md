# Kết quả thực nghiệm của Phúc - 15/11/2026

## Dữ liệu và quy trình

Đã giải nén bản Dryad vào `data/Word-Wheel_Water_Meter_Dataset/`, đủ detection và recognition. ZIP SHA-256: `3b7d3d8168ab924314a7c71987ce09f54dec95818a9cb484b46ea804fc1d90e6`, khớp metadata Dryad đã đọc. Ba tập có 9.577/2.290/2.000 ảnh, không thiếu tệp. Đo lại độ lăn trên toàn bộ eval cho nhãn tầng trùng 100% CSV của PR #21: 437 nhẹ, 1.156 trung bình, 407 nặng.

Mẫu chữ số lấy từ 6.178 ảnh dev_fit không half-word. Dò 27 cấu hình trên dev_val, chốt pitch=58, max_shift=6, threshold=0.4 rồi mới đánh giá eval; không chọn lại tham số từ eval. Fingerprint split lưu trong selected.json. Ngưỡng 0.4 là biên dưới của miền khảo sát; dò thêm trên dev_val (pitch 58, shift 6) cho 0.3 là 45,20%, 0.2 là 43,67%, 0.1 là 37,64%, nên 0.4 là cực đại.

## E1 và đánh giá phương pháp

| Phương pháp | Tầng | n | Đúng số cuối (%) | Đúng cả chỉ số (%) | Trung bình bốn số đầu (%) |
|---|---|---:|---:|---:|---:|
| baseline | all | 2000 | 48.25 | 37.15 | 89.91 |
| baseline | light | 437 | 64.07 | 51.49 | 88.62 |
| baseline | medium | 1156 | 51.99 | 39.45 | 90.10 |
| baseline | heavy | 407 | 20.64 | 15.23 | 90.79 |
| proposed | all | 2000 | 54.45 | 42.10 | 89.91 |
| proposed | light | 437 | 64.76 | 51.95 | 88.62 |
| proposed | medium | 1156 | 59.60 | 45.59 | 90.10 |
| proposed | heavy | 407 | 28.75 | 21.62 | 90.79 |

Baseline số cuối giảm từ 64,07% xuống 20,64% giữa tầng nhẹ và nặng (43,43 điểm phần trăm), trong khi bốn số đầu không giảm tương ứng (88,62% và 90,79%). Đây là chứng cứ thách thức tập trung ở ô cuối. Độ sáng trung bình tăng 168,97→173,00; tương phản 38,95→39,98; Laplacian variance 605,83→653,46. Tầng nặng không tối hơn hoặc mờ hơn theo các proxy này. Tuy vậy chưa có kiểm định tương đương và không có ID loại đồng hồ: không tuyên bố đã loại bỏ mọi yếu tố gây nhiễu. Bảng theo chữ số đúng nằm ở e1_by_digit.csv để kiểm tra ảnh hưởng phân bố chữ số.

P cải thiện số cuối 6,20 điểm phần trăm toàn tập, 8,11 điểm ở tầng nặng; cả chuỗi tăng 4,95 điểm. Bốn số đầu giữ nguyên từng dự đoán vì chỉ thay bước nhận dạng ô cuối. Các giá trị là ước lượng điểm, chưa có khoảng tin cậy.

Kết quả cũng không ủng hộ toàn bộ dự đoán trong PR #22: P vẫn giảm từ 64,76% ở tầng nhẹ xuống 28,75% ở tầng nặng. Chỉ 223/911 lỗi số cuối của P lệch một số (24,48%), nên chưa đúng dự đoán phần lớn lỗi là chữ số kề bên. Không sửa dự đoán sau khi xem eval. Mẫu trung bình bị nhòe, kiểu chữ khác nhau, bước bánh xe chung và chiều quay cố định là những khả năng cần kiểm tra ở thí nghiệm phát triển tiếp theo, chưa phải nguyên nhân đã chứng minh.

## E2 - ảnh hưởng tham số

27 cấu hình và accuracy từng tầng trên dev_val ở e2_grid.csv. Cấu hình tốt nhất đạt 45,41% số cuối (nhẹ 59,55%, trung bình 54,23%, nặng 25,89%).

- Giữ pitch=58, threshold=0.4: shift 2/6/10 cho 37,64% / 45,41% / 43,45%. Tăng từ 2 tới 6 giúp bù lệch; tăng lên 10 giảm accuracy, phù hợp khả năng có thêm vị trí khớp nhầm nhưng chưa chứng minh cơ chế này.
- Giữ shift=6, threshold=0.4: pitch 54/58/62 cho 44,98% / 45,41% / 45,11%. Bước 58 tốt nhất toàn tập, còn tầng nặng tốt nhất trong ba cấu hình này là pitch 62 (27,28%); chọn theo tiêu chí toàn dev_val đã định trước.
- Giữ pitch=58, shift=6: threshold 0.4/0.5/0.6 cho 45,41% / 45,20% / 44,98%. Chênh lệch nhỏ, chưa đủ khẳng định mạnh về quy ước nhãn.

Ảnh trung gian raw, cân bằng histogram, ô cuối và cửa sổ dải khớp đặt cạnh nhau trong e2_intermediates.png. Ba ảnh chọn bằng vị trí cố định trong dev_val, không lựa theo kết quả eval.

## Notebook và phần còn lại

Notebook phuc_experiments.ipynb tổng hợp E1/E2 từ CSV thật, có đồ thị và nhận xét. E3/E4 vẫn chờ kết quả của Quang; notebook báo rõ phần chưa có. Vì thế #16 chưa được coi là hoàn tất toàn bộ E1 tới E4. Mã P là bản thực hiện để nhóm review, chưa thay cho việc cả nhóm chốt PR #22. Không đóng issue hay gộp PR tự động.
