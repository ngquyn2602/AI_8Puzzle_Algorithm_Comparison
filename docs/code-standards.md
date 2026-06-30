# Tiêu chuẩn Lập trình (Code Standards)

Tài liệu này định nghĩa các quy tắc lập trình, quy chuẩn cấu trúc và cách tổ chức mã nguồn nhằm duy trì tính nhất quán và dễ bảo trì cho dự án.

## 1. Backend (Python)

### 1.1 Tính Bất biến (Immutability) của Trạng thái
- Trạng thái bàn cờ 8-Puzzle bắt buộc phải sử dụng **`tuple[int, ...]`** thay vì `list`.
- Tuple đảm bảo tính bất biến (immutable), giúp tránh lỗi tham chiếu ngoài ý muốn và cho phép lưu trạng thái trực tiếp làm khóa (key) trong tập hợp `set` (như tập `explored` hoặc `visited`) hoặc làm khóa của Dictionary.

### 1.2 Quy tắc viết thuật toán tìm kiếm
- Mỗi thuật toán tìm kiếm cần trả về kiểu dữ liệu `SearchResult` hoặc cấu trúc tương ứng đầy đủ.
- Mọi hàm thuật toán đều phải nhận tham số giới hạn `max_expansions` (số node mở rộng tối đa) để tránh bị lặp vô tận và tràn bộ nhớ RAM của Server.
- Cần ghi lại lịch sử duyệt qua danh sách `trace_rows` ở mỗi vòng lặp để phục vụ cho tính năng ma trận truy vết (Trace Matrix) ở Frontend.

### 1.3 Quy chuẩn viết code
- Tuân thủ chuẩn **PEP-8**.
- Bắt buộc khai báo Type Hinting đầy đủ cho tất cả các tham số truyền vào và kiểu dữ liệu trả về của hàm.
- Tên biến sử dụng kiểu `snake_case`. Tên lớp sử dụng kiểu `PascalCase`.

---

## 2. Frontend (TypeScript & React)

### 2.1 Quản lý trạng thái và Kiểu dữ liệu
- Không dùng kiểu dữ liệu `any`. Tất cả dữ liệu trả về từ API đều phải được định nghĩa kiểu cụ thể tại [types.ts](../web/src/types.ts).
- Các components tương tác cần được viết bằng TypeScript dưới dạng Function Components (`React.FC` hoặc khai báo hàm chuẩn).

### 2.2 Quy chuẩn Giao diện & CSS
- Sử dụng Tailwind CSS để cấu hình giao diện nhanh chóng và nhất quán.
- Thiết kế Responsive: Giao diện phải hiển thị tốt trên cả màn hình máy tính (khuyên dùng để xem Trace Matrix) và thiết bị di động.
- Màu sắc chủ đạo phải theo concept "Phòng thí nghiệm thám tử" (Detective Lab) mang màu sắc chuyên nghiệp, trực quan học thuật cao.
