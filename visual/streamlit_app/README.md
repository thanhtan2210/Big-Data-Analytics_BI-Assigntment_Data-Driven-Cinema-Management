# Cinema BI Dashboard — Streamlit Prototype

Ứng dụng web prototype visualise 3 dashboard BI với mock data, trước khi chuyển lên Power BI production.

---

## Yêu cầu

- Python 3.9+
- Các thư viện trong `requirements.txt`

---

## Cài đặt

Dùng venv chung ở root project (một venv cho toàn bộ dự án):

```powershell
# từ root project
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

---

## Chạy ứng dụng

```powershell
# từ root project (activate venv trước)
.\.venv\Scripts\activate
.\.venv\Scripts\streamlit.exe run visual/streamlit_app/app.py
```

Mặc định mở tại **http://localhost:8501**

---

## Cấu trúc

```
streamlit_app/
├── app.py            # Entry point — toàn bộ UI và chart logic
├── data.py           # Mock data generators (9 hàm, ~300 dòng)
├── requirements.txt  # Dependencies
└── README.md         # File này
```

---

## 3 Dashboard

| Dashboard                | Nội dung                          | Charts                                                                       |
| ------------------------ | --------------------------------- | ---------------------------------------------------------------------------- |
| 📊 Revenue & Genre       | Doanh thu theo thể loại, ROI      | Bar, Bubble, Line theo thập kỷ, Treemap, Top-20 table                        |
| 👥 Audience Engagement   | Xu hướng đánh giá, phân bố rating | Bar, Histogram, Dual-axis timeline, Heatmap, Combo bar+line + Quadrant table |
| 🎯 Customer Segmentation | Phân khúc người dùng, ALS gợi ý   | Donut, Grouped bar, Tag bar, Recs table, Scatter                             |

---

## Dữ liệu

Toàn bộ dữ liệu là **mock data** sinh từ `data.py` — phản ánh cấu trúc schema thực của MongoDB collections được mô tả trong [`visual/CONNECTION_GUIDE.md`](../visual/CONNECTION_GUIDE.md).

Khi pipeline PySpark hoàn tất, thay các hàm `get_*()` trong `data.py` bằng queries thực từ MongoDB hoặc đọc CSV từ `dataset/`.

---

## Chuyển sang Power BI

Xem hướng dẫn kết nối tại [`visual/CONNECTION_GUIDE.md`](../visual/CONNECTION_GUIDE.md) và mô tả chart tại [`visual/DASHBOARDS.md`](../visual/DASHBOARDS.md).
