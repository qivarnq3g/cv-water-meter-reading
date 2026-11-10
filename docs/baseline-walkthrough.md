# Giải thích mã nguồn: đọc dữ liệu và baseline

Tài liệu này đi qua `src/wmr/dataset.py`, `src/wmr/baseline.py` và `src/wmr/metrics.py` theo thứ tự chương trình chạy. Mục tiêu là đọc xong thì tự giải thích được từng bước khi bị hỏi.

## Ý tưởng bằng ví dụ đời thường

Hình dung cậu có mười con dấu, mỗi con khắc một chữ số từ 0 đến 9. Muốn biết ô số trên đồng hồ đang hiện số mấy, cậu áp lần lượt từng con dấu lên ô đó, xê dịch qua lại một chút, và xem con nào khít nhất. Con dấu khít nhất chính là chữ số đọc được. Cách này gọi là so khớp mẫu (template matching).

Mười "con dấu" không có sẵn, nên phải tự làm: lấy thật nhiều ô đã biết là số 3, cộng lại rồi chia trung bình, ra một ảnh số 3 "điển hình". Làm tương tự cho chín số còn lại.

Cách này hỏng khi ô cuối đang lăn: ô lúc đó hiện nửa dưới của số 1 và nửa trên của số 2, không khít với con dấu nào. Đó là thách thức của đề tài.

## Tệp `dataset.py`: đọc nhãn và ảnh

### `MeterSample`

```python
@dataclass(frozen=True)
class MeterSample:
    name: str
    source_split: str
    reading: str
    is_reversed: bool
    is_half_word: bool
```

- `@dataclass(frozen=True)`: tạo một kiểu dữ liệu chỉ để chứa thông tin, tạo xong không sửa được. Mỗi ảnh là một `MeterSample`.
- `name`: tên tệp ảnh, ví dụ `test12.jpg`.
- `source_split`: ảnh nằm ở thư mục `train` hay `test` của bộ dữ liệu gốc, cần để tìm đường dẫn.
- `reading`: chỉ số đúng, giữ ở dạng chuỗi. Nếu đổi sang số nguyên thì `00412` thành `412`, mất ba số 0 đầu.
- `is_reversed`: ảnh bị chụp ngược 180 độ.
- `is_half_word`: chữ số cuối đang lăn giữa hai số.

### `parse_label_row`

```python
if len(row) != 5:
    raise ValueError(...)
name, reading, reversed_flag, half_word_flag, _six_digit_flag = row
if not reading.isdigit():
    raise ValueError(...)
return MeterSample(..., is_reversed=reversed_flag == "1", is_half_word=half_word_flag == "1")
```

- Dòng 1 và 2: mỗi dòng nhãn phải có đúng năm cột, sai thì dừng ngay và báo lỗi, không đoán.
- Dòng 3: tách năm cột ra năm biến. Cột thứ năm (đồng hồ sáu chữ số) không dùng nên tên bắt đầu bằng dấu gạch dưới.
- Dòng 4 và 5: chỉ số phải toàn chữ số.
- Dòng cuối: tệp nhãn ghi cờ bằng `"0"` hoặc `"1"`. Phép so sánh `== "1"` đổi nó thành đúng hoặc sai.

### `load_labels`

```python
with open(path, encoding="utf-8-sig", newline="") as handle:
    return [parse_label_row(row, source_split) for row in csv.reader(handle) if row]
```

- `utf-8-sig`: bỏ ký tự đánh dấu vô hình mà Excel hay chèn ở đầu tệp CSV.
- `csv.reader(handle)`: đọc từng dòng, tách theo dấu phẩy.
- `if row`: bỏ dòng trống.

### `assign_dev_subset`

```python
digest = hashlib.sha1(name.encode("utf-8")).hexdigest()
bucket = int(digest, 16) % 100
return "val" if bucket < val_percent else "fit"
```

- Dòng 1: biến tên ảnh thành một dãy ký tự trông ngẫu nhiên nhưng cố định, cùng tên thì luôn ra cùng dãy (hàm băm).
- Dòng 2: đổi dãy đó thành số rồi lấy phần dư khi chia 100, được một số từ 0 đến 99.
- Dòng 3: số nhỏ hơn 20 thì ảnh vào phần `val`, còn lại vào `fit`. Kết quả là khoảng 20 phần trăm ảnh vào `val`.
- Vì sao không dùng `random`: chia ngẫu nhiên thì mỗi máy, mỗi lần chạy có thể ra kết quả khác nhau. Chia theo tên thì bốn người chạy đều ra một danh sách.

### `read_upright_gray`

```python
data = np.fromfile(str(path), dtype=np.uint8)
image = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
if is_reversed:
    image = cv2.rotate(image, cv2.ROTATE_180)
```

- Dòng 1 và 2: đọc tệp thành dãy byte rồi giải mã thành ảnh xám. Không dùng `cv2.imread` vì ở nhiều phiên bản OpenCV trên Windows, hàm đó trả về rỗng khi đường dẫn có dấu tiếng Việt.
- Dòng 3 và 4: ảnh ngược thì xoay 180 độ cho xuôi lại. Cờ ngược lấy từ nhãn, đây là một giả định thu hẹp: baseline không tự phát hiện ảnh ngược.

## Tệp `baseline.py`: so khớp mẫu

### `BaselineConfig`

```python
digit_count: int = 5
max_shift: int = 6
template_positions: tuple[int, ...] = (0, 1, 2, 3)
```

- `digit_count`: đồng hồ có năm ô số.
- `max_shift`: khi áp mẫu được xê dịch tối đa 6 điểm ảnh mỗi hướng.
- `template_positions`: chỉ lấy bốn ô đầu để dựng mẫu. Ô cuối hay lăn dở, kể cả ở ảnh không gắn cờ half-word, nên lấy vào sẽ làm bẩn mẫu.

### `preprocess`

```python
return cv2.equalizeHist(gray)
```

Cân bằng histogram: kéo giãn mức sáng để ảnh tối và ảnh sáng có độ tương phản gần nhau. Đây là toán tử điểm học ở chương 2.

### `cell_bounds` và `extract_cell`

```python
cell_width = width // digit_count
start = position * cell_width
return start, start + cell_width
```

- Ảnh rộng 200 điểm ảnh, chia 5, mỗi ô rộng 40.
- Ô số `position` bắt đầu ở cột `position * 40`. Ô 0 là cột 0 đến 40, ô 4 là cột 160 đến 200.
- `extract_cell` dùng hai mốc này để cắt ô ra: `image[:, start:end]` nghĩa là lấy mọi hàng, chỉ lấy các cột từ `start` đến trước `end`.

### `build_templates`: làm mười con dấu

```python
sums = None
counts = np.zeros(10, dtype=np.int64)
for image, reading in zip(images, readings):
    prepared = preprocess(image).astype(np.float32)
    for position in config.template_positions:
        cell = extract_cell(prepared, config.digit_count, position)
        if sums is None:
            sums = np.zeros((10, *cell.shape), dtype=np.float64)
        digit = int(reading[position])
        sums[digit] += cell
        counts[digit] += 1
if sums is None or np.any(counts == 0):
    raise ValueError(...)
return (sums / counts[:, None, None]).astype(np.float32)
```

- `counts`: mười ô đếm, ô thứ `d` đếm đã gặp bao nhiêu ô ảnh là số `d`.
- `for image, reading in zip(...)`: đi qua từng ảnh cùng chỉ số đúng của nó.
- `prepared = ...`: cân bằng histogram, đổi sang số thực để cộng không bị tràn.
- `for position in ...`: đi qua bốn ô đầu.
- `cell = ...`: cắt ô đó ra.
- `if sums is None`: lần đầu tiên mới biết kích thước ô, lúc đó tạo mười ảnh toàn số 0 để cộng dồn.
- `digit = int(reading[position])`: ô này là số mấy, tra trong chỉ số đúng.
- `sums[digit] += cell`: cộng ô vào tổng của chữ số đó.
- `counts[digit] += 1`: tăng ô đếm.
- `if ... np.any(counts == 0)`: nếu có chữ số chưa từng gặp thì không có mẫu cho nó, báo lỗi thay vì chạy tiếp với mẫu rỗng.
- Dòng cuối: tổng chia cho số lượng ra ảnh trung bình. `counts[:, None, None]` đổi mười con số thành dạng chia được cho mười ảnh.

### `match_scores`: áp mười con dấu lên một ô

```python
shift = config.max_shift
padded = cv2.copyMakeBorder(prepared, shift, shift, shift, shift, cv2.BORDER_REPLICATE)
start, end = cell_bounds(prepared.shape[1], config.digit_count, position)
region = padded[:, start : end + 2 * shift].astype(np.float32)
scores = np.empty(len(templates), dtype=np.float32)
for digit, template in enumerate(templates):
    response = cv2.matchTemplate(region, template, cv2.TM_CCOEFF_NORMED)
    scores[digit] = response.max()
return scores
```

- `padded`: nới ảnh thêm 6 điểm ảnh ở cả bốn phía bằng cách lặp lại điểm ảnh ở mép. Nhờ vậy ô ở sát mép vẫn có chỗ để xê dịch mẫu.
- `region`: vùng tìm kiếm của ô này. Vì ảnh đã nới 6 điểm ảnh bên trái, cột `start` của ảnh nới chính là cột `start - 6` của ảnh gốc. Vùng rộng 40 + 12 = 52, cao 60 + 12 = 72, tức là ô gốc cộng thêm 6 điểm ảnh mỗi phía.
- `scores`: mười ô để ghi điểm của mười chữ số.
- `cv2.matchTemplate(...)`: trượt mẫu 40 x 60 trên vùng 52 x 72, tại mỗi vị trí tính một điểm giống nhau. Có 13 x 13 = 169 vị trí.
- `TM_CCOEFF_NORMED`: tương quan chéo chuẩn hóa. Trước khi so, cả mẫu và vùng ảnh đều bị trừ đi độ sáng trung bình và chia cho độ lệch chuẩn, nên điểm nằm từ -1 đến 1 và không đổi khi ảnh sáng lên hay tối đi đều. Điểm 1 là khít hoàn toàn.
- `response.max()`: lấy điểm cao nhất trong 169 vị trí, tức là vị trí áp khít nhất.

### `read_meter`: đọc cả đồng hồ

```python
prepared = preprocess(image)
digits = []
for position in range(config.digit_count):
    scores = match_scores(prepared, templates, position, config)
    digits.append(str(int(np.argmax(scores))))
return "".join(digits)
```

- Cân bằng histogram một lần cho cả ảnh.
- Với từng ô trong năm ô: lấy mười điểm, `np.argmax` trả về vị trí của điểm cao nhất, đó chính là chữ số.
- Ghép năm chữ số thành chuỗi, ví dụ `"00412"`.

## Tệp `metrics.py`: chấm điểm

- `position_accuracy`: với mỗi vị trí từ 1 đến 5, đếm bao nhiêu ảnh đọc đúng chữ số ở vị trí đó rồi chia cho tổng số ảnh. Trả về năm con số.
- `reading_accuracy`: tỉ lệ ảnh đọc đúng cả năm chữ số. Sai một chữ số là tính sai cả ảnh.

## Câu hỏi có thể gặp

- Vì sao baseline đọc sai chữ số cuối? Khi ô đang lăn, ô hiện hai nửa của hai chữ số. Mẫu là một chữ số nguyên vẹn nằm giữa ô, nên không mẫu nào khít. Trên 355 ảnh half-word của tập đánh giá, baseline đúng 45, ra số kế tiếp 31, và ra một số không liên quan 279.
- Vì sao xê dịch 6 điểm ảnh không cứu được? Xê dịch chỉ bù được lệch nhỏ của cả chữ số. Khi lăn nửa vòng, chữ số lệch khoảng nửa chiều cao ô, tức khoảng 30 điểm ảnh, và phần còn lại bị khuất.
- Vì sao bốn số đầu chỉ đạt 0,85 đến 0,96 chứ không gần 1? Chia đều năm ô là giả định thô, vị trí ô thật lệch tùy ảnh, và mẫu trung bình bị nhòe. Đây là điểm yếu chung của baseline, không liên quan tới độ lăn.
- Baseline có dùng nhãn khi đọc không? Có một chỗ: cờ ảnh ngược lấy từ nhãn để xoay ảnh. Chỉ số thì không dùng.
