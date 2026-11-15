# Phần thực hiện của Phúc

Nhánh `phuc-experiments` kế thừa PR #21 (#3). Mã phương pháp bám đề xuất trong PR #22, chưa coi là phương pháp đã được cả nhóm duyệt.

## Chạy

Từ thư mục gốc repo, Python >=3.10:

```sh
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
python -m pip install -e .
python -m pytest
python experiments/run_phuc.py --stage tune --data-root /path/to/data
python experiments/run_phuc.py --stage evaluate --data-root /path/to/data
```

`data-root` chứa `Word-Wheel_Water_Meter_Dataset`. Tune chỉ dùng dev_fit và dev_val. Grid gồm pitch 54/58/62, dịch ngang 2/6/10, ngưỡng nhãn 0.4/0.5/0.6 (27 cấu hình). Chọn accuracy chữ số cuối lớn nhất, hòa chọn cấu hình xuất hiện trước. `selected.json` ghi cấu hình và SHA-256 danh sách chia tập; đánh giá kiểm tra các fingerprint trước khi chạy. Không chọn lại tham số từ eval.

## Sản phẩm

- #3: mã đo độ lăn, bảng tầng và hình được kế thừa từ PR #21; số liệu đó do PR gốc cung cấp, chưa được chạy lại ở đây.
- #6 E1: `predictions.csv`, `summary.csv` (accuracy từng số/cả chuỗi, theo tầng), `e1_controls.csv` (độ sáng, tương phản, Laplacian variance, chữ số đúng, half-word).
- #8: `src/wmr/proposed.py`; dải tuần hoàn 0–9, tìm pha bằng NCC; `enabled=False` trả đúng baseline cùng max_shift. Khi báo cáo E3 phải dùng cùng max_shift với cấu hình đã chọn.
- #11 E2: grid theo tầng trên dev_val, cấu hình đã chọn, ảnh raw/equalized/ô cuối/mẫu khớp. Cần đọc kết quả và bổ sung nhận xét sau khi chạy dữ liệu thật.
- #16: notebook đọc E1/E2 và kết quả E3/E4 của Quang khi có; không tự tạo số liệu thay Quang.

## Giới hạn cần công bố

Thước đo khe nền có thể nhầm khoảng trống bên trong chữ số. Mối liên hệ accuracy–tầng không đủ chứng minh nhân quả. E1 xuất proxy độ sáng/độ nét và độ chính xác bốn số đầu; không có ID đồng hồ nên không khẳng định đã kiểm soát cùng loại đồng hồ. Cần kiểm tra bảng controls và ảnh thật trước khi kết luận. Quy ước chữ số khi chuyển 9→0 và chiều quay phải xác minh từ ảnh dev_val. P dùng một chiều quay cố định và một pitch chung; đây là giả thuyết cần kiểm chứng, không phải kết quả đã xác nhận.

Chưa có bộ ảnh tại máy thực hiện; Dryad trả HTTP 401/403 khi tải ngày 15/11/2026. Vì thế chưa có bảng thực nghiệm mới và chưa thể đóng các issue #6/#11/#16.
