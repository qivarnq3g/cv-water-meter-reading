# Thước đo độ lăn của chữ số cuối và ba tầng của tập đánh giá

Mã: `src/wmr/roll.py`. Chạy lại: `python experiments/make_roll_tiers.py` (cần `WMR_DATA_ROOT` và `PYTHONPATH=src`). Kết quả từng ảnh nằm trong `eval_roll.csv` (cột `name`, `roll`, `tier`), hình minh họa trong `report/figures/roll-tiers.png`.

## Thước đo

Khi bánh xe số quay, khe nền sáng giữa hai chữ số liên tiếp trượt qua ô cửa sổ. Chữ số đứng yên thì khe nằm sát mép trên hoặc mép dưới của ô. Chữ số lăn đúng nửa thì khe nằm giữa ô. Thước đo vì vậy là vị trí của khe:

1. Cân bằng histogram ảnh xám, rồi nhị phân hóa bằng ngưỡng thích nghi trung bình (khối 15 px, trừ 8) để tách nét mực khỏi nền. Cách này giữ được nét mảnh của số 1, số 7 khi ảnh sáng không đều.
2. Lấy ô chữ số cuối (một phần năm chiều rộng ảnh, bỏ 10% mỗi bên để tránh vạch khung), tính tỉ lệ điểm mực trên từng hàng, làm trơn bằng Gauss σ = 1.5.
3. Khe là hàng có ít mực nhất, tìm trong các hàng cách mép trên và mép dưới ít nhất 5 px.
4. Độ lăn = khoảng cách từ khe tới mép gần nhất, chia cho nửa chiều cao ảnh. Giá trị nằm trong [0, 1]: gần 0 là chữ số đứng yên, gần 1 là lăn đúng nửa. Do bỏ 5 px ở mỗi mép, giá trị nhỏ nhất thực tế là 0.17.

Thước đo không dùng nhãn: nó chỉ đọc ảnh, nên dùng được cho ảnh mới.

Cách tính này được chọn trên tập `dev_val` (2.290 ảnh), so khả năng tách ảnh có cờ `half-word` (AUC) và độ lệch giá trị trung bình giữa các chữ số khi không lăn. Phiên bản trung bình độ tối theo hàng cho AUC 0.83 và độ lệch giữa các chữ số 0.16. Phiên bản nhị phân hóa thích nghi cho AUC 0.86 và độ lệch 0.08. Tập đánh giá không được dùng để chọn.

## Tiêu chí chia tầng

Ngưỡng cố định, đặt theo ý nghĩa vật lý chứ không dò trên dữ liệu:

| Tầng | Độ lăn | Ý nghĩa |
|---|---|---|
| Nhẹ (`light`) | dưới 1/3 | khe nằm trong một phần ba trên hoặc dưới của nửa ô, chữ số gần như đứng yên |
| Trung bình (`medium`) | từ 1/3 tới dưới 2/3 | chữ số lăn rõ, phần lớn chữ số hiện tại vẫn còn |
| Nặng (`heavy`) | từ 2/3 trở lên | khe gần giữa ô, hai chữ số chia đôi ô cửa sổ |

## Số ảnh mỗi tầng trên tập đánh giá (2.000 ảnh)

| Tầng | Số ảnh | Ảnh có cờ `half-word` | Baseline đọc đúng chữ số cuối |
|---|---:|---:|---:|
| Nhẹ | 437 | 27 (6.2%) | 64.1% |
| Trung bình | 1.156 | 89 (7.7%) | 52.0% |
| Nặng | 407 | 239 (58.7%) | 20.6% |

Cột cuối lấy từ `outputs/baseline_eval.csv` (baseline so khớp mẫu của issue #1). Độ chính xác giảm dần qua ba tầng, nên các tầng phản ánh đúng độ khó mà thước đo nhắm tới.

## Hạn chế

- Cờ `half-word` là nhãn nhị phân, còn độ lăn là liên tục. Nhiều ảnh không có cờ vẫn lăn một phần, nên AUC 0.86 là cận dưới của độ chính xác thật của thước đo.
- Hình dạng chữ số vẫn ảnh hưởng một ít: hàng giữa của số 0 hoặc số 7 ít mực hơn nên có thể bị nhận là khe. Với ảnh không lăn, độ lăn trung bình giữa các chữ số lệch nhau tối đa 0.08.
- Tầng trung bình lớn nhất (58% tập đánh giá) và chứa cả ảnh lăn ít lẫn ảnh lăn vừa. Hình minh họa có một ảnh ở tầng nặng mà chữ số cuối đứng yên ("02549", độ lăn 0.81).
