# Tổng quan Dự án & PDR (Project Definition Record)

## 1. Giới thiệu dự án
**8-Puzzle Detective Lab** là một phòng thí nghiệm giả lập AI tương tác, được xây dựng để nghiên cứu, giảng dạy và trực quan hóa hoạt động của 6 nhóm thuật toán tìm kiếm phổ biến trong Khoa học Máy tính. Dự án biến việc hiểu các thuật toán tìm kiếm trừu tượng (như BFS, A*, Leo đồi, Minimax) thành một trải nghiệm giải quyết các "hồ sơ thám tử" (cases).

## 2. Mô hình PEAS (Problem Environment Agent System)
Các thuật toán tìm kiếm trong dự án được triển khai dựa trên cấu trúc tác nhân thông minh (Intelligent Agent) trong AI:
- **Performance Measure (Tiêu chuẩn đánh giá):** 
  - Đảm bảo tìm ra lời giải ngắn nhất (Tối ưu - Optimality).
  - Số lượng Node cần duyệt (Độ phức tạp không gian) ít nhất.
  - Thời gian tính toán bằng mili-giây (Runtime MS) thấp nhất.
- **Environment (Môi trường):**
  - Trò chơi 8-Puzzle: Bảng 3x3 chứa các ô số từ 1 đến 8 và 1 ô trống. Môi trường là tĩnh (Static), tất cả ô số đều hiển thị đầy đủ (Fully Observable), tất cả hành động dịch chuyển ô đều xác định rõ ràng (Deterministic).
  - Trò chơi Caro 3x3: Môi trường có tính đối kháng (Adversarial) và có thể mở rộng xác suất (Stochastic - Expectimax).
- **Actuators (Cơ cấu tác động):**
  - Hành động dịch chuyển ô trống: Lên (UP), Xuống (DOWN), Trái (LEFT), Phải (RIGHT).
- **Sensors (Bộ cảm biến):**
  - Nhận biết cấu hình hiện tại của bảng (Trạng thái bảng - State) gồm vị trí các ô số và ô trống (ô `0`).

## 3. Khách hàng & Đối tượng mục tiêu
- **Sinh viên & Học viên AI:** Muốn hiểu rõ cơ chế từng thuật toán qua trực quan và ma trận truy vết từng bước.
- **Giảng viên:** Sử dụng làm công cụ trực quan hóa trong các bài giảng về Tìm kiếm Trạng thái & Tối ưu hóa.

## 4. Các tính năng cốt lõi
- **Trình diễn Thuật toán (Execution & Trace Matrix):** Hiển thị danh sách Frontier (Hàng đợi) trước khi chọn Node tiếp theo để giải thích vì sao Node đó được chọn.
- **Phân tích Khám nghiệm (Algorithm Autopsy):** Đánh giá tính đầy đủ, độ tối ưu của thuật toán và các bẫy cục bộ.
- **Hồ sơ thám tử mẫu (Cases):** 6 ca điều tra cài đặt sẵn tương ứng với 6 vấn đề thuật toán đặc thù.
- **Hệ thống CLI chuyên dụng:** Chạy trực tiếp qua Terminal cho phép lập trình viên phân tích sâu qua luồng xuất dữ liệu JSON hoặc báo cáo văn bản có định dạng.
- **Tài liệu và GIF trong repo:** Mỗi thuật toán đang hiển thị có một GIF sinh từ trace backend thật, được lập chỉ mục tại `docs/algorithms/index.md`.

## 5. Tiêu chí nghiệm thu học thuật

- Local Beam phải duy trì nhiều trạng thái (`k=3`), không giả làm Steepest-Ascent.
- CSP Backtracking chỉ claim trong horizon giới hạn; Min-Conflicts được ghi rõ là local repair, không phải solver blank-move chuẩn.
- Minimax, Alpha-Beta, Expectimax dùng cây Caro/chance giới hạn độ sâu và xuất thống kê đánh giá.
- Đủ 22 GIF hợp lệ, một GIF cho mỗi thuật toán đang hiển thị; manifest và `--check` phải khớp.
