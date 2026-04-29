# 16. Hướng dẫn chạy Streamlit Prototype

Tài liệu này mô tả cách chạy ứng dụng Streamlit trong `visual/streamlit_app/` để demo 3 dashboard BI bằng mock data.

## 16.1 Điều kiện tiên quyết

- Windows + PowerShell
- Python 3.9+
- Đã clone đầy đủ project

## 16.2 Cài đặt môi trường

Chạy tại root project:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Nếu đã có `.venv` thì chỉ cần activate và cài bổ sung package nếu thiếu.

## 16.3 Lệnh chạy Streamlit

Từ root project:

```powershell
.\.venv\Scripts\activate
.\.venv\Scripts\streamlit.exe run visual/streamlit_app/app.py
```

Ứng dụng sẽ mở mặc định tại:

- `http://localhost:8501`

## 16.4 Nội dung demo trong app

App gồm 3 dashboard:

- Revenue and Genre
- Audience Engagement
- Customer Segmentation

Nguồn dữ liệu hiện tại là mock data từ `visual/streamlit_app/data.py`.

## 16.5 Dừng app

Trong cửa sổ terminal đang chạy Streamlit:

- Nhấn `Ctrl + C` để dừng server.

## 16.6 Troubleshooting nhanh

1. Lỗi `streamlit is not recognized`

- Nguyên nhân: chưa activate đúng venv.
- Cách xử lý: chạy lại `.\.venv\Scripts\activate` rồi dùng đường dẫn đầy đủ `.\.venv\Scripts\streamlit.exe`.

2. Lỗi `Port 8501 is already in use`

- Cách xử lý: đổi port khác:

```powershell
.\.venv\Scripts\streamlit.exe run visual/streamlit_app/app.py --server.port 8502
```

3. Lỗi thiếu thư viện (`ModuleNotFoundError`)

- Cách xử lý:

```powershell
pip install -r requirements.txt
```

## 16.7 Chuyển từ prototype sang dữ liệu thật

Khi pipeline đã có dữ liệu thật (Task 3), có 2 hướng:

- Hướng 1: giữ Streamlit, thay các hàm `get_*()` trong `data.py` bằng đọc CSV trong `visual/exports/`.
- Hướng 2: chuyển sang Power BI production theo `visual/CONNECTION_GUIDE.md`.
