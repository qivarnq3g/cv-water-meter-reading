# Dữ liệu

Kho này không chứa bộ dữ liệu đầy đủ (tệp nén khoảng 2,6 GB). Thư mục `data/` bị bỏ qua trong Git, trừ tệp này và `data/sample/`.

## Tải về

1. Mở trang Dryad của bộ Word-Wheel Water Meter Dataset: <https://doi.org/10.5061/dryad.7d7wm3860>.
2. Bấm nút "Download full dataset" trong trình duyệt. Mở gói `doi_10_5061_dryad_7d7wm3860__v20260130.zip` và lấy tệp `Word-Wheel_Water_Meter_Dataset.zip` bên trong. Có thể tải riêng tệp này từ danh sách trên trang nếu trình duyệt tải được qua liên kết trực tiếp.
3. Giải nén vào `data/`. Kiểm tra hai thư mục `data/Word-Wheel_Water_Meter_Dataset/detection/` và `data/Word-Wheel_Water_Meter_Dataset/recognition/`. Nếu trình giải nén tạo thêm một thư mục bao ngoài, di chuyển thư mục chứa trực tiếp `detection/` và `recognition/` về đúng vị trí trên.
4. Sau khi [cài đặt môi trường](../README.md#cài-đặt), chạy `.venv\Scripts\python.exe experiments/make_splits.py` từ thư mục gốc để kiểm tra mã đọc được nhãn của bộ dữ liệu.

## Ghi chú về nhãn

Tệp `rec_label` không có dòng tiêu đề. Cột 1 là tên ảnh, cột 2 là chỉ số đồng hồ, cột 3 đến 5 lần lượt là cờ ảnh xoay ngược (reversed), chữ số cuối đang lăn giữa hai số (half-word) và đồng hồ sáu chữ số (six-digit). Với ảnh half-word, nhãn lấy số nhỏ hơn trong hai số đang hiện.

## Dữ liệu mẫu

Ảnh mẫu và nhãn gốc lấy từ tập test của [Word-Wheel Water Meter Dataset](https://doi.org/10.5061/dryad.7d7wm3860). Có thể dùng ngay sau khi clone kho.

- `sample/detection_labels.csv` chứa nhãn phân loại của 21 ảnh PNG, trích từ `detection/test/test_class_label_EXCEL.xlsx`. Ô trống trong Excel được ghi thành `0` trong CSV.
- `sample/recognition_labels.csv` chứa chỉ số và cờ `is_half_word` của 4 ảnh JPG đồng hồ năm chữ số, trích từ `5-digit_test_rec_label_CSV.csv`. Có 1 ảnh thường và 3 ảnh có chữ số cuối đang lăn. Các ảnh PNG và JPG thuộc hai tập con của bộ dữ liệu. Tra nhãn theo tên tệp đầy đủ, gồm cả phần mở rộng.

Chạy lệnh sau từ thư mục gốc để đọc ảnh nhận dạng, áp dụng cờ xoay và in nhãn giữ nguyên các chữ số 0 ở đầu.

```powershell
.venv\Scripts\python.exe -c "from pathlib import Path; from wmr.dataset import read_split, read_upright_gray; root = Path('data/sample'); [print(row.name, row.reading, row.is_half_word, read_upright_gray(root / row.name, row.is_reversed).shape) for row in read_split(root / 'recognition_labels.csv')]"
```
