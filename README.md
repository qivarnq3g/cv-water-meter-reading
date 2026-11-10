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
| `src/` | Mã nguồn dùng chung: đọc dữ liệu, phương pháp đối chứng (baseline), phương pháp đề xuất, thước đo |
| `experiments/` | Script tái tạo bốn thí nghiệm bắt buộc E1 đến E4 và tệp mô tả phân tầng tập đánh giá |
| `notebooks/` | Notebook ghi nhận quá trình thực nghiệm |
| `report/` | Báo cáo và slide thuyết trình |
| `data/` | Dữ liệu tải về (không đưa lên Git), xem `data/README.md` |

## Cài đặt

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Sau đó tải dữ liệu theo `data/README.md`.

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
