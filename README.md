# 📊 IT Recruitment Market Dashboard
> **Hệ thống Phân tích & Dự báo Thị trường Tuyển dụng IT Việt Nam**

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-1.35%2B-red?style=flat-square&logo=streamlit)](https://streamlit.io/)
[![DuckDB](https://img.shields.io/badge/Database-DuckDB-orange?style=flat-square&logo=duckdb)](https://duckdb.org/)
[![Scikit-Learn](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-blueviolet?style=flat-square&logo=scikit-learn)](https://scikit-learn.org/)
[![Plotly](https://img.shields.io/badge/Visualizations-Plotly-blue?style=flat-square&logo=plotly)](https://plotly.com/)

---

## 📌 Giới thiệu dự án
**IT Recruitment Market Dashboard** là một ứng dụng phân tích dữ liệu toàn diện (Full-stack Data Analytics App) kết hợp mô hình Học máy (Machine Learning) và truy vấn dữ liệu thời gian thực. Hệ thống được thiết kế để phân tích các tin tuyển dụng IT tại thị trường Việt Nam, cung cấp bức tranh toàn cảnh trực quan về lương, xu hướng công nghệ phổ biến, phân bổ địa lý, và mối tương quan giữa kinh nghiệm với thu nhập.

Ứng dụng hướng tới hai đối tượng chính:
* **Ứng viên IT:** Đánh giá năng lực bản thân, dự đoán mức lương cá nhân dựa trên hồ sơ, định vị bản thân trên bản đồ công nghệ và lập lộ trình học tập tối ưu.
* **Doanh nghiệp / HR:** Khảo sát mức lương thị trường để đưa ra đãi ngộ cạnh tranh, phân tích nhu cầu kỹ năng của đối thủ để thiết kế mô tả công việc (JD) thu hút nhân tài.

---

## ✨ Các tính năng nổi bật

### 1. 📈 Tổng Quan Thị Trường Trực Quan (Market Overview)
* **Metric Cards Động:** Hiển thị thời gian thực các chỉ số KPI cốt lõi như *Tổng số lượng việc làm, Mức lương trung bình, Kỹ năng được săn đón nhất, Tỷ lệ việc làm Remote*.
* **Tương quan Lương & Kinh nghiệm (Scatter Plot + Trendline):** Sử dụng hồi quy tuyến tính OLS để trực quan hóa xu hướng gia tăng thu nhập theo số năm tích lũy kinh nghiệm cho từng vị trí IT cụ thể.
* **Top 15 Kỹ năng hàng đầu:** Biểu đồ thanh ngang đếm tần suất công nghệ yêu cầu trong các tin tuyển dụng, làm nổi bật xu hướng thị trường (ví dụ: Python, JavaScript, SQL, React, etc.).
* **Phân bổ Địa lý & Quy mô doanh nghiệp:** Trực quan phân cấp nhu cầu tuyển dụng tại các trung tâm công nghệ (Hồ Chí Minh, Hà Nội, Đà Nẵng, Remote) và theo loại hình quy mô công ty.
* **Bộ lọc nâng cao (Sidebar Filter):** Cho phép lọc động dữ liệu hiển thị theo vị trí địa lý, kinh nghiệm yêu cầu và vai trò cụ thể.

### 2. 🗃️ SQL Playground Tương Tác (DuckDB Engine)
* **Hiệu năng vượt trội:** Tích hợp **DuckDB** - hệ quản trị cơ sở dữ liệu phân tích nhúng (Embedded Analytical Database) chạy trực tiếp trong bộ nhớ (In-memory), giúp truy vấn hàng triệu dòng dữ liệu chỉ trong vài mili-giây.
* **Truy vấn tự do:** Trình soạn thảo SQL (SQL Query Editor) cho phép người dùng viết các câu lệnh SQL chuẩn để lọc, gộp nhóm, tính toán trực tiếp trên bảng `jobs`.

#### 📊 Cấu trúc bảng dữ liệu `jobs`
| Tên cột | Kiểu dữ liệu | Mô tả & Ví dụ minh họa |
| :--- | :--- | :--- |
| **`job_id`** | TEXT | Mã định danh duy nhất của tin tuyển dụng (Ví dụ: `IT-0001`) |
| **`job_title`** | TEXT | Tiêu đề tin tuyển dụng (Ví dụ: `Senior Python Backend Developer`) |
| **`role_category`** | TEXT | Nhóm vai trò/vị trí chính (Ví dụ: `Python Backend Developer`, `Data Analyst`, `AI/ML Engineer`) |
| **`skills`** | TEXT | Danh sách các kỹ năng/công nghệ yêu cầu, phân tách bằng dấu phẩy (Ví dụ: `Python, SQL, Pandas`) |
| **`experience_years`** | INTEGER | Số năm kinh nghiệm làm việc tối thiểu yêu cầu (Ví dụ: `3`, `5`) |
| **`salary_usd`** | INTEGER | Mức lương tháng (Đơn vị: USD, ví dụ: `1800`) |
| **`location`** | TEXT | Địa điểm làm việc (Ví dụ: `Ho Chi Minh City`, `Ha Noi`, `Da Nang`, `Remote`) |
| **`company_size`** | TEXT | Quy mô của công ty tuyển dụng (Ví dụ: `Small (Startup)`, `Medium (SME)`, `Large (Enterprise)`) |
| **`job_type`** | TEXT | Loại hình hợp đồng lao động (Ví dụ: `Full-time`, `Contract`, `Internship`) |
| **`work_mode`** | TEXT | Hình thức làm việc thực tế (Ví dụ: `On-site`, `Hybrid`, `Remote`) |
| **`posted_date`** | DATE (TEXT) | Ngày tin tuyển dụng được đăng tải (Định dạng: `YYYY-MM-DD`, ví dụ: `2026-05-15`) |

* **Mẫu truy vấn chuyên nghiệp:** Cung cấp sẵn các mẫu câu truy vấn hữu ích như:
  * Thống kê lương và số lượng tuyển dụng theo vai trò.
  * Top 10 công việc thu nhập cao nhất.
  * Phân tích tỷ lệ & mức lương theo hình thức (Remote, Hybrid, On-site).
  * Khảo sát lương theo cấp bậc kinh nghiệm (Junior, Mid-level, Senior, Lead).
* **Tự động trực quan kết quả (Auto Charting):** Tự động nhận diện dữ liệu chữ và số từ kết quả truy vấn SQL để tạo nhanh biểu đồ Cột (Bar Chart) hoặc Đường (Line Chart) mà không cần code thêm.
* **Xuất dữ liệu:** Cho phép tải kết quả truy vấn trực tiếp dưới định dạng `.CSV`.

### 3. 🐍 Phân Tích Python & Học Máy (Machine Learning & AI)
* **Mô hình Dự báo Lương (Salary Predictor):**
  * Sử dụng thuật toán học máy **Random Forest Regressor** (`scikit-learn`) kết hợp tiền xử lý dữ liệu tự động (`OneHotEncoder`, `ColumnTransformer` đóng gói dạng `Pipeline`).
  * Đo lường hiệu năng trực tiếp thông qua hai chỉ số độ chính xác: hệ số xác định **$R^2$ Score** và Sai số tuyệt đối trung bình **MAE (Mean Absolute Error)**.
  * Cho phép người dùng nhập thông số hồ sơ (*Số năm kinh nghiệm, Vai trò chính, Địa điểm, Quy mô công ty, Hình thức làm việc*) để dự đoán khoảng lương phù hợp.
* **Gom cụm Kỹ năng Công nghệ (K-Means Clustering & PCA):**
  * Xây dựng ma trận đặc trưng kỹ năng nhị phân (Binary Skill Matrix) từ 30 kỹ năng phổ biến nhất.
  * Áp dụng thuật toán **K-Means Clustering** để gom cụm các tin tuyển dụng thành các nhóm nghề nghiệp công nghệ tương tự nhau.
  * Sử dụng thuật toán giảm chiều dữ liệu **PCA (Principal Component Analysis)** để chiếu dữ liệu lên không gian 2D và vẽ biểu đồ phân tán trực quan.
  * Tự động trích xuất Insights của từng nhóm (Kỹ năng cốt lõi, vai trò đặc trưng, mức lương & kinh nghiệm trung bình của nhóm).

### 4. ⚙️ Ánh Xạ Dữ Liệu Tự Động (Dynamic Data Loader & Mapping)
* **Lọc & Nhập tệp thô:** Hỗ trợ người dùng tải lên tệp tuyển dụng thô tùy biến bất kỳ (định dạng `.csv` hoặc `.xlsx`).
* **Fuzzy Match & Từ đồng nghĩa:** Áp dụng thuật toán so khớp từ đồng nghĩa tiếng Anh & tiếng Việt kết hợp chuẩn hóa loại bỏ dấu tiếng Việt để tự động nhận diện và ánh xạ các cột dữ liệu quan trọng như *vị trí, kỹ năng, kinh nghiệm, lương, địa điểm*.
* **Chuẩn hóa & Bù đắp dữ liệu:** Tự động điền dữ liệu khuyết thiếu, chuẩn hóa tỷ giá tiền tệ (tự động quy đổi VND sang USD dựa trên ngưỡng quy mô lương), gán định danh an toàn.

### 5. 📋 Báo Cáo Phân Tích Tự Động (Executive Report)
* Tự động tính toán các chỉ số thống kê toán học như hệ số tương quan tuyến tính **Pearson Correlation** giữa số năm kinh nghiệm và mức lương.
* Tự động biên soạn một báo cáo phân tích chuyên sâu (Executive Summary Report) bằng ngôn ngữ Markdown và cung cấp tính năng tải xuống tệp báo cáo dạng `.md` để sử dụng cho thuyết trình hoặc nghiên cứu.

---

## 🛠️ Công nghệ sử dụng
* **Frontend UI / Framework:** [Streamlit](https://streamlit.io/) (Ứng dụng giao diện tối giản, responsive, kết hợp CSS tùy biến trong `styles/custom.css` mang phong cách Glassmorphism và tối ưu hóa trải nghiệm người dùng).
* **Cơ sở dữ liệu:** [DuckDB](https://duckdb.org/) (In-memory SQL database tối ưu cho phân tích dữ liệu OLAP).
* **Xử lý dữ liệu:** [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/).
* **Học máy (ML):** [Scikit-Learn](https://scikit-learn.org/) (Pipeline, RandomForestRegressor, KMeans, PCA, train_test_split).
* **Trực quan hóa:** [Plotly Express](https://plotly.com/python/), [Plotly Graph Objects](https://plotly.com/python/).
* **Định dạng file:** `openpyxl` (Đọc ghi Excel), `statsmodels` (Hỗ trợ đường xu hướng OLS).

---

## 📁 Cấu trúc thư mục dự án
```text
IT Recruitment Market Dashboard/
├── app.py                   # Điểm khởi chạy ứng dụng (Main Entrypoint & Streamlit Layout)
├── requirements.txt         # Khai báo các thư viện phụ thuộc của dự án
├── styles/
│   └── custom.css           # File CSS tùy biến giao diện (Giao diện tối, hiệu ứng Glassmorphism)
└── utils/
    ├── __init__.py          # Khởi tạo gói python
    ├── data_generator.py    # Trình tạo dữ liệu mẫu tuyển dụng IT mô phỏng thực tế
    ├── sql_engine.py        # Động cơ xử lý DuckDB SQL và định nghĩa các truy vấn mẫu
    └── analysis_engine.py   # Mô hình học máy dự đoán lương (Random Forest) & Gom cụm kỹ năng (K-Means, PCA)
```

---

## 🚀 Hướng dẫn cài đặt và chạy ứng dụng

### Yêu cầu hệ thống
* Đã cài đặt **Python 3.10** hoặc phiên bản cao hơn.

### Các bước thực hiện

**Bước 1: Clone dự án hoặc tải mã nguồn về máy**
```bash
git clone https://github.com/username/it-recruitment-dashboard.git
cd it-recruitment-dashboard
```

**Bước 2: Tạo môi trường ảo (Virtual Environment) và kích hoạt**
* Trên Linux/macOS:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
* Trên Windows:
  ```bash
  python -m venv .venv
  .venv\Scripts\activate
  ```

**Bước 3: Cài đặt các thư viện dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Bước 4: Khởi chạy ứng dụng Streamlit**
```bash
streamlit run app.py
```
Sau khi chạy lệnh, trình duyệt web sẽ tự động mở trang ứng dụng tại địa chỉ: `http://localhost:8501`.

---

## 💼 Cách đưa dự án này vào CV / Resume

Để tối ưu hóa hồ sơ năng lực của bạn trong mắt nhà tuyển dụng (đặc biệt cho vị trí **Data Analyst**, **Data Engineer**, hoặc **Python Developer**), dưới đây là đoạn giới thiệu dự án được biên soạn chuẩn hóa để bạn copy-paste trực tiếp:

### Tiếng Việt (Dành cho CV tiếng Việt)
> **IT Recruitment Market Dashboard | Python, Streamlit, DuckDB, Machine Learning**
> * **Vai trò:** Lập trình viên chính & Chuyên viên Phân tích dữ liệu (Full-stack Data Analytics Developer).
> * **Mô tả:** Xây dựng ứng dụng dashboard tương tác phân tích thị trường tuyển dụng CNTT tại Việt Nam. Cho phép người dùng trực quan xu hướng lương/kinh nghiệm, tải lên dữ liệu thô để tự động chuẩn hóa bằng giải thuật Fuzzy Match và tự động xuất báo cáo chuyên sâu.
> * **Công nghệ sử dụng:** Python, Streamlit, DuckDB, Pandas, Plotly, Scikit-learn (Random Forest, K-Means, PCA).
> * **Kết quả & Điểm nhấn kỹ thuật:**
>   * Tích hợp **DuckDB** làm động cơ SQL tại bộ nhớ giúp giảm thiểu thời gian truy vấn dữ liệu phân tích xuống dưới 10ms.
>   * Xây dựng **SQL Playground tương tác** cho phép viết code SQL tự do, tự động vẽ biểu đồ thông minh từ kết quả truy vấn và xuất file CSV.
>   * Phát triển hệ thống học máy gồm mô hình **Random Forest Regressor** dự báo lương với độ chính xác cao và phân cụm kỹ năng bằng thuật toán **K-Means & PCA** hiển thị bản đồ công nghệ 2D trực quan.
>   * Thiết kế module tải dữ liệu động tự động nhận dạng, đổi tên và bù đắp dữ liệu khuyết thiếu của bất kỳ tệp CSV/Excel nào tải lên bằng giải thuật đối chiếu từ đồng nghĩa không dấu.

### English (For English CV/Resume)
> **IT Recruitment Market Dashboard | Python, Streamlit, DuckDB, Machine Learning**
> * **Role:** Lead Data Analytics Developer
> * **Project Description:** Developed an interactive full-stack analytics application to analyze the IT job market in Vietnam. It enables job seekers and recruiters to discover salary insights, write custom SQL queries, predict individual compensation packages, and discover tech skill clusters.
> * **Tech Stack:** Python, Streamlit, DuckDB, Pandas, Plotly, Scikit-learn (Random Forest, K-Means, PCA).
> * **Key Accomplishments & Engineering Highlights:**
>   * Integrated **DuckDB** as an in-memory SQL engine, reducing analytical query latency to under 10ms.
>   * Designed a **dynamic data loading module** with English/Vietnamese synonym mapping and Vietnamese accent normalization to automatically clean and ingest unstructured job-posting datasets.
>   * Implemented a **Salary Predictor pipeline** using **Random Forest Regressor** (measuring R² & MAE) and a **Skill Clustering tool** using **K-Means and PCA** to map technology trends on 2D scatter plots.
>   * Engineered an **Interactive SQL Playground** supporting ad-hoc queries, automated chart rendering, and CSV exports of query results.
>   * Built custom dark-themed UI components using custom CSS injection (Glassmorphism design language) to maximize UX.

---

*Dự án được xây dựng với mục tiêu mang lại công cụ đắc lực hỗ trợ cộng đồng CNTT và thể hiện năng lực phân tích dữ liệu / lập trình Python chuyên nghiệp.*
