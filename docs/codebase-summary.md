# Tóm tắt cấu trúc Mã nguồn (Codebase Summary)

Tài liệu này tóm tắt cấu trúc và phân tích chi tiết các file mã nguồn cốt lõi trong hệ thống **8-Puzzle Detective Lab**.

## 1. Bản đồ Mã nguồn (Codebase Map)

Hệ thống được thiết kế dạng **Monorepo** chia làm 3 phần chính: Backend (FastAPI), Giao diện (React) và Tài liệu (Docs).

```text
8-Puzzle-Detective/
├── api/                             # Backend (Python / FastAPI)
│   ├── main.py                      # Router API, khởi chạy server, export report
│   ├── eight_puzzle_detective_core.py # Chứa LÕI cấu trúc dữ liệu và tất cả thuật toán tìm kiếm
│   ├── cli.py                       # CLI để tương tác trực tiếp với lõi qua Terminal
│   ├── requirements.txt             # Các thư viện Python cần dùng (FastAPI, uvicorn, pytest, reportlab...)
│   └── tests/                       # Unit Test cho lõi
│       └── test_detective_core.py   # Test lõi, API, CLI và GIF generator
├── web/                             # Frontend (React / TypeScript / Vite)
│   ├── src/
│   │   ├── main.tsx                 # Entrypoint khởi tạo React
│   │   ├── App.tsx                  # Component chính điều khiển luồng, layout thám tử
│   │   ├── api-client.ts            # Client HTTP gọi sang API FastAPI
│   │   ├── types.ts                 # Định nghĩa kiểu dữ liệu TS (State, Trace, Autopsy...)
│   │   ├── styles.css               # CSS styling chính
│   │   ├── algorithm-constants.ts   # Hằng số nhóm thuật toán hiển thị trên UI
│   │   └── components/              # Các components UI nhỏ gọn
├── docs/                            # Tài nguyên tài liệu và tệp bổ sung
```

### 1.1 Tài liệu thuật toán và GIF trace

- `docs/algorithms/index.md`: tài liệu thuật toán, ranh giới solver chuẩn vs mô hình học thuật, gallery GIF.
- `docs/assets/algorithm-gifs/`: 22 GIF trace cho thuật toán đang hiển thị.
- `scripts/capture_web_algorithm_frames.mjs`: mở React bằng Playwright, chọn/chạy đúng alias và chụp panel trace thật.
- `scripts/generate_algorithm_gifs.py`: ghép frame web thành GIF; `--check` xác minh nguồn capture, header và SHA-256.
- `api/requirements.txt`: có `Pillow` để script sinh GIF chạy được trên máy mới clone.
- Lõi trace tách rõ: Local Beam thật (`k=3`), CSP Backtracking bounded với legal transition, Min-Conflicts local repair, và cây Caro/chance depth-bounded cho Minimax/Alpha-Beta/Expectimax.

---

## 2. Chi tiết các Tệp lõi Backend (`api/`)

### 2.1 [eight_puzzle_detective_core.py](../api/eight_puzzle_detective_core.py)
Đây là tệp quan trọng nhất của hệ thống, chứa toàn bộ định nghĩa toán học và lập trình của các tác vụ tìm kiếm:

- **Định nghĩa Trạng thái (State):** `State = tuple[int, ...]` là một tuple gồm 9 phần tử đại diện cho lưới 3x3. `0` là ô trống. Ví dụ: `(1, 2, 3, 4, 5, 6, 7, 8, 0)` là trạng thái đích (Goal).
- **Lớp Dữ liệu (Dataclasses):**
  - `Node`: Đại diện node tìm kiếm với `state`, `parent`, `action`, `g`, `h`; thuộc tính `f` trả về `g + h`.
  - `DetectiveCase`: Cấu hình một ca điều tra mẫu (`id`, `title`, `start`, `goal`, `algorithm`, `lesson`).
  - `SearchResult`: Kết quả trả về cho API/CLI, gồm path, trace, certificate, autopsy và claim complete/optimal.
- **Hàm hỗ trợ logic:**
  - `normalize_state()`: Chuẩn hóa đầu vào của người dùng.
  - `legal_moves()`: Sinh các trạng thái láng giềng bằng legal blank moves.
  - `inversions()` và `is_solvable()`: Kiểm tra parity của cấu hình 8-Puzzle.
- **Điểm phân phối:** `solve()` chuẩn hóa alias rồi chuyển đến `graph_search()`, `ids()`, `ida_star()`, `local_demo()`, `local_beam_demo()`, `csp_backtracking_demo()`, `min_conflicts_demo()`, `caro_demo()` hoặc `educational_demo()`.
- **Ranh giới:** Graph/BFS/UCS/IDS/Greedy/A*/IDA* là solver đường đi; Complex/CSP Definition là mô hình học thuật; CSP Backtracking là bounded transition search; Min-Conflicts là local repair; Minimax/Alpha-Beta/Expectimax chạy trên Caro 3x3 depth-bounded.

### 2.2 [main.py](../api/main.py)
Cung cấp cổng API RESTful phục vụ cho Frontend React.
- **Các Endpoint chính:**
  - `GET /healthz`: Kiểm tra trạng thái hoạt động của Server.
  - `GET /api/cases`, `GET /api/algorithms`, `GET /api/algorithm-groups`: Trả dữ liệu ca mẫu và taxonomy.
  - `POST /api/run`: Chạy một thuật toán và trả về `SearchResult` dạng JSON.
  - `POST /api/predict`, `POST /api/benchmark`: Kiểm tra dự đoán và so sánh thuật toán.
  - `POST /api/export`: Tạo gói báo cáo Markdown/CSV/HTML/DOCX/PDF mã hóa trong JSON.

### 2.3 [cli.py](../api/cli.py)
Cung cấp giao diện dòng lệnh (CLI). Giúp nhà phát triển kiểm tra nhanh chóng mà không cần chạy Web Browser. Hỗ trợ xuất dữ liệu ra định dạng JSON máy đọc hoặc Báo cáo thám tử định dạng text trực quan trên Console.

---

## 3. Chi tiết Giao diện Frontend (`web/`)

### 3.1 [App.tsx](../web/src/App.tsx)
Quản lý toàn bộ State chính của giao diện:
- Chọn vụ án mẫu (Case) hoặc nhập trạng thái bàn cờ thủ công.
- Chọn Thuật toán và Heuristic (Manhattan / Misplaced).
- Hiển thị Bảng 8-Puzzle trực quan sinh động dưới dạng phòng thí nghiệm thám tử.
- Bảng ma trận truy vết từng bước chạy (Frontier, Selected Node, Scores g, h, f).
- Báo cáo khám nghiệm thuật toán (Autopsy Report).

### 3.2 [api-client.ts](../web/src/api-client.ts)
Sử dụng `fetch` để kết nối và truyền nhận dữ liệu với FastAPI Server. Tự động xử lý địa chỉ API từ biến môi trường `VITE_API_URL`.
