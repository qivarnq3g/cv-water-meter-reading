# Rà nội dung để bàn giao phần Phúc

Phần số liệu E1/E2, notebook và kết quả E3/E4 đã có đủ nguồn để tập thuyết trình. Trước khi đóng gói, nhóm cần duyệt notebook, chốt người nói và ghi rõ tiêu chí E4 trên slide. Bản rà này đối chiếu nội dung và dữ liệu trong tệp PowerPoint, chưa kiểm tra hiển thị thực tế bằng PowerPoint.

## Tình trạng tài liệu

| Thành phần | Tình trạng kiểm tra |
|---|---|
| PR #31, notebook E1 tới E4 | Đã gửi yêu cầu review tới Quang, tài khoản qivarnq3g. Chờ duyệt và gộp để đóng #16. |
| PR #30, bộ slide 10 trang | Đã đối chiếu chữ, ghi chú và dữ liệu biểu đồ với bảng gốc. |
| Báo cáo trên main | Các mục nguồn dữ liệu, công trình liên quan, thiết lập và kết quả có riêng trong report/. Issue #15 về ghép báo cáo hoàn chỉnh còn mở. Chưa có căn cứ xác nhận bản hoàn chỉnh đủ 12 mục và 6 tới 15 trang. |
| Tập thuyết trình #17 | Đã chuẩn bị lời nói và bộ hỏi đáp. Chưa ghi nhận buổi tập trực tiếp hoặc xác nhận mỗi thành viên đã trình bày đủ. |

## Đối chiếu số liệu slide

Biểu đồ E1 ở slide 5 khớp summary.csv tới hai chữ số thập phân: baseline số cuối nhẹ/trung bình/nặng 64,07% / 51,99% / 20,64%, đề xuất 64,76% / 59,60% / 28,75%. Mức tăng tầng nặng là 8,11 điểm phần trăm.

Bảng slide 6 trình bày đúng 27 cấu hình E2. Cao nhất trong lưới là pitch 58, dịch ngang 6 và ngưỡng 0,4, đạt 45,41% trên dev_val. Biểu đồ E3 ở slide 7 khớp e3_summary.csv, gồm bản bỏ pha trung gian 65,90% / 52,25% / 21,38%. Phần ghi chú E4 có nêu 165 cặp, bước pha 0,05 và tiêu chí d hoặc d+1.

## Các điểm cần chốt trước buổi tập

1. Tên người trình bày chưa xuất hiện trong chữ hoặc ghi chú của bộ slide PR #30 đã kiểm tra. Tiêu chí issue #14 yêu cầu ghi tên cho từng phần. Đề xuất Phúc nói slide 3, 5, 6; nhóm xác nhận các slide còn lại và thời lượng trước khi ghi vào slide.
2. Ở slide 8, tiêu chí “tỉ lệ đọc ra d hoặc (d+1) mod 10” mới được giải thích trong ghi chú và hình gốc. Nên thêm dòng chú thích dễ thấy để người xem phân biệt với accuracy nhãn thật E1/E3.
3. Slide 9 nói “dải tuần hoàn luôn trên 50% trên ảnh tổng hợp”. Khi trình bày, giới hạn phát biểu thành “chưa xuống dưới 50% theo tiêu chí d hoặc d+1 trong miền pha 0 tới 0,5 đã khảo sát”. Sai số pha vẫn tăng mạnh và accuracy trên ảnh thật tầng nặng vẫn thấp.
4. Nhóm cần xác nhận bản báo cáo ghép cuối cùng, phụ lục phân công và số trang tại #15 trước khi đóng gói #18. Các mảnh báo cáo hiện có không thay cho việc kiểm tra bản ghép.

## Tài liệu dùng khi tập

[`phuc-presentation.md`](phuc-presentation.md) có lời trình bày khoảng bốn phút và các con số cần nhớ. [`questions-answers.md`](questions-answers.md) có 19 câu hỏi và trả lời ngắn, gồm giả định dùng nhãn reversed, điểm gãy, pha liên tục và giới hạn ảnh tổng hợp.

Buổi tập dự kiến của nhóm là 24/11 theo #17. Mỗi người cần thực sự trình bày và nhận câu hỏi trước khi đánh dấu hoàn tất. Không đóng #17 chỉ vì đã có tài liệu.

## Nguồn đã rà

- Main: commit `7ad144b03c9259677907f6b08ec08baeb07b3bfb`.
- Slide: nhánh `14-slide-thuyet-trinh`, PR #30, tệp `report/Doc-chi-so-dong-ho-nuoc-Suon-thuyet-trinh.pptx`.
- [PR #31](https://github.com/qivarnq3g/cv-water-meter-reading/pull/31), [PR #30](https://github.com/qivarnq3g/cv-water-meter-reading/pull/30), [issue #17](https://github.com/qivarnq3g/cv-water-meter-reading/issues/17).
- [`summary.csv`](../experiments/phuc/results/summary.csv), [`e2_grid.csv`](../experiments/phuc/results/e2_grid.csv), [`e3_summary.csv`](../experiments/quang/results/e3_summary.csv), [`e4_curve.csv`](../experiments/quang/results/e4_curve.csv), [`experimental-setup.md`](experimental-setup.md).
