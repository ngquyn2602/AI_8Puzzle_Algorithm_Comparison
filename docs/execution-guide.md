# Hướng dẫn chi tiết cách chạy Thuật toán (Execution Guide)

Tài liệu này cung cấp hướng dẫn thực tế chi tiết về cách cấu hình, khởi chạy và diễn giải kết quả của các thuật toán tìm kiếm trong dự án **8-Puzzle Detective Lab**.

---

## 1. Chạy thuật toán thông qua Giao diện Web (GUI)

Đây là cách trực quan và dễ tiếp cận nhất để quan sát hoạt động của thuật toán.

1. **Khởi động Frontend và Backend** (theo hướng dẫn trong `README.md`).
2. **Truy cập Giao diện:** Mở trình duyệt tại địa chỉ `http://localhost:5173`.
3. **Chọn Vụ án hoặc Tự thiết lập:**
   - Ở cột bên trái, bạn chọn một **Detective Case** có sẵn (Ví dụ: `Easy Two-Move Scenario` hoặc `Greedy Trap`).
   - Hoặc bạn có thể click trực tiếp vào bàn cờ ở khung trung tâm để hoán đổi vị trí các ô số, tạo ra một trạng thái xuất phát (`Start State`) tùy ý.
4. **Chọn Thuật toán & Hàm đánh giá (Heuristic):**
   - Chọn thuật toán bất kỳ từ thanh menu xổ xuống ở góc cấu hình.
   - Nếu thuật toán thuộc nhóm **Tìm kiếm có thông tin** hoặc **Tìm kiếm cục bộ**, bạn có thể chọn thêm Heuristic:
     - **Manhattan Distance:** Tổng khoảng cách dịch chuyển tối thiểu (theo chiều dọc và chiều ngang) của tất cả các ô số để về đúng vị trí đích.
     - **Misplaced Tiles:** Số lượng các ô số đang nằm sai vị trí so với trạng thái đích.
5. **Chọn Giới hạn bước duyệt (Max Expansions):**
   - Đặt ngưỡng tối đa để thuật toán dừng lại (mặc định là `500`). Giúp tránh các trường hợp thuật toán chạy vô tận trên các trạng thái vô nghiệm hoặc cấu hình cực khó.
6. **Nhấn "SOLVE":**
   - Hệ thống lập tức gửi API Request lên backend, tính toán và hiển thị:
     - **Path Steps:** Các bước chuyển động (Up, Down, Left, Right) từ trạng thái đầu đến đích.
     - **Trace Matrix:** Chi tiết từng vòng lặp: tập Frontier gồm những node nào, điểm số đánh giá ra sao, vì sao node hiện tại được rút ra khỏi hàng đợi.
     - **Autopsy Report:** Báo cáo đánh giá tính tối ưu và đầy đủ.

---

## 2. Chạy thuật toán qua Giao diện Dòng lệnh (CLI)

Bộ CLI tại [api/cli.py](../api/cli.py) là công cụ đắc lực để chạy các thuật toán một cách độc lập mà không cần khởi động server FastAPI hoặc trình duyệt web.

### 2.1 Cú pháp cơ bản
Để kích hoạt CLI, trước hết bạn cần kích hoạt môi trường ảo Python của mình:
```powershell
# Kích hoạt môi trường ảo Windows
.\.venv\Scripts\Activate.ps1
```

Cú pháp lệnh chạy CLI:
```powershell
python api/cli.py [TÙY_CHỌN]
```

### 2.2 Các tham số cấu hình chính
- `--case [CASE_ID]`: Chạy thuật toán dựa trên một vụ án mẫu có sẵn.
- `--start [BOARD]`: Nhập trạng thái bắt đầu dưới dạng chuỗi số. Hỗ trợ nhiều cách nhập:
  - Chuỗi liên tục: `123456078`
  - Các số cách nhau bởi dấu phẩy: `1,2,3,4,5,6,0,7,8`
  - Bọc trong dấu ngoặc vuông: `[1,2,3,4,5,6,0,7,8]`
- `--goal [BOARD]`: Trạng thái đích muốn đạt tới. Mặc định là trạng thái giải xong chuẩn: `1,2,3,4,5,6,7,8,0`.
- `--algorithm [ALGORITHM_NAME]`: Tên thuật toán viết tắt (bfs, dfs, ucs, ids, greedy, astar, ida, minimax, alpha-beta, expectimax, hill-climbing...).
- `--heuristic [manhattan|misplaced]`: Lựa chọn hàm heuristic. Mặc định là `manhattan`.
- `--max-expansions [N]`: Giới hạn tối đa số node được mở rộng (Mặc định: `500`).
- `--trace-limit [N]`: Giới hạn số dòng lịch sử ma trận truy vết in ra Terminal (tránh làm tràn màn hình khi số bước chạy lớn). Mặc định: `12`.
- `--path-limit [N]`: Giới hạn số bước đường đi kết quả in ra màn hình. Mặc định: `20`.
- `--json`: Xuất toàn bộ kết quả tìm kiếm dưới dạng cấu trúc dữ liệu JSON để phục vụ việc lập trình hoặc lưu trữ dữ liệu.
- `--list-cases`: Hiển thị danh sách toàn bộ các vụ án mẫu đã cài sẵn.
- `--list-algorithms`: Hiển thị danh sách phân nhóm toàn bộ các thuật toán được hệ thống hỗ trợ.

---

## 3. Các Ví dụ Chạy lệnh CLI chi tiết

### Ví dụ 1: Chạy A* với trạng thái nhập thủ công
Chạy giải bài toán từ trạng thái bắt đầu `1,3,0,4,2,5,7,8,6` về đích mặc định bằng thuật toán A*:
```powershell
python api/cli.py --start "1,3,0,4,2,5,7,8,6" --algorithm astar --heuristic manhattan
```

**Kết quả hiển thị trên Terminal:**
```text
8-Puzzle Detective Lab CLI
============================
Algorithm: Tìm kiếm A* (astar)
Group: Informed Search
Found: True | Message: Target state successfully reached!
Path cost: 4 | Expanded: 6 | Generated: 12
Reached: 10 | Max frontier: 7 | Runtime: 1.15 ms
Certificate: solvable=True, path_valid=True, inversions=3/0

PEAS
- Aspect: Performance Measure: Min path length, count of node expansions
- Aspect: Environment: 8-Puzzle board 3x3 (1-8 and blank)
- Aspect: Actuators: Slide tile (Up, Down, Left, Right)
- Aspect: Sensors: Read current board layout

Start
  1 3 ·
  4 2 5
  7 8 6
Goal
  1 2 3
  4 5 6
  7 8 ·

Solution path
Step 0: Start
  1 3 ·
  4 2 5
  7 8 6
Step 1: Down
  1 3 5
  4 2 ·
  7 8 6
...
```

### Ví dụ 2: Chạy kiểm tra vụ án có sẵn
Chạy thuật toán Leo đồi (Hill Climbing) trên vụ án `case-greedy-trap` để xem thuật toán có bị mắc bẫy cực tiểu cục bộ hay không:
```powershell
python api/cli.py --case case-greedy-trap --algorithm hill-climbing
```

### Ví dụ 3: Lấy dữ liệu JSON thô để lập trình
Xuất dữ liệu chạy BFS dưới dạng JSON để sử dụng cho mục đích khác:
```powershell
python api/cli.py --case case-easy-two-moves --algorithm bfs --json
```

---

## 4. Chạy thuật toán thông qua API Endpoint

Nếu bạn muốn tích hợp lõi thuật toán vào một ứng dụng khác (ví dụ: ứng dụng mobile hoặc ứng dụng web tùy biến):

Bạn có thể gửi một POST Request bằng công cụ `curl` hoặc các thư viện HTTP của ngôn ngữ khác (như `requests` trong Python, `axios` trong JS) tới server FastAPI:

```bash
curl -X POST "http://localhost:8000/solve" \
     -H "Content-Type: application/json" \
     -d '{"start": [1,2,3,4,5,6,0,7,8], "goal": [1,2,3,4,5,6,7,8,0], "algorithm": "astar", "heuristic": "manhattan", "max_expansions": 100}'
```
API sẽ phản hồi bằng một JSON `SearchResult` chứa đầy đủ thông tin tìm kiếm, ma trận truy vết và phân tích khám nghiệm.
