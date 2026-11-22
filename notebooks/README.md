# Notebook thực nghiệm E1 tới E4

Mở `phuc_experiments.ipynb` bằng Jupyter từ thư mục gốc repo hoặc `notebooks/`, chọn Restart & Run All. Cài `requirements.txt` và `requirements-dev.txt` trước khi chạy. Không cần bộ ảnh đầy đủ: notebook đọc trực tiếp bảng và hình đã commit trong `experiments/phuc/results/` và `experiments/quang/results/`.

E1: chứng cứ theo tầng, đối chứng bốn số đầu và proxy ánh sáng/độ nét. E2: đủ 27 cấu hình, ba đồ thị giữ cố định các tham số còn lại, ảnh trung gian. E3: baseline, bỏ pha trung gian và phương pháp đầy đủ. E4: đủ 11 mức pha, đường cong với ba bán kính baseline, sai số pha, độ lăn, nhóm chiều cao và đối chiếu bốn dự đoán.

Notebook kiểm tra cấu hình E1/E2 trùng E3/E4, số ảnh các tầng cộng thành 2.000, bảng E1 trùng E3 ở baseline/proposed, bốn số đầu không đổi, điểm gãy tính từ CSV trùng JSON. Thiếu bảng sẽ báo lỗi. Cuối notebook in SHA-256 CSV đầu vào để truy nguồn.

Không chạy lại lựa chọn tham số hoặc ảnh eval trong notebook. E4 đo tỉ lệ đọc ra d hoặc d+1 trên ảnh tổng hợp, không phải accuracy nhãn thật. Không coi 165 cặp ghép là 165 đồng hồ độc lập hoặc khẳng định quan hệ nhân quả từ E1.

Đã kiểm tra chạy từ đầu đến cuối với kernel Python 3 trên macOS. Kiểm tra này xác minh notebook đọc và trình bày nhất quán kết quả đã lưu; không phải một lần chạy lại toàn bộ thực nghiệm ảnh.
