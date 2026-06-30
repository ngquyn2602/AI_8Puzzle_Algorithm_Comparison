# Lộ trình Phát triển Dự án (Project Roadmap)

Lộ trình phát triển **8-Puzzle Detective Lab** tập trung vào việc gia tăng tính năng sư phạm, bổ sung thêm các nhóm thuật toán mới và tăng cường giao diện tương tác trực quan.

## Phase 1: Nền tảng cốt lõi (Đã hoàn thành)
- Xây dựng lõi thuật toán 8-Puzzle cho 6 nhóm thuật toán chính.
- Triển khai Backend FastAPI + REST API phục vụ Frontend.
- Thiết lập giao diện React tương tác với Trace Matrix (Ma trận truy vết Frontier và Node được chọn).
- Xây dựng CLI chạy thuật toán trực tiếp và hỗ trợ xuất báo cáo PDF/HTML/Markdown.
- Hoàn thiện tài liệu thuật toán và 22 GIF trace trong repo; tách rõ solver chuẩn, mô hình bounded và local repair.

## Phase 2: Mở rộng Thuật toán & Trực quan hóa (Đang thực hiện)
- **Tích hợp Thuật toán Di truyền (Genetic Algorithm - GA):** 
  - Thêm GA để giải bài toán 8-Puzzle và các bài toán tối ưu hóa lân cận. Học viên có thể cấu hình kích thước quần thể (population size), tỷ lệ đột biến (mutation rate) và tỷ lệ lai ghép (crossover rate).
- **Heuristic Máy học (ML-based Heuristic):**
  - Huấn luyện một mạng thần kinh nhân tạo nhỏ (như MLP hoặc CNN) để tự động học hàm Heuristic `h(n)` từ hàng triệu trạng thái 8-Puzzle có sẵn lời giải tối ưu thay vì sử dụng khoảng cách Manhattan viết tay.
- **Trực quan hóa Cây Tìm kiếm (Interactive Search Tree Visualization):**
  - Xây dựng sơ đồ cây tìm kiếm 2D/3D (Node Link Tree Diagram) tương tác trực quan cho phép người dùng click zoom vào từng Node trên cây để xem cách cây tìm kiếm nở rộng theo thời gian thực (real-time tree expansion).

## Phase 3: Nâng cấp Môi trường Phức tạp & Cộng đồng (Kế hoạch tương lai)
- **Hỗ trợ Kích thước Bảng lớn hơn:** Mở rộng không gian trạng thái từ 8-Puzzle (3x3) lên 15-Puzzle (4x4) và 24-Puzzle (5x5).
- **Hệ thống tạo Đề bài & Đấu trường AI (AI Arena):**
  - Cho phép người dùng tự tải lên các kịch bản vụ án riêng biệt bằng file JSON.
  - Xây dựng đấu trường cho phép 2 thuật toán AI đối đầu trực tiếp xem thuật toán nào tìm ra lời giải nhanh hơn hoặc ít tốn bộ nhớ hơn.
- **Đóng gói Thư viện (SDK):** Đóng gói lõi `eight_puzzle_detective_core.py` thành một thư viện Python độc lập có thể cài đặt dễ dàng qua `pip` phục vụ nghiên cứu.
