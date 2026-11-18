# 7. Thiết lập thực nghiệm

## 7.1. Dữ liệu và phân chia tập

Thực nghiệm dùng ảnh vùng hiển thị đã cắt sẵn thuộc phần nhận dạng đồng hồ năm chữ số của [Word-Wheel Water Meter Dataset](data-origin.md). Mỗi ảnh có nhãn chỉ số gồm năm ký tự, giữ cả số 0 ở đầu. Ảnh được đọc ở mức xám và xoay 180° khi nhãn đánh dấu ảnh ngược.

| Tập | Nguồn | Số ảnh | Có cờ `half-word` | Vai trò |
|---|---|---:|---:|---|
| `dev_fit` | Train gốc | 9.577 | 3.399 | Dựng mẫu chữ số từ 6.178 ảnh không có cờ `half-word` |
| `dev_val` | Train gốc | 2.290 | 836 | Chọn thước đo độ lăn, dò tham số và lấy ô nguồn cho E4 tổng hợp |
| `eval` | Test gốc | 2.000 | 355 | Đánh giá trên ảnh thật sau khi chốt tham số |

Ảnh train vào `dev_val` khi SHA-1 của tên ảnh, diễn giải thành số nguyên, có số dư dưới 20 sau khi chia cho 100. Các ảnh train còn lại vào `dev_fit`. Danh sách cố định nằm trong [`experiments/splits/`](../experiments/splits/).

Điểm độ lăn $R$ là khoảng cách từ khe nền sáng trong ô cuối đến mép trên hoặc dưới gần nhất, chia cho nửa chiều cao ô. E1 và E3 báo cáo theo toàn tập và ba tầng sau. E2 dùng cùng ngưỡng để phân tầng `dev_val`. Cờ `half-word` là nhãn nhị phân của bộ dữ liệu, còn tầng được tính từ ảnh theo [thước đo độ lăn](../experiments/roll/README.md).

| Tầng trên `eval` | Khoảng $R$ | Số ảnh | Có cờ `half-word` |
|---|---|---:|---:|
| Nhẹ | $R < 1/3$ | 437 | 27 |
| Trung bình | $1/3 \le R < 2/3$ | 1.156 | 89 |
| Nặng | $R \ge 2/3$ | 407 | 239 |

## 7.2. Thước đo và chọn tham số

Thước đo chính là tỷ lệ đọc đúng chữ số thứ năm. Báo cáo thêm tỷ lệ khớp cả chuỗi năm chữ số, độ chính xác từng vị trí và trung bình độ chính xác của bốn vị trí đầu. Mọi tỷ lệ dùng số ảnh của nhóm tương ứng làm mẫu số. E1 dùng thêm độ sáng trung bình, độ tương phản (độ lệch chuẩn mức xám) và phương sai Laplacian để mô tả chất lượng ảnh giữa các tầng.

Mỗi mẫu chữ số là trung bình các ô tương ứng ở bốn vị trí đầu của các ảnh `dev_fit` đủ điều kiện. Baseline so khớp mẫu bằng tương quan chéo chuẩn hóa. Phương pháp đề xuất giữ nguyên cách đọc bốn vị trí đầu và dùng dải bánh xe tuần hoàn cho ô cuối.

E2 thử 27 tổ hợp trên `dev_val`: bước bánh xe 54/58/62 px, bán kính dịch ngang 2/6/10 px và ngưỡng giải mã pha 0,4/0,5/0,6. Tiêu chí là độ chính xác chữ số cuối trên toàn `dev_val`, ưu tiên tổ hợp xuất hiện trước trong lưới khi bằng điểm. Cấu hình chốt là **58 px, 6 px, 0,4** (45,41%). Phúc kiểm tra thêm các ngưỡng 0,1/0,2/0,3 trên `dev_val` với bước và bán kính đã chọn. Các ngưỡng này cho điểm thấp hơn 0,4. Lệnh `tune` bên dưới tái tạo lưới 27 tổ hợp. Cấu hình, mã băm danh sách ảnh và mẫu chữ số được lưu trước khi đánh giá `eval`. Xem [báo cáo của Phúc](phuc-results.md) và [bảng E2](../experiments/phuc/results/e2_grid.csv).

## 7.3. Quy trình chạy

Cài môi trường Python theo [README của kho](../README.md#cài-đặt) và giải nén [bộ dữ liệu đầy đủ](../data/README.md). Chạy từ thư mục gốc của kho bằng Python trong môi trường đã cài. Các lệnh mặc định tìm dữ liệu trong `data/`. Nếu đặt dữ liệu ở nơi khác, đặt `WMR_DATA_ROOT` trỏ tới thư mục chứa `Word-Wheel_Water_Meter_Dataset`. Khối lệnh dưới đây dùng PowerShell.

```powershell
$env:PYTHONPATH = 'src'
python experiments/make_splits.py
python experiments/make_roll_tiers.py
python experiments/run_phuc.py --stage tune
python experiments/run_phuc.py --stage evaluate
python experiments/run_e3_e4.py --output-dir outputs/section-7/e3-e4
```

1. Hai lệnh đầu tạo lại CSV danh sách ảnh, bảng tầng `experiments/roll/eval_roll.csv` và hình tầng `report/figures/roll-tiers.png`.
2. `tune` chạy E2 và lưu bảng lưới, hình minh họa, `selected.json` và `templates.npy` trong `experiments/phuc/results/`.
3. `evaluate` kiểm tra mã băm của các danh sách ảnh rồi chạy E1 trên `eval`. Thư mục kết quả chứa dự đoán từng ảnh, bảng tổng hợp theo tầng và các thống kê chất lượng ảnh.
4. E3 đọc lại cấu hình và mẫu đã chốt từ `experiments/phuc/results/`. Trên cùng 2.000 ảnh `eval`, E3 so baseline, dải bỏ các pha giữa hai chữ số và dải liên tục, với cùng bán kính dịch 6 px.
5. Cùng script chạy E4 trên 165 cặp ô lấy từ ảnh `dev_val` không gắn cờ `half-word` và có $R < 0{,}21$. Với seed 0, ghép ô $d$ với ô $(d+1) \bmod 10$ sau khi chuẩn hóa độ sáng và độ tương phản của ô thứ hai theo ô thứ nhất. Dịch cửa sổ từ 0 đến 0,50 chiều cao ô, bước 0,05. So sánh phương pháp đề xuất với baseline có bán kính dịch 2, 6 và 10 px. Điểm gãy là pha đầu tiên có tỷ lệ đọc ra $d$ hoặc $(d+1) \bmod 10$ dưới 50%. E4 còn báo cáo sai số pha và kiểm tra trên ảnh thật theo độ lệch chiều cao chữ số so với trung vị (ngưỡng 9%). Kết quả E3/E4 nằm trong `outputs/section-7/e3-e4/`. Xem [thiết lập và giới hạn của E3/E4](../experiments/quang/README.md).

Các lệnh tạo tập, tạo tầng và chạy E1/E2 ghi lại một số tệp đã được theo dõi trong Git. Dùng một bản checkout riêng khi cần giữ nguyên các kết quả trong thư mục làm việc hiện tại.

Đã chạy lại toàn bộ khối lệnh trên Windows với dữ liệu đầy đủ. Danh sách ảnh, bảng phân tầng và các bảng E1–E4 tái lập kết quả đã lưu trong kho, với sai khác dấu phẩy động nhỏ hơn $10^{-6}$ ở các bảng E4 đối chiếu.
