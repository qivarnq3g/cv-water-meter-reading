# Dữ liệu

Kho này không chứa bộ dữ liệu đầy đủ (tệp nén khoảng 2,6 GB). Thư mục `data/` bị bỏ qua trong Git, trừ tệp này và `data/sample/`.

## Tải về

1. Mở trang Dryad của bộ Word-Wheel Water Meter Dataset: <https://doi.org/10.5061/dryad.7d7wm3860>.
2. Tải `Word-Wheel_Water_Meter_Dataset.zip` bằng trình duyệt.
3. Giải nén vào `data/`, để có `data/Word-Wheel_Water_Meter_Dataset/detection/` và `data/Word-Wheel_Water_Meter_Dataset/recognition/`.

## Ghi chú về nhãn

Tệp `rec_label` không có dòng tiêu đề. Cột 1 là tên ảnh, cột 2 là chỉ số đồng hồ, cột 3 đến 5 lần lượt là cờ ảnh xoay ngược (reversed), chữ số cuối đang lăn giữa hai số (half-word) và đồng hồ sáu chữ số (six-digit). Với ảnh half-word, nhãn lấy số nhỏ hơn trong hai số đang hiện.

## Dữ liệu mẫu

`data/sample/` chứa một ít ảnh kèm nhãn để chạy thử mã nguồn mà không cần tải cả bộ.
