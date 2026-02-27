# MPE Benchmark Đa Tác Nhân 🎮🤖

Bộ tiêu chí kiểm tra học tăng cường đa tác nhân dựa trên môi trường PettingZoo MPE, với quyết định tác nhân được điều khiển bởi API LLM được tích hợp.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PettingZoo](https://img.shields.io/badge/PettingZoo-MPE-green.svg)](https://pettingzoo.farama.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

🌐 **Có sẵn trong**: [English](README_en.md) | [中文](README_zh.md) | [日本語](README_ja.md) | [Tiếng Việt](README_vi.md)

---

## 🌟 Điểm Nổi Bật Dự Án

- 🎯 **9 Môi Trường Cổ Điển**: Bao gồm các kịch bản hợp tác, đối kháng và truyền thông
- 🤖 **Tích Hợp LLM**: Hỗ trợ OpenAI, DeepSeek, Qwen, Gemini
- 📊 **Phân Tích Chuẩn Hóa**: Chuyển đổi quan sát thô sang định dạng JSON thân thiện với LLM
- 📝 **Tài Liệu Toàn Diện**: Hướng dẫn đầy đủ từ bắt đầu nhanh đến phát triển nâng cao
- 🔧 **Thiết Kế Mô Đun**: Dễ mở rộng và tùy chỉnh

## 📁 Cấu Trúc Dự Án

```
MPE_muiltiagent_benchmark/
├── 📄 Tệp Cấu Hình
│   ├── requirements.txt          # Phụ thuộc Python
│   ├── requirements.lock         # Phiên bản được ghim (tái sản xuất)
│   ├── pyproject.toml           # Cấu hình dự án
│   ├── .env.example             # Mẫu khóa API
│   └── .gitignore               # Quy tắc bỏ qua Git
│
├── 📚 Tài Liệu (docs/)
│   ├── README.md                # Trung tâm Tài liệu
│   ├── getting_started/         # Hướng dẫn bắt đầu
│   │   ├── quickstart.md        # ⭐ Bắt đầu nhanh
│   │   ├── environment_setup.md # Thiết lập môi trường
│   │   ├── dependency_management.md # Quản lý phụ thuộc
│   │   └── overview.md          # Tổng quan dự án
│   ├── configuration/           # Hướng dẫn cấu hình
│   │   └── api_keys.md          # 🔑 Quản lý khóa API
│   ├── architecture/            # Kiến trúc & Thiết kế
│   │   ├── observation_space.md # Phân tích quan sát
│   │   ├── logging_system.md    # 📊 Hệ thống Ghi nhật ký
│   │   └── models.md            # 🤖 Hướng dẫn sử dụng Mô hình
│   ├── experiments/             # Hướng dẫn Thí nghiệm
│   │   ├── reproducibility.md   # 🎲 Sửa hạt giống
│   │   ├── running_benchmarks.md # Chạy Benchmark
│   │   └── benchmark_review.md  # 📈 Phân tích Benchmark
│   └── dev_notes/               # Ghi chú Nhà phát triển
│       ├── work_summary.md      # Tóm tắt Công việc
│       ├── workflow_standardization.md # Chuẩn hóa Quy trình
│       └── api_keys_refactor.md # Nhật ký Di chuyển Khóa API
│
├── 🎮 Triển Khai Môi Trường (9 trò chơi hoàn chỉnh)
│   ├── spread_API.py            # Simple Spread
│   ├── adv_API.py               # Simple Adversary
│   ├── tag_API.py               # Simple Tag
│   ├── push.py                  # Simple Push
│   ├── crypto.py                # Simple Crypto
│   ├── reference.py             # Simple Reference
│   ├── speaker_listener.py      # Simple Speaker Listener
│   ├── world_comm.py            # Simple World Comm
│   ├── simple.py                # Simple (Basic)
│   └── utils_api.py             # Giao diện API LLM Thống nhất
│
├── 🧪 Kiểm tra & Công cụ
│   ├── benchmark_runner.py      # ✅ Khung Kiểm tra Hàng loạt
│   ├── setup_api_keys.py        # ✅ Tập lệnh Thiết lập Khóa API
│   ├── verify_environment.py    # ✅ Xác minh Môi trường
│   └── test_unified_api.py      # Kiểm tra API
│
├── 🔍 Phân Tích Quan Sát (obs/)
│   ├── parse_*_obs.py           # 9 Trình phân tích Môi trường
│   └── utils.py                 # Các hàm Tiện ích chung
│
├── 💬 Kỹ Thuật Nhắc (prompt/)
│   └── prompt_for_*.py          # Các Mô đun Nhắc chuẩn hóa
│
└── 📊 Đầu Ra Kết Quả (results/)
    └── benchmarks/<env>/        # Kết quả Kiểm tra theo Môi trường
        ├── *.mp4                # Ghi âm Video
        └── *.json               # Nhật ký Chi tiết
```

## 🚀 Bắt Đầu Nhanh

### Yêu Cầu Hệ Thống

- **Python**: 3.8+ (Khuyến nghị: 3.12.3, đã kiểm tra)
- **Hệ Điều Hành**: Linux / macOS / Windows
- **Trình Quản Lý Phụ Thuộc**: pip / conda / uv

### 1. Cài Đặt Phụ Thuộc

```bash
# Clone kho lưu trữ
git clone https://github.com/HuangShengZeBlueSky/MPE_muiltiagent_benchmark.git
cd MPE_muiltiagent_benchmark

# Tùy Chọn A: Sử Dụng venv (Khuyến nghị)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt

# Tùy Chọn B: Sử Dụng conda
conda create -n mpe-bench python=3.12
conda activate mpe-bench
pip install -r requirements.txt

# Tùy Chọn C: Cài đặt Trực tiếp (Không khuyến nghị)
pip install -r requirements.txt
```

**Xác Minh Cài Đặt**:
```bash
# Chạy tập lệnh Xác minh Môi trường
python verify_environment.py
# ✅ Tất cả các kiểm tra thông qua có nghĩa là thiết lập thành công
```

**📖 Hướng Dẫn Chi Tiết**: Xem [docs/getting_started/environment_setup.md](docs/getting_started/environment_setup.md)

### 2. Định Cấu Hình Khóa API 🔑

#### Phương Pháp A: Cấu Hình Tương Tác (Khuyến Nghị)
```bash
python setup_api_keys.py
```

#### Phương Pháp B: Cấu Hình Thủ Công
```bash
# Sao chép mẫu và chỉnh sửa
cp .env.example .env
nano .env  # Thêm khóa API của bạn
```

#### Phương Pháp C: Biến Môi Trường
```bash
export QWEN_API_KEY="sk-your-key"
export DEEPSEEK_API_KEY="sk-your-key"
export OPENAI_API_KEY="sk-your-key"
```

**Nhận Khóa API**:
- Qwen (Khuyến nghị): https://dashscope.console.aliyun.com
- DeepSeek: https://platform.deepseek.com
- OpenAI: https://platform.openai.com/api-keys
- Gemini: https://aistudio.google.com/apikey

**📖 Cấu Hình Chi Tiết**: Xem [docs/configuration/api_keys.md](docs/configuration/api_keys.md)

### 3. Chạy Kiểm Tra

#### Kiểm Tra Môi Trường Đơn
```bash
# Chạy một trò chơi duy nhất (sử dụng API Qwen theo mặc định)
python adv_API.py
python spread_API.py
python tag_API.py
```

#### Kiểm Tra Benchmark Hàng Loạt (Khuyến Nghị)
```bash
# Chạy 10 tập Adversary với hạt 1-10
python benchmark_runner.py

# Môi trường tùy chỉnh và số tập
python -c "from benchmark_runner import run_benchmark; run_benchmark(env_name='spread', provider='qwen', episodes=20, seed_start=1)"
```

**Đầu Ra**: Tự động lưu video (`*.mp4`) và nhật ký (`*.json`) vào `results/benchmarks/<env>/`

**📖 Hướng Dẫn Chi Tiết**: [docs/getting_started/quickstart.md](docs/getting_started/quickstart.md)

## 📚 Hướng Dẫn Tài Liệu

**Chỉ Mục Tài Liệu Hoàn Chỉnh**: [docs/README.md](docs/README.md) 📖

### 🚀 Bắt Đầu
- [Bắt Đầu Nhanh](docs/getting_started/quickstart.md) - Chạy trong 5 phút
- [Thiết Lập Môi Trường](docs/getting_started/environment_setup.md) - Hướng dẫn Thiết lập Chi tiết
- [Quản Lý Phụ Thuộc](docs/getting_started/dependency_management.md) - requirements.txt vs requirements.lock
- [Tổng Quan Dự Án](docs/getting_started/overview.md) - Kiến trúc Dự án

### ⚙️ Cấu Hình
- [Cấu Hình Khóa API](docs/configuration/api_keys.md) - Quản lý Khóa API An toàn

### 🏗️ Kiến Trúc
- [Không Gian Quan Sát](docs/architecture/observation_space.md) - Phát triển Phân tích
- [Hệ Thống Ghi Nhật Ký](docs/architecture/logging_system.md) - Đặc Tả Định Dạng Nhật Ký
- [Hướng Dẫn Sử Dụng Mô Hình](docs/architecture/models.md) - Hỗ Trợ LLM

### 🧪 Thí Nghiệm
- [Thí Nghiệm Có Thể Tái Sản Xuất](docs/experiments/reproducibility.md) - Hướng Dẫn Sửa Hạt
- [Chạy Benchmark](docs/experiments/running_benchmarks.md) - Quy Trình Kiểm Tra Hàng Loạt
- [Đánh Giá Benchmark](docs/experiments/benchmark_review.md) - Phân Tích Nhật Ký Đa Vai Trò

### 🛠️ Ghi Chú Nhà Phát Triển
- [Tóm Tắt Công Việc](docs/dev_notes/work_summary.md) - Lịch Sử Phát Triển v1.0
- [Chuẩn Hóa Quy Trình](docs/dev_notes/workflow_standardization.md) - Nguyên Tắc Thiết Kế
- [Cấu Trúc Lại Khóa API](docs/dev_notes/api_keys_refactor.md) - Nhật Ký Di Chuyển

## 🛠️ Trạng Thái Phát Triển

### Hoàn Thành ✅ (Phiên Bản 1.0)
- [x] **9 Môi Trường Hoàn Chỉnh** (spread, adversary, tag, push, crypto, reference, speaker_listener, world_comm, simple)
- [x] **Giao Diện API LLM Thống Nhất** (Từ xa: qwen/deepseek/gpt/gemini; Cục Bộ: transformers/ollama/vllm)
- [x] **Trình Phân Tích Quan Sát** (9 môi trường với đầu ra JSON chuẩn hóa)
- [x] **Chuẩn Hóa Nhắc** (4 hàm mô đun × 9 môi trường)
- [x] **Hệ Thống Ghi Nhật Ký** (obs + action + thought + reward + final_summary)
- [x] **Khung Benchmark** (Kiểm tra Hàng loạt + Phân tích Thống kê)
- [x] **Cơ Chế Hạt** (1-20 thí nghiệm có thể tái sản xuất)
- [x] **Quản Lý Khóa API** (Tệp .env + Tập lệnh Thiết lập Tương tác)
- [x] **Tài Liệu** (15+ tài liệu Markdown)
- [x] **Ghi Hình Video** (Tự động tạo mp4 mỗi tập)

### Phạm Vi Kiểm Tra ✅
- [x] Tất cả 9 môi trường chạy độc lập
- [x] Khung Benchmark kiểm tra tất cả các môi trường
- [x] Xác minh Sửa hạt
- [x] Định dạng Nhật ký Thống nhất và Hoàn chỉnh
- [x] Quản lý An toàn Khóa API

### Lên Kế Hoạch 📅 (Phiên Bản 1.1+)
- [ ] Cơ sở dữ liệu Tiêu chí Hiệu suất
- [ ] Dashboard Trực Quan Hóa Tương Tác
- [ ] Thư Viện Ví Dụ Few-shot
- [ ] Kiểm Tra Song Song Đa Quy Trình
- [ ] Hỗ Trợ Mô Hình Cục Bộ Nhiều Hơn

## 🤝 Đóng Góp

Mong Đợi Đóng Góp! Các Bước:

1. Fork kho lưu trữ
2. Tạo nhánh tính năng của bạn (`git checkout -b feature/AmazingFeature`)
3. Cam Kết Thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Đẩy đến nhánh (`git push origin feature/AmazingFeature`)
5. Mở Yêu Cầu Kéo

**Khu Vực Đóng Góp**:
- Triển khai Trình phân tích cho Môi trường mới
- Cải thiện Mẫu Kỹ Thuật Nhắc
- Thêm Số Liệu Đánh Giá mới
- Nâng cấp Tài liệu và Ví dụ

## 📄 Giấy Phép

Dự án này được cấp phép theo Giấy Phép MIT - xem tệp [LICENSE](LICENSE)

## 🙏 Lời Cảm Ơn

- [PettingZoo](https://pettingzoo.farama.org/) - Thư Viện Môi Trường Đa Tác Nhân
- [OpenAI](https://openai.com/) - API LLM
- Tất cả Người Đóng Góp

## 📧 Liên Hệ

- **Tác Giả**: HuangShengZeBlueSky
- **Kho Lưu Trữ**: https://github.com/HuangShengZeBlueSky/MPE_muiltiagent_benchmark
- **Vấn Đề**: [GitHub Issues](https://github.com/HuangShengZeBlueSky/MPE_muiltiagent_benchmark/issues)

## ⭐ Lịch Sử Sao

Nếu Dự Án này Hữu Ích cho Bạn, Vui Lòng Cho Chúng Tôi Một Sao ⭐!

---

**Cập Nhật Lần Cuối**: 2026-01-26  
**Phiên Bản**: 1.0.0 - Tất Cả Các Tính Năng Cốt Lõi Hoàn Thành  
**Trạng Thái**: ✅ Sẵn Sàng Cho Sản Xuất
