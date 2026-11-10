# Đọc chỉ số đồng hồ nước bánh xe số

Bài tập lớn học phần Xử lý ảnh và thị giác máy tính (121036), Trường Đại học Giao thông vận tải Thành phố Hồ Chí Minh.

## Đề tài

- Tác vụ: đọc chỉ số trên ảnh mặt số của đồng hồ nước cơ, loại bánh xe số.
- Dữ liệu: bộ ảnh công khai Word-Wheel Water Meter Dataset (Dryad, <https://doi.org/10.5061/dryad.7d7wm3860>).
- Thách thức dự kiến: chữ số cuối đang lăn giữa hai số, nên trong ô số chỉ hiện một phần của mỗi chữ số.

Tuyên bố thách thức đầy đủ (bối cảnh, lý thuyết của giải pháp, tiêu chí kiểm chứng) nằm ở `report/` sau khi nhóm chốt.

## Hạn

Hạn nộp trên Moodle: 03:00 thứ Sáu 04/12/2026. Hạn của từng việc ghi trong issue tương ứng.

## Cấu trúc thư mục

| Thư mục | Nội dung |
|---|---|
| `src/wmr/` | Mã nguồn dùng chung: đọc dữ liệu (`dataset.py`), phương pháp đối chứng (`baseline.py`), thước đo (`metrics.py`), sau này thêm phương pháp đề xuất |
| `tests/` | Kiểm thử tự động cho `src/wmr/` |
| `docs/` | Tài liệu giải thích mã nguồn |
| `experiments/` | Script tái tạo bốn thí nghiệm bắt buộc E1 đến E4 và tệp mô tả phân tầng tập đánh giá |
| `notebooks/` | Notebook ghi nhận quá trình thực nghiệm |
| `report/` | Báo cáo và slide thuyết trình |
| `data/` | Dữ liệu tải về (không đưa lên Git), xem `data/README.md` |

## Cài đặt

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

Đã thử với Python 3.11.9. Sau đó tải dữ liệu theo `data/README.md`. Nếu dữ liệu nằm ở thư mục khác, đặt biến môi trường `WMR_DATA_ROOT` trỏ tới thư mục chứa `Word-Wheel_Water_Meter_Dataset`, hoặc truyền `--data-root` cho từng script.

## Tập phát triển và tập đánh giá

Chỉ dùng phần đồng hồ năm chữ số. Tập đánh giá là tập test gốc của bộ dữ liệu, tập phát triển là tập train gốc, chia tiếp thành hai phần theo mã băm của tên ảnh nên lần chạy nào cũng ra cùng kết quả. Danh sách ảnh nằm trong `experiments/splits/`.

| Tập | Tệp | Số ảnh | Trong đó chữ số cuối đang lăn (half-word) |
|---|---|---|---|
| Phát triển, phần dựng mẫu | `dev_fit.csv` | 9.577 | 3.399 |
| Phát triển, phần chọn tham số | `dev_val.csv` | 2.290 | 836 |
| Đánh giá | `eval.csv` | 2.000 | 355 |

Tạo lại danh sách:

```
python experiments/make_splits.py
```

## Baseline so khớp mẫu

Mẫu của mỗi chữ số là ảnh trung bình các ô số ở bốn vị trí đầu, lấy từ ảnh không gắn cờ half-word của `dev_fit`. Khi đọc, ảnh được cân bằng histogram, chia đều thành năm ô, mỗi ô so với mười mẫu bằng tương quan chéo chuẩn hóa trong phạm vi lệch 6 điểm ảnh, chọn mẫu có điểm cao nhất. Giải thích mã nguồn từng dòng: `docs/baseline-walkthrough.md`.

```
python experiments/run_baseline.py
```

Lệnh in bảng dưới đây và ghi kết quả từng ảnh vào `outputs/baseline_eval.csv`. Độ chính xác trên tập đánh giá, đo ngày 10/11/2026:

| Nhóm ảnh | Số ảnh | Số 1 | Số 2 | Số 3 | Số 4 | Số 5 | Cả chỉ số |
|---|---|---|---|---|---|---|---|
| Tất cả | 2.000 | 0,964 | 0,908 | 0,871 | 0,854 | 0,482 | 0,371 |
| Không half-word | 1.645 | 0,962 | 0,908 | 0,866 | 0,851 | 0,559 | 0,431 |
| Half-word | 355 | 0,972 | 0,907 | 0,893 | 0,865 | 0,127 | 0,096 |

Bốn chữ số đầu gần như không đổi giữa hai nhóm, còn chữ số cuối tụt từ 0,559 xuống 0,127 ở ảnh half-word. Hai nhóm này mới chia theo cờ có sẵn trong nhãn, chưa phải phân tầng theo cường độ mà đề yêu cầu.

## Kiểm thử

```
python -m pytest
```

## Cách làm việc

1. Mỗi việc là một issue, có người phụ trách và hạn.
2. Không đẩy thẳng lên `main`. Tạo nhánh từ `main`, đặt tên theo số issue, ví dụ `12-roll-metric`.
3. Mở pull request, dòng đầu của phần mô tả ghi `Closes #12.` để issue tự đóng khi gộp.
4. Một thành viên khác duyệt rồi mới gộp.
5. Đẩy nhánh lên mỗi tối, kể cả khi chưa xong.

## Quy tắc thực nghiệm theo đề

- Mọi so sánh dùng cùng dữ liệu và cùng thước đo, báo cáo theo từng tầng cường độ của thách thức, kèm số ảnh mỗi tầng.
- Tham số chọn trên tập phát triển, không tinh chỉnh trên tập đánh giá.
- Hàm hoặc mô hình dựng sẵn chỉ dùng làm tiện ích hoặc baseline, không dùng làm thành phần xử lý thách thức.
- Mọi nguồn tham khảo trích dẫn theo chuẩn IEEE.
