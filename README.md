# Đọc chỉ số đồng hồ nước bánh xe số

Bài tập lớn học phần Xử lý ảnh và thị giác máy tính (121036), Trường Đại học Giao thông vận tải Thành phố Hồ Chí Minh.

## Đề tài

- Tác vụ: đọc chỉ số năm chữ số trên ảnh vùng hiển thị của đồng hồ nước cơ loại bánh xe số.
- Dữ liệu: bộ ảnh công khai Word-Wheel Water Meter Dataset (Dryad, <https://doi.org/10.5061/dryad.7d7wm3860>).
- Thách thức: chữ số cuối đang lăn giữa hai số, nên ô cuối chỉ hiện phần dưới của số d và phần trên của số d + 1. Cường độ thách thức đo bằng vị trí khe nền trong ô cuối và chia tập đánh giá thành ba tầng nhẹ, trung bình, nặng.
- Baseline: so khớp mẫu từng ô bằng tương quan chéo chuẩn hóa (normalized cross-correlation, NCC).
- Phương pháp đề xuất: ghép mười mẫu chữ số thành một dải tuần hoàn như bánh xe thật, tìm cửa sổ trên dải khớp nhất với ô cuối để ước lượng pha lăn, rồi giải mã pha thành chữ số. Bốn chữ số đầu giữ nguyên cách đọc của baseline.

Báo cáo đầy đủ, gồm tuyên bố thách thức, lý thuyết, thực nghiệm và thảo luận, nằm ở `report/`.

## Kết quả chính

Độ chính xác trên 2.000 ảnh của tập đánh giá:

| Tầng | Số ảnh | Chữ số cuối, baseline | Chữ số cuối, đề xuất | Cả chỉ số, baseline | Cả chỉ số, đề xuất |
|---|---:|---:|---:|---:|---:|
| Nhẹ | 437 | 64,07% | 64,76% | 51,49% | 51,95% |
| Trung bình | 1.156 | 51,99% | 59,60% | 39,45% | 45,59% |
| Nặng | 407 | 20,64% | 28,75% | 15,23% | 21,62% |
| Toàn tập | 2.000 | 48,25% | 54,45% | 37,15% | 42,10% |

Bảng đủ theo từng vị trí chữ số: `experiments/phuc/results/summary.csv`. Khoảng tin cậy và kiểm định ý nghĩa thống kê nằm trong báo cáo.

## Cấu trúc thư mục

| Thư mục | Nội dung |
|---|---|
| `src/wmr/` | Mã nguồn: đọc dữ liệu (`dataset.py`), baseline (`baseline.py`), phương pháp đề xuất (`proposed.py`), thước đo độ lăn và phân tầng (`roll.py`), thước đo độ chính xác (`metrics.py`), tổng hợp kết quả (`analysis.py`) |
| `experiments/` | Script chia tập, phân tầng và bốn thí nghiệm E1 đến E4, cùng kết quả đã lưu |
| `experiments/splits/` | Danh sách ảnh của tập phát triển và tập đánh giá |
| `experiments/roll/` | Tệp mô tả phân tầng tập đánh giá (`eval_roll.csv`) và giải thích thước đo |
| `notebooks/` | Notebook trình bày kết quả E1 đến E4 |
| `tests/` | Kiểm thử tự động |
| `docs/` | Giải thích mã nguồn baseline |
| `data/` | Dữ liệu mẫu đi kèm kho; dữ liệu đầy đủ tải về theo `data/README.md` |
| `report/` | Báo cáo và slide thuyết trình |

## Cài đặt

Cần Python 3.10 trở lên. Chạy các lệnh dưới đây từ thư mục gốc của kho.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install -e .
```

Trên Linux và macOS, thay `.venv\Scripts\python.exe` bằng `.venv/bin/python`. Đã kiểm tra cài mới trên Windows với Python 3.11 và 3.13.

## Chạy thử trên dữ liệu mẫu

Không cần tải bộ dữ liệu đầy đủ. Lệnh dưới đây đọc 4 ảnh trong `data/sample/` bằng cả baseline và phương pháp đề xuất, dùng mẫu chữ số và cấu hình đã chọn trên tập phát triển (`experiments/phuc/results/templates.npy`, `selected.json`):

```powershell
.venv\Scripts\python.exe experiments/run_sample.py
```

Kết quả in ra màn hình và ghi vào `outputs/sample_predictions.csv`:

```
name       reading    roll tier    baseline  proposed
test5.jpg  00001     0.475 medium  00001     00001
test6.jpg  00001     0.169 light   07603     07603
test7.jpg  00001     0.881 heavy   00097     00097
test8.jpg  00001     0.983 heavy   00991     00991
```

Cột `roll` là thước đo độ lăn, `tier` là tầng tương ứng. Bốn ảnh mẫu thuộc tập đánh giá, và dự đoán trùng với dòng tương ứng trong `experiments/phuc/results/predictions.csv` của lần chạy đầy đủ (có kiểm thử tự động cho điều này). Ảnh `test6.jpg` bị baseline đọc sai cả bốn chữ số đầu nên phương pháp đề xuất cũng sai theo; hai ảnh lăn nặng cho thấy chữ số cuối vẫn là phần khó nhất. Bốn ảnh chỉ dùng để kiểm tra pipeline chạy được, không dùng để đánh giá.

Cách đọc nhãn mẫu và áp dụng cờ xoay: `data/README.md`.

## Tái lập E1 đến E4 trên dữ liệu đầy đủ

Tải và giải nén bộ dữ liệu theo [hướng dẫn](data/README.md#tải-về). Mặc định các script đọc dữ liệu trong `data/`. Nếu dữ liệu nằm ở thư mục khác, đặt biến môi trường `WMR_DATA_ROOT` trỏ tới thư mục chứa `Word-Wheel_Water_Meter_Dataset`, hoặc truyền `--data-root` cho từng script.

Chạy lần lượt từ thư mục gốc:

| Bước | Lệnh | Kết quả |
|---|---|---|
| Chia tập | `.venv\Scripts\python.exe experiments/make_splits.py` | `experiments/splits/*.csv` |
| Phân tầng tập đánh giá | `.venv\Scripts\python.exe experiments/make_roll_tiers.py` | `experiments/roll/eval_roll.csv`, `report/figures/roll-tiers.png` |
| E2, chọn tham số trên `dev_val` | `.venv\Scripts\python.exe experiments/run_phuc.py --stage tune` | `experiments/phuc/results/e2_grid.csv`, `selected.json`, `templates.npy` |
| E1, so sánh trên tập đánh giá theo tầng | `.venv\Scripts\python.exe experiments/run_phuc.py --stage evaluate` | `experiments/phuc/results/predictions.csv`, `summary.csv`, `e1_*.csv` |
| E3 loại bỏ thành phần, E4 điểm gãy | `.venv\Scripts\python.exe experiments/run_e3_e4.py` | `experiments/quang/results/` |

E2 chạy trước E1 vì cấu hình dùng cho tập đánh giá phải được chốt trên tập phát triển. Bước E1 kiểm tra mã băm của các tệp chia tập so với lúc chọn tham số và dừng nếu có thay đổi. Các lệnh ghi đè kết quả đã lưu trong kho; lần chạy lại ngày 22/11/2026 trên bản sao sạch cho các tệp CSV trùng với bản trong kho.

Giải thích chi tiết từng phần: `experiments/roll/README.md` (thước đo độ lăn), `experiments/phuc/README.md` (E1, E2), `experiments/quang/README.md` (E3, E4), `docs/baseline-walkthrough.md` (baseline). Chỉ chạy baseline trên một tập: `.venv\Scripts\python.exe experiments/run_baseline.py`.

## Tập phát triển và tập đánh giá

Chỉ dùng phần đồng hồ năm chữ số. Tập đánh giá là tập test gốc của bộ dữ liệu. Tập phát triển là tập train gốc, chia tiếp thành hai phần theo mã băm của tên ảnh nên lần chạy nào cũng ra cùng kết quả.

| Tập | Tệp | Số ảnh | Trong đó có cờ half-word |
|---|---|---:|---:|
| Phát triển, phần dựng mẫu | `dev_fit.csv` | 9.577 | 3.399 |
| Phát triển, phần chọn tham số | `dev_val.csv` | 2.290 | 836 |
| Đánh giá | `eval.csv` | 2.000 | 355 |

Cờ half-word có sẵn trong nhãn của bộ dữ liệu và chỉ dùng để đối chiếu. Phân tầng dùng thước đo độ lăn tính từ ảnh.

## Kiểm thử

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m pytest
```

## Quy tắc thực nghiệm theo đề

- Mọi so sánh dùng cùng dữ liệu và cùng thước đo, báo cáo theo từng tầng cường độ của thách thức, kèm số ảnh mỗi tầng.
- Tham số chọn trên tập phát triển, không tinh chỉnh trên tập đánh giá.
- Hàm hoặc mô hình dựng sẵn chỉ dùng làm tiện ích hoặc baseline, không dùng làm thành phần xử lý thách thức.
- Mọi nguồn tham khảo trích dẫn theo chuẩn IEEE.

## Kiểm tra bản bàn giao

Sau khi giải nén gói nộp, chạy từ thư mục gốc bằng Python đã cài các thư viện:

```sh
python experiments/check_submission.py
python experiments/run_sample.py
python -m pytest
```

Lệnh đầu kiểm tra tệp cần thiết, ghép cặp dự đoán, 27 cấu hình E2, 54 ô quét lệch bước E4, hình báo cáo và cấu trúc bộ 14 slide. Mã băm các tệp được ghi vào `outputs/submission_check.json`. Notebook được kiểm tra riêng bằng Restart & Run All. Kiểm tra nguồn không thay thế việc xem bản PDF/slide, điền thông tin bìa hoặc xác nhận nộp Moodle.
