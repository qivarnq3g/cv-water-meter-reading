# E3 và E4

Phần này dùng nguyên cấu hình đã chốt trên `dev_val` trong `experiments/phuc/results/selected.json` (bước 58, trượt ngang 6, ngưỡng 0,4) và mẫu chữ số `templates.npy`. Không chọn lại tham số nào.

## Chạy

Từ thư mục gốc của kho, sau khi cài như README chính:

```sh
python experiments/run_e3_e4.py --data-root /path/to/data
```

Kết quả ghi vào `experiments/quang/results/`, mất khoảng một phút.

## E3: loại bỏ thành phần

`WheelConfig` có thêm tham số `continuous`. Khi đặt `False`, dải bánh xe chỉ giữ các pha cách tâm chữ số không quá `max_shift` hàng, tức là bỏ đúng phần pha nằm giữa hai chữ số. Ba phiên bản chạy trên 2.000 ảnh của tập đánh giá:

| Độ chính xác chữ số cuối | Toàn tập | Nhẹ | Trung bình | Nặng |
|---|---:|---:|---:|---:|
| Baseline (`enabled=False`) | 48,25% | 64,07% | 51,99% | 20,64% |
| Bỏ pha giữa hai chữ số (`continuous=False`) | 48,95% | 65,90% | 52,25% | 21,38% |
| Phương pháp đề xuất | 54,45% | 64,76% | 59,60% | 28,75% |

Bỏ pha giữa hai chữ số thì kết quả gần như trở về baseline ở cả ba tầng. Phần tăng ở tầng trung bình và tầng nặng đến từ các pha giữa hai chữ số, đúng thành phần nhắm vào độ lăn. Bốn chữ số đầu không đổi ở cả ba phiên bản (89,91%). Bảng đủ: `e3_summary.csv`.

## E4: kiểm tra điểm gãy

Ảnh lăn tổng hợp: lấy ô chữ số cuối của một ảnh ít lăn trong `dev_val` (độ lăn đo được dưới 0,21, khoảng 20% ảnh ít lăn nhất) làm chữ số d, ghép phía dưới ô của một ảnh khác có chữ số d + 1 (chuẩn hóa về cùng độ sáng trung bình và độ lệch chuẩn), rồi cắt cửa sổ lệch φ chiều cao ô. Quét φ từ 0 tới 0,5, bước 0,05, trên 165 cặp. Các phần khác của ảnh giữ nguyên.

| φ | Thước đo độ lăn | Baseline ±2 | Baseline ±6 | Baseline ±10 | Đề xuất |
|---:|---:|---:|---:|---:|---:|
| 0,00 | 0,18 | 52,7% | 66,1% | 70,9% | 66,7% |
| 0,10 | 0,34 | 46,7% | 63,6% | 67,3% | 67,3% |
| 0,20 | 0,40 | 30,9% | 47,3% | 61,8% | 67,3% |
| 0,30 | 0,59 | 28,5% | 32,1% | 36,4% | 64,8% |
| 0,40 | 0,77 | 24,2% | 22,4% | 27,9% | 58,8% |
| 0,50 | 0,85 | 25,5% | 20,0% | 19,4% | 56,4% |

Số trong bảng là tỉ lệ đọc ra d hoặc d + 1. Bảng đủ và hình: `e4_curve.csv`, `e4_curve.png`.

Đối chiếu với dự đoán trong `report/challenge-statement.md`:

- Dự đoán 1 (baseline gãy theo s/p): điểm gãy, lấy là φ đầu tiên có tỉ lệ dưới 50%, dời theo bán kính trượt: 0,10 với ±2, 0,20 với ±6, 0,30 với ±10. Chiều dời đúng dự đoán. Vị trí muộn hơn s/p (0,03; 0,10; 0,17) khoảng 0,07 tới 0,13, gần với (s + w)/p khi w khoảng 5 điểm ảnh. Quan hệ này rút ra sau khi xem số liệu, chưa kiểm chứng độc lập.
- Dự đoán 2 (đề xuất không gãy theo φ ở tầng nhẹ và trung bình): đúng trên ảnh tổng hợp. Tỉ lệ của phương pháp đề xuất ở trong khoảng 56% tới 70% suốt dải φ và không xuống dưới 50%. Tuy vậy, việc định vị pha bắt đầu kém đi từ φ khoảng 0,35: trung vị sai số pha giữ quanh 0,08 chữ số tới φ = 0,3, rồi tăng lên 0,22 ở φ = 0,35 và 0,70 ở φ = 0,5. Ở vùng này phương pháp đề xuất vẫn đọc ra d hoặc d + 1, nhưng không còn biết chính xác cửa sổ đang ở đâu giữa hai chữ số, nên ngưỡng t quyết định nhiều hơn pha đo được.
- Dự đoán 3 (lỗi dồn quanh ngưỡng, phần lớn lệch một chữ số): không được ủng hộ. Ở φ = 0, trung vị sai số pha chỉ 0,09 chữ số, nhưng khoảng 36% cặp sai trọn một hay nhiều chữ số. Lỗi chính là nhầm mẫu chữ số, giống baseline ở ảnh đứng yên, không phải lỗi định vị pha. Trên tập đánh giá, lỗi lệch một chữ số chỉ chiếm 25,2% lỗi chữ số cuối ở tầng nặng.
- Dự đoán 4 (gãy khi chiều cao chữ số lệch quá 9% trung vị): chưa kết luận được. Trung vị chiều cao đo trên bốn chữ số đầu là 56,5 điểm ảnh. Ở tầng nặng chỉ 18 ảnh lệch quá 9%, độ chính xác 38,9% so với 28,3% ở 389 ảnh còn lại, ngược chiều dự đoán nhưng mẫu quá nhỏ. Bảng: `e4_height_split.csv`. Phép quét lệch bước trên ảnh tổng hợp (`--stages pitch`, khoảng 1 phút) cho kết quả rõ hơn: khi bước thật dài hơn 58 điểm ảnh từ 10% trở lên, trung vị sai số pha vượt 0,25 chữ số từ pha 0,3; khi ngắn hơn từ 15% trở lên, P mất định vị cả ở pha nhỏ. Tỉ lệ đọc ra d hoặc d + 1 chỉ xuống quanh 50% ở độ lệch 15% đến 20%. Bảng: `e4_pitch_curve.csv`, `e4_pitch_report.json`.

Thước đo độ lăn của PR #21 tăng đều theo φ trên ảnh tổng hợp (0,18 lên 0,85), một kiểm chứng độc lập cho thước đo này.

## Giới hạn

- Ảnh "đứng yên" vẫn có độ lăn đo được khoảng 0,18, và hai ô ghép đến từ hai đồng hồ khác nhau. Ảnh tổng hợp không thay được ảnh lăn thật; kết quả E4 chỉ cho biết cơ chế, không cho số liệu tuyệt đối.
- Chu kỳ ghép bằng chiều cao ô (60 hàng), không phải bước thật của bánh xe.
- Kho chữ số đứng yên ít (7 ảnh cho chữ số 7), nên 165 cặp lặp lại cùng một số ô.
- Chiều quay: trên 836 ảnh half-word của `dev_val`, dải xếp xuôi (0, 1, ..., 9) và dải xếp ngược khớp gần bằng nhau (NCC trung bình 0,420 so với 0,421). Dữ liệu chưa xác định được chiều quay. Đây là điểm cần làm rõ trước khi khẳng định phương pháp mô hình hóa đúng chuyển động của bánh xe.
