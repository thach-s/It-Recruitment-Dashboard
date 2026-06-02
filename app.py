import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime
from utils.data_generator import generate_it_recruitment_data
from utils.sql_engine import execute_sql_query, get_predefined_queries
from utils.analysis_engine import train_salary_predictor, predict_user_salary, perform_skill_clustering

# 1. Cấu hình trang Streamlit
st.set_page_config(
    page_title="IT Recruitment Market Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Nhúng CSS tùy biến
css_path = os.path.join(os.path.dirname(__file__), "styles", "custom.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        custom_css = f.read()
    st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)
else:
    st.warning("Không tìm thấy tệp CSS tùy biến. Sử dụng giao diện mặc định.")

# 3. Quản lý trạng thái Dữ liệu trong Session State
if "df" not in st.session_state:
    st.session_state.df = None
if "df_source_name" not in st.session_state:
    st.session_state.df_source_name = ""

# --- SIDEBAR: Quản lý tải và lọc dữ liệu ---
st.sidebar.markdown('<div class="brand-title" style="font-size: 1.8rem; text-align: center; margin-bottom: 20px;">📊 IT LABOUR INSIGHTS</div>', unsafe_allow_html=True)
st.sidebar.markdown("---")

# Tải tệp lên
st.sidebar.subheader("📂 Nhập dữ liệu phân tích")
uploaded_file = st.sidebar.file_uploader(
    "Tải lên tệp tuyển dụng (CSV hoặc Excel)",
    type=["csv", "xlsx"]
)

# Xử lý file tải lên
if uploaded_file is not None:
    if ("raw_df" not in st.session_state) or (st.session_state.get("raw_filename") != uploaded_file.name):
        try:
            if uploaded_file.name.endswith(".csv"):
                # Đọc tệp CSV với xử lý dữ liệu thô
                st.session_state.raw_df = pd.read_csv(uploaded_file)
            else:
                st.session_state.raw_df = pd.read_excel(uploaded_file)
            st.session_state.raw_filename = uploaded_file.name
            # Reset trạng thái phân tích của file cũ
            st.session_state.df = None 
        except Exception as e:
            st.sidebar.error(f"Lỗi đọc file: {e}")

# Nút dữ liệu mẫu
if st.sidebar.button("💡 Dùng Dữ liệu mẫu (1,000 tin tuyển IT)", width='stretch'):
    with st.spinner("Đang tạo dữ liệu mẫu tuyển dụng..."):
        st.session_state.df = generate_it_recruitment_data(n_samples=1000)
        st.session_state.df_source_name = "Dữ liệu mẫu tuyển dụng IT 2026 (1,000 dòng)"
        if "raw_df" in st.session_state:
            del st.session_state.raw_df
        st.sidebar.success("Đã nạp dữ liệu mẫu thành công!")
        st.rerun()

# Cấu hình ánh xạ cột nếu có tệp thô được tải lên
if "raw_df" in st.session_state:
    raw_df = st.session_state.raw_df
    columns = raw_df.columns.tolist()
    
    # Danh sách từ đồng nghĩa tiếng Anh & tiếng Việt để tự động nhận dạng
    synonyms = {
        "job_title": ["job_title", "title", "tên công việc", "tiêu đề", "vị trí", "chức danh", "jobtitle", "job_name", "job name", "tên vị trí"],
        "skills": ["skills", "skill", "kỹ năng", "công nghệ", "yêu cầu công nghệ", "yêu cầu kỹ năng", "technologies", "tech_stack", "tech stack", "skills_list"],
        "experience_years": ["experience_years", "experience", "exp", "kinh nghiệm", "năm kinh nghiệm", "yêu cầu kinh nghiệm", "years_of_experience", "yoe", "số năm kinh nghiệm"],
        "salary_usd": ["salary_usd", "salary", "lương", "mức lương", "thu nhập", "lương usd", "salary usd", "salary_in_usd", "lương_usd"],
        "location": ["location", "địa điểm", "nơi làm việc", "tỉnh thành", "thành phố", "city", "work_location", "work location"]
    }
    
    # Chuẩn hóa chuỗi so khớp không dấu
    import re
    def clean_str(s):
        s = str(s).lower().strip()
        s = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
        s = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', s)
        s = re.sub(r'[ìíịỉĩ]', 'i', s)
        s = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
        s = re.sub(r'[ùúụủũưừứựửữ]', 'u', s)
        s = re.sub(r'[ỳýỵỷỹ]', 'y', s)
        s = re.sub(r'[đ]', 'd', s)
        s = re.sub(r'[^a-z0-9_ ]', '', s)
        return s
        
    # Dự đoán ánh xạ tự động các cột
    auto_mappings = {}
    for standard_col, syn_list in synonyms.items():
        cleaned_syns = [clean_str(syn) for syn in syn_list]
        for col in columns:
            cleaned_col = clean_str(col)
            if cleaned_col in cleaned_syns or any(syn in cleaned_col for syn in cleaned_syns if len(syn) > 3):
                auto_mappings[standard_col] = col
                break
                
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Cấu hình cột dữ liệu")
    
    mapped_cols = {}
    with st.sidebar.expander("🛠️ Thiết lập ánh xạ cột", expanded=True):
        st.info("Hãy xác định các cột tương ứng trong file của bạn:")
        
        # 1. Tiêu đề công việc
        default_idx = columns.index(auto_mappings["job_title"]) if "job_title" in auto_mappings else 0
        mapped_cols["job_title"] = st.selectbox("Tiêu đề công việc:", options=columns, index=default_idx)
        
        # 2. Kỹ năng
        default_idx = columns.index(auto_mappings["skills"]) if "skills" in auto_mappings else 0
        mapped_cols["skills"] = st.selectbox("Kỹ năng yêu cầu:", options=columns, index=default_idx)
        
        # 3. Kinh nghiệm
        default_idx = columns.index(auto_mappings["experience_years"]) if "experience_years" in auto_mappings else 0
        mapped_cols["experience_years"] = st.selectbox("Năm kinh nghiệm:", options=columns, index=default_idx)
        
        # 4. Lương
        default_idx = columns.index(auto_mappings["salary_usd"]) if "salary_usd" in auto_mappings else 0
        mapped_cols["salary_usd"] = st.selectbox("Mức lương:", options=columns, index=default_idx)
        
        # 5. Địa điểm
        default_idx = columns.index(auto_mappings["location"]) if "location" in auto_mappings else 0
        mapped_cols["location"] = st.selectbox("Địa điểm làm việc:", options=columns, index=default_idx)
        
    if st.sidebar.button("💾 Xác nhận & Chạy Phân Tích", width='stretch'):
        with st.spinner("Đang chuẩn hóa và làm sạch dữ liệu tệp..."):
            try:
                processed_df = raw_df.copy()
                
                # Áp dụng ánh xạ đổi tên cột
                rename_dict = {v: k for k, v in mapped_cols.items()}
                processed_df = processed_df.rename(columns=rename_dict)
                
                # Bù đắp tự động các cột không bắt buộc nếu thiếu
                if "company_size" not in processed_df.columns:
                    processed_df["company_size"] = "Medium (SME)"
                if "job_type" not in processed_df.columns:
                    processed_df["job_type"] = "Full-time"
                if "work_mode" not in processed_df.columns:
                    processed_df["work_mode"] = processed_df["location"].apply(
                        lambda x: "Remote" if "remote" in str(x).lower() else "On-site"
                    )
                if "posted_date" not in processed_df.columns:
                    processed_df["posted_date"] = datetime.now().strftime("%Y-%m-%d")
                if "role_category" not in processed_df.columns:
                    # Trích xuất vai trò đầu tiên của Job Title làm vai trò chính
                    processed_df["role_category"] = processed_df["job_title"].apply(
                        lambda x: str(x).split(" ")[0] if len(str(x).split(" ")) > 1 else "Other IT"
                    )
                if "job_id" not in processed_df.columns:
                    processed_df["job_id"] = [f"IT-{i+1:04d}" for i in range(len(processed_df))]
                    
                # Ép kiểu dữ liệu an toàn (Kinh nghiệm)
                processed_df["experience_years"] = pd.to_numeric(processed_df["experience_years"], errors="coerce").fillna(0).astype(int)
                
                # Làm sạch và chuẩn hóa Lương (Hỗ trợ tự động đổi VNĐ sang USD nếu cần)
                def clean_salary(val):
                    try:
                        if pd.isna(val):
                            return 1000
                        val_str = re.sub(r'[^\d]', '', str(val))
                        if not val_str:
                            return 1000
                        val_num = int(val_str)
                        # Nếu mức lương lớn hơn 500,000 thì phỏng đoán là tiền Việt (VNĐ), chia 25,400 để ra USD
                        if val_num > 500000:
                            return int(val_num / 25400)
                        return val_num
                    except:
                        return 1000
                        
                processed_df["salary_usd"] = processed_df["salary_usd"].apply(clean_salary)
                
                # Điền giá trị rỗng cho Kỹ năng và Địa điểm
                processed_df["skills"] = processed_df["skills"].fillna("General IT").astype(str)
                processed_df["location"] = processed_df["location"].fillna("Remote").astype(str)
                
                # Trích xuất các cột chuẩn
                final_cols = [
                    "job_id", "job_title", "role_category", "skills", "experience_years",
                    "salary_usd", "location", "company_size", "job_type", "work_mode", "posted_date"
                ]
                
                st.session_state.df = processed_df[final_cols]
                st.session_state.df_source_name = st.session_state.raw_filename
                st.sidebar.success("✔️ Chuẩn hóa dữ liệu thành công!")
                st.rerun()
            except Exception as ex:
                st.sidebar.error(f"Lỗi chuẩn hóa dữ liệu: {ex}")

# Nếu chưa có dữ liệu, hiển thị thông báo hướng dẫn
if st.session_state.df is None:
    if "raw_df" in st.session_state:
        st.markdown(f"""
        <div class="glass-container" style="text-align: center; margin-top: 50px;">
            <h2 style="margin-bottom: 15px;">⚙️ Thiết lập cấu trúc cột tệp "{st.session_state.raw_filename}"</h2>
            <p style="color: #9aa0b9; font-size: 1.1rem; max-width: 700px; margin: 0 auto 25px auto;">
                Chúng tôi đã đọc thành công tệp dữ liệu của bạn ({len(st.session_state.raw_df):,} dòng). <br><br>
                Vui lòng kiểm tra và thiết lập ánh xạ các cột dữ liệu ở <b>menu bên trái (Sidebar)</b>, sau đó nhấn nút <b>"Xác nhận & Chạy Phân Tích"</b> để bắt đầu hiển thị Dashboard.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="glass-container" style="text-align: center; margin-top: 50px;">
            <h2 style="margin-bottom: 15px;">👋 Chào mừng đến với Dashboard Phân tích Thị trường IT</h2>
            <p style="color: #9aa0b9; font-size: 1.1rem; max-width: 700px; margin: 0 auto 25px auto;">
                Hệ thống phân tích dữ liệu tuyển dụng lao động IT nâng cao. Vui lòng tải lên tệp dữ liệu tuyển dụng 
                (CSV/Excel) ở menu bên trái hoặc bấm vào nút <b>"Dùng Dữ liệu mẫu"</b> để trải nghiệm ngay lập tức.
            </p>
            <div style="display: inline-block; padding: 10px 20px; border-radius: 8px; background: rgba(0, 242, 254, 0.05); border: 1px dashed rgba(0, 242, 254, 0.3);">
                💡 <b>Tính năng nổi bật:</b> Phân tích thống kê quan trọng, Truy vấn SQL thời gian thực (DuckDB), Học máy dự báo lương & Gom cụm kỹ năng, Xuất báo cáo tự động.
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# Dữ liệu gốc
df_original = st.session_state.df.copy()

# Bộ lọc Sidebar (Chỉ áp dụng cho Tab 1 & Tab 4 để giữ nguyên dữ liệu cho SQL/Python Code)
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Bộ lọc trực quan (Tab Tổng quan)")

# Bộ lọc địa điểm
available_locations = df_original["location"].unique().tolist()
selected_locations = st.sidebar.multiselect(
    "Địa điểm làm việc:",
    options=available_locations,
    default=available_locations
)

# Bộ lọc kinh nghiệm
if len(df_original) > 0:
    min_exp = int(df_original["experience_years"].min())
    max_exp = int(df_original["experience_years"].max())
else:
    min_exp = 0
    max_exp = 1

# Đảm bảo min_value luôn nhỏ hơn max_value để tránh crash Streamlit
if min_exp == max_exp:
    max_exp = min_exp + 1

selected_exp_range = st.sidebar.slider(
    "Năm kinh nghiệm yêu cầu:",
    min_value=min_exp,
    max_value=max_exp,
    value=(min_exp, max_exp)
)

# Bộ lọc vai trò chính
available_roles = df_original["role_category"].unique().tolist()
selected_roles = st.sidebar.multiselect(
    "Vai trò tuyển dụng:",
    options=available_roles,
    default=available_roles
)

# Áp dụng bộ lọc cho dữ liệu hiển thị tổng quan
df_filtered = df_original[
    (df_original["location"].isin(selected_locations)) &
    (df_original["experience_years"].between(selected_exp_range[0], selected_exp_range[1])) &
    (df_original["role_category"].isin(selected_roles))
]

# Hiển thị thông tin file đang phân tích
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style="font-size: 0.85rem; color: #9aa0b9;">
    <b>Tệp đang xử lý:</b><br>{st.session_state.df_source_name}<br>
    <b>Số dòng:</b> {len(df_original)} tin tuyển dụng<br>
    <b>Đã lọc:</b> {len(df_filtered)} tin tuyển dụng
</div>
""", unsafe_allow_html=True)


# --- TIÊU ĐỀ TRANG CHÍNH ---
st.markdown('<div class="brand-title" style="font-size: 2.8rem; margin-bottom: 5px;">📊 THỊ TRƯỜNG LAO ĐỘNG IT VIỆT NAM</div>', unsafe_allow_html=True)
st.markdown(f'<div style="color: #9aa0b9; font-size: 1.1rem; margin-bottom: 25px;">Phân tích chuyên sâu từ Data Analyst | Nguồn: <span class="glow-badge">{st.session_state.df_source_name}</span></div>', unsafe_allow_html=True)

# Khởi tạo các Tab chính
tab_overview, tab_sql, tab_python, tab_report = st.tabs([
    "📈 Tổng Quan Thị Trường", 
    "🗃️ SQL Playground", 
    "🐍 Phân Tích Python & AI", 
    "📋 Báo Cáo Phân Tích"
])

# ==========================================
# TAB 1: TỔNG QUAN THỊ TRƯỜNG
# ==========================================
with tab_overview:
    if len(df_filtered) == 0:
        st.warning("Không có dữ liệu phù hợp với bộ lọc hiện tại. Vui lòng điều chỉnh lại bộ lọc ở Sidebar.")
    else:
        # Tính toán các chỉ số KPI
        total_jobs = len(df_filtered)
        avg_salary = df_filtered["salary_usd"].mean()
        
        # Tìm kỹ năng hot nhất
        all_skills = df_filtered["skills"].str.split(", ").explode().str.strip()
        top_skill = all_skills.value_counts().index[0] if not all_skills.empty else "N/A"
        top_skill_count = all_skills.value_counts().values[0] if not all_skills.empty else 0
        
        # Tỷ lệ việc làm Remote
        remote_jobs = len(df_filtered[df_filtered["work_mode"] == "Remote"])
        remote_ratio = (remote_jobs / total_jobs) * 100 if total_jobs > 0 else 0
        
        # Render Metric Cards bằng HTML/CSS tùy biến
        st.markdown(f"""
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-title">Tổng số việc làm (Lọc)</div>
                <div class="metric-value">{total_jobs:,}</div>
                <div class="metric-sub neutral">Từ tổng số {len(df_original):,} tin gốc</div>
            </div>
            <div class="metric-card green">
                <div class="metric-title">Lương trung bình</div>
                <div class="metric-value">${avg_salary:,.0f}</div>
                <div class="metric-sub up">▲ USD / Tháng</div>
            </div>
            <div class="metric-card purple">
                <div class="metric-title">Kỹ năng săn đón nhất</div>
                <div class="metric-value" style="font-size: 1.8rem; margin-top: 5px;">{top_skill}</div>
                <div class="metric-sub neutral">Xuất hiện trong {top_skill_count} tin tuyển</div>
            </div>
            <div class="metric-card gold">
                <div class="metric-title">Tỷ lệ Remote</div>
                <div class="metric-value">{remote_ratio:.1f}%</div>
                <div class="metric-sub neutral">Có {remote_jobs} vị trí làm từ xa</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Grid biểu đồ hàng 1
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            st.subheader("💵 Tương quan Lương theo Kinh nghiệm & Vai trò")
            # Vẽ biểu đồ Scatter lương vs kinh nghiệm
            fig_scatter = px.scatter(
                df_filtered,
                x="experience_years",
                y="salary_usd",
                color="role_category",
                hover_data=["job_title", "location"],
                labels={"experience_years": "Kinh nghiệm (Năm)", "salary_usd": "Mức lương (USD)", "role_category": "Vị trí"},
                opacity=0.7,
                trendline="ols",
                trendline_scope="overall"
            )
            fig_scatter.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_family="Outfit",
                margin=dict(l=40, r=40, t=20, b=40),
                height=400
            )
            fig_scatter.update_traces(marker=dict(size=8, line=dict(width=1, color='DarkSlateGrey')))
            st.plotly_chart(fig_scatter, width='stretch')
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            st.subheader("🔥 Top 15 Kỹ năng được Yêu cầu Nhiều nhất")
            # Đếm kỹ năng và vẽ biểu đồ thanh ngang
            skill_counts = all_skills.value_counts().head(15).reset_index()
            skill_counts.columns = ["Kỹ năng", "Số lượng tuyển dụng"]
            
            fig_bar = px.bar(
                skill_counts,
                x="Số lượng tuyển dụng",
                y="Kỹ năng",
                orientation="h",
                color="Số lượng tuyển dụng",
                color_continuous_scale="Viridis",
                labels={"Số lượng tuyển dụng": "Số lượng tin đăng", "Kỹ năng": "Công nghệ/Kỹ năng"}
            )
            fig_bar.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_family="Outfit",
                margin=dict(l=40, r=40, t=20, b=40),
                height=400,
                coloraxis_showscale=False
            )
            fig_bar.update_yaxes(categoryorder="total ascending")
            st.plotly_chart(fig_bar, width='stretch')
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Grid biểu đồ hàng 2
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            st.subheader("📍 Phân bổ Nhu cầu tuyển dụng theo Địa điểm")
            
            fig_pie = px.pie(
                df_filtered,
                names="location",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_family="Outfit",
                margin=dict(l=20, r=20, t=20, b=20),
                height=350
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, width='stretch')
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col4:
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            st.subheader("🏢 Phân bổ Quy mô doanh nghiệp tuyển dụng")
            
            fig_comp = px.histogram(
                df_filtered,
                x="company_size",
                color="work_mode",
                barmode="group",
                labels={"company_size": "Quy mô công ty", "count": "Số lượng", "work_mode": "Hình thức"},
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_comp.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_family="Outfit",
                margin=dict(l=40, r=40, t=20, b=40),
                height=350,
                yaxis_title="Số lượng tuyển dụng"
            )
            st.plotly_chart(fig_comp, width='stretch')
            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 2: SQL PLAYGROUND TƯƠNG TÁC
# ==========================================
with tab_sql:
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    st.subheader("⌨️ SQL Playground - Thực thi truy vấn thời gian thực")
    st.markdown("""
    Viết câu lệnh SQL của bạn để truy vấn trực tiếp trên toàn bộ bảng dữ liệu. Bảng dữ liệu chính được đặt tên là `jobs`.
    Bạn có thể sử dụng cú pháp SQL chuẩn của **DuckDB** để xử lý chuỗi, thời gian, và tính toán nâng cao.
    """)
    
    with st.expander("📋 Xem cấu trúc bảng dữ liệu 'jobs' (Columns Schema)"):
        st.markdown("""
        Bảng dữ liệu chính có tên là **`jobs`**. Các cột khả dụng gồm:
        
        | Tên Cột | Kiểu Dữ Liệu | Ví dụ minh họa |
        | :--- | :--- | :--- |
        | **`job_id`** | TEXT | Mã định danh công việc (Ví dụ: `IT-0001`) |
        | **`job_title`** | TEXT | Tiêu đề công việc (Ví dụ: `Senior Python Backend Developer`) |
        | **`role_category`** | TEXT | Vai trò chính (Ví dụ: `Python Backend Developer`, `Data Analyst`, `AI/ML Engineer`) |
        | **`skills`** | TEXT | Tổ hợp kỹ năng (Ví dụ: `Python, SQL, Power BI, Excel`) |
        | **`experience_years`** | INTEGER | Số năm kinh nghiệm tối thiểu yêu cầu (Ví dụ: `3`, `5`) |
        | **`salary_usd`** | INTEGER | Mức lương tháng (Đơn vị: USD, ví dụ: `1500`) |
        | **`location`** | TEXT | Địa điểm (Ví dụ: `Ho Chi Minh City`, `Ha Noi`, `Da Nang`, `Remote`) |
        | **`company_size`** | TEXT | Quy mô doanh nghiệp (Ví dụ: `Small (Startup)`, `Medium (SME)`, `Large (Enterprise)`) |
        | **`job_type`** | TEXT | Loại hợp đồng (Ví dụ: `Full-time`, `Contract`, `Internship`) |
        | **`work_mode`** | TEXT | Hình thức làm việc (Ví dụ: `On-site`, `Hybrid`, `Remote`) |
        | **`posted_date`** | DATE / TEXT | Ngày đăng tuyển dụng (Định dạng: `YYYY-MM-DD`, ví dụ: `2026-05-15`) |
        """)
    
    # Dropdown các câu truy vấn mẫu
    predefined_queries = get_predefined_queries()
    query_names = [q["name"] for q in predefined_queries]
    selected_query_name = st.selectbox(
        "💡 Chọn câu truy vấn SQL phân tích mẫu (Chạy nhanh):",
        options=query_names
    )
    
    # Tìm kiếm câu truy vấn tương ứng
    query_val = ""
    for pq in predefined_queries:
        if pq["name"] == selected_query_name:
            query_val = pq["query"]
            break
            
    # Quản lý văn bản truy vấn trong session state
    if "sql_editor_val" not in st.session_state or st.session_state.get("prev_query_name") != selected_query_name:
        st.session_state.sql_editor_val = query_val
        st.session_state.prev_query_name = selected_query_name
        
    # Textarea cho biên tập SQL
    sql_query = st.text_area(
        "SQL Query Editor", 
        value=st.session_state.sql_editor_val, 
        height=180,
        help="Viết câu lệnh SQL ở đây và nhấn 'Chạy truy vấn SQL'"
    )
    
    # Cập nhật giá trị vào session state khi thay đổi thủ công
    st.session_state.sql_editor_val = sql_query
    
    # Nút bấm chạy
    if st.button("🚀 Chạy truy vấn SQL"):
        with st.spinner("Đang truy vấn DuckDB..."):
            result_df, error_msg = execute_sql_query(df_original, sql_query)
            
            if error_msg:
                st.error(f"❌ Lỗi cú pháp SQL:\n{error_msg}")
            else:
                st.success(f"✔️ Thực thi thành công! Trả về {len(result_df)} dòng kết quả.")
                
                # Hiển thị bảng dữ liệu kết quả đẹp mắt
                st.dataframe(result_df, width='stretch')
                
                # Tải xuống kết quả dạng CSV
                csv_data = result_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Tải kết quả truy vấn (.CSV)",
                    data=csv_data,
                    file_name="sql_query_result.csv",
                    mime="text/csv",
                    width='stretch'
                )
                
                # Vẽ biểu đồ nhanh từ kết quả nếu có >= 2 cột
                if len(result_df) > 0 and len(result_df.columns) >= 2:
                    st.write("---")
                    st.subheader("📊 Trực quan hóa tự động kết quả SQL")
                    
                    # Xác định cột phân loại và cột số
                    cols = result_df.columns.tolist()
                    numeric_cols = result_df.select_dtypes(include=[np.number]).columns.tolist()
                    categorical_cols = [c for c in cols if c not in numeric_cols]
                    
                    if numeric_cols and categorical_cols:
                        x_axis = st.selectbox("Chọn trục X (Phân loại):", options=categorical_cols, key="sql_x")
                        y_axis = st.selectbox("Chọn trục Y (Số liệu):", options=numeric_cols, key="sql_y")
                        chart_type = st.radio("Chọn dạng biểu đồ:", ["Cột (Bar Chart)", "Đường (Line Chart)"], horizontal=True)
                        
                        if chart_type == "Cột (Bar Chart)":
                            fig_sql = px.bar(result_df, x=x_axis, y=y_axis, color=y_axis, color_continuous_scale="Tealgrn")
                        else:
                            fig_sql = px.line(result_df, x=x_axis, y=y_axis, markers=True)
                            
                        fig_sql.update_layout(
                            template="plotly_dark",
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            font_family="Outfit",
                            height=350
                        )
                        st.plotly_chart(fig_sql, width='stretch')
                    else:
                        st.info("💡 Kết quả truy vấn cần có ít nhất 1 cột phân loại (chữ) và 1 cột số để tự động vẽ biểu đồ.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 3: PHÂN TÍCH PYTHON & MACHINE LEARNING
# ==========================================
with tab_python:
    # Chia làm 2 phần phân tích lớn
    subtab_predictor, subtab_clustering = st.tabs([
        "🧠 Mô hình Dự Báo Lương (ML Regressor)", 
        "🧩 Phân tích Gom Cụm Kỹ Năng (K-Means)"
    ])
    
    # 3.1. Mô hình Dự Báo Lương
    with subtab_predictor:
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        st.subheader("🤖 Huấn luyện mô hình Học máy dự báo mức lương IT")
        st.markdown("""
        Tại đây, chúng tôi sử dụng mô hình học máy **Random Forest Regressor** của thư viện `scikit-learn` trong Python 
        để học hỏi các yếu tố quyết định đến mức lương gồm: *Số năm kinh nghiệm, Địa điểm làm việc, Vai trò chính, Quy mô công ty, và Hình thức làm việc*.
        """)
        
        # Tiến hành huấn luyện mô hình
        with st.spinner("Đang huấn luyện mô hình Random Forest trên dữ liệu tuyển dụng..."):
            pipeline_model, r2, mae = train_salary_predictor(df_original)
            
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric(label="R² Score (Độ chính xác mô hình)", value=f"{r2:.2%}", delta="Tốt" if r2 > 0.6 else "Khá")
        with col_m2:
            st.metric(label="Sai số trung bình (MAE)", value=f"${mae:,.0f} USD", delta="Thấp (Sai lệch ít)", delta_color="inverse")
            
        st.markdown("---")
        st.subheader("🎯 Dự đoán lương của bạn")
        
        # Các widget nhập thông số của người dùng để dự đoán
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            input_exp = st.slider("Số năm kinh nghiệm làm việc:", min_value=0, max_value=15, value=3, step=1)
            input_loc = st.selectbox("Địa điểm làm việc:", options=df_original["location"].unique().tolist())
        with col_p2:
            input_role = st.selectbox("Vai trò/Vị trí chính:", options=df_original["role_category"].unique().tolist())
            input_size = st.selectbox("Quy mô công ty:", options=df_original["company_size"].unique().tolist())
        with col_p3:
            input_mode = st.selectbox("Hình thức làm việc:", options=df_original["work_mode"].unique().tolist())
            
        if st.button("💰 Tính toán Dự báo Mức lương", width='stretch'):
            predicted_val = predict_user_salary(
                pipeline_model,
                experience_years=input_exp,
                location=input_loc,
                role_category=input_role,
                company_size=input_size,
                work_mode=input_mode
            )
            
            st.markdown(f"""
            <div style="text-align: center; padding: 25px; background: rgba(0, 242, 254, 0.08); border-radius: 12px; border: 1px solid rgba(0, 242, 254, 0.3); margin-top: 15px;">
                <span style="font-size: 1.1rem; color: #9aa0b9; text-transform: uppercase;">Mức lương dự báo phù hợp với bạn:</span>
                <h2 style="color: #00f2fe; font-size: 3rem; margin: 10px 0 5px 0; font-family: 'Space Grotesk', sans-serif;">${predicted_val:,.0f} USD / Tháng</h2>
                <p style="color: #d1d5db; margin-bottom: 0;">Khoảng lương dao động thực tế: <b>${(predicted_val - mae):,.0f}</b> - <b>${(predicted_val + mae):,.0f} USD</b></p>
            </div>
            """, unsafe_allow_html=True)
            
        # Hiển thị Code Python dùng để huấn luyện
        with st.expander("👁️ Xem mã nguồn Python huấn luyện mô hình"):
            st.code("""
# Mã nguồn Python thực hiện phân tích và huấn luyện Random Forest
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error

# 1. Định nghĩa đặc trưng đầu vào và nhãn đầu ra
features = ["experience_years", "location", "role_category", "company_size", "work_mode"]
X = df[features]
y = df["salary_usd"]

# 2. Phân tách tập huấn luyện và tập kiểm định
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Tiền xử lý dữ liệu phân loại (One-Hot Encoding)
preprocessor = ColumnTransformer(
    transformers=[
        ("num", "passthrough", ["experience_years"]),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), 
         ["location", "role_category", "company_size", "work_mode"])
    ]
)

# 4. Tạo Pipeline kết hợp tiền xử lý và mô hình Random Forest Regressor
pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("regressor", RandomForestRegressor(n_estimators=50, max_depth=8, random_state=42))
])

# 5. Huấn luyện mô hình và đánh giá
pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)
print(f"R2 Score: {r2_score(y_test, y_pred):.2f}")
print(f"MAE: ${mean_absolute_error(y_test, y_pred):.1f}")
            """, language="python")
        st.markdown('</div>', unsafe_allow_html=True)
        
    # 3.2. Phân tích Gom Cụm Kỹ Năng
    with subtab_clustering:
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        st.subheader("🧩 K-Means Clustering: Phân nhóm tin tuyển dụng dựa trên tổ hợp Kỹ năng")
        st.markdown("""
        Bằng cách áp dụng thuật toán gom cụm **K-Means** trên ma trận kỹ năng nhị phân và giảm chiều dữ liệu xuống không gian 2D 
        thông qua phân tích thành phần chính **PCA**, chúng ta có thể nhận biết cấu trúc phân bổ các nhóm kỹ năng và vai trò chính trong thị trường lao động.
        """)
        
        n_clusters_input = st.slider("Số lượng nhóm cần gom cụm (K-Means):", min_value=2, max_value=6, value=4)
        
        with st.spinner("Đang xử lý ma trận kỹ năng & chạy thuật toán K-Means..."):
            plot_df, insights = perform_skill_clustering(df_original, n_clusters=n_clusters_input)
            
        # Vẽ biểu đồ 2D PCA Scatter plot
        fig_clusters = px.scatter(
            plot_df,
            x="x",
            y="y",
            color="cluster",
            hover_data=["job_title", "role_category", "skills", "salary_usd"],
            title="Bản đồ Phân cụm Kỹ năng IT (Trực quan hóa PCA 2D)",
            labels={"cluster": "Nhóm phân cụm", "x": "Thành phần PCA 1", "y": "Thành phần PCA 2"}
        )
        fig_clusters.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_family="Outfit",
            height=450
        )
        st.plotly_chart(fig_clusters, width='stretch')
        
        # Hiển thị phân tích Insights cho mỗi nhóm
        st.markdown("### 💡 Thông tin chi tiết các Nhóm Phân Cụm")
        col_c = st.columns(len(insights))
        for idx, ins in enumerate(insights):
            with col_c[idx]:
                st.markdown(f"""
                <div style="background: rgba(18, 26, 56, 0.8); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 15px; height: 100%;">
                    <h4 style="color: #00f2fe; margin-top: 0;">📍 {ins['cluster_name']}</h4>
                    <p style="font-size: 0.85rem; color: #9aa0b9; margin-bottom: 8px;">Số lượng: <b>{ins['count']} tin tuyển dụng</b></p>
                    <p style="font-size: 0.9rem; margin-bottom: 8px;"><b>Kỹ năng cốt lõi:</b><br>{", ".join(ins['top_skills'])}</p>
                    <p style="font-size: 0.9rem; margin-bottom: 8px;"><b>Vai trò chính:</b><br>{ins['representative_roles']}</p>
                    <p style="font-size: 0.9rem; margin-bottom: 0; color: #00decb;"><b>Lương TB:</b> ${ins['avg_salary']:,.0f}</p>
                    <p style="font-size: 0.9rem; margin-bottom: 0; color: #ffa751;"><b>Kinh nghiệm TB:</b> {ins['avg_exp']:.1f} Năm</p>
                </div>
                """, unsafe_allow_html=True)
                
        # Hiển thị Code Python thực thi clustering
        with st.expander("👁️ Xem mã nguồn Python gom cụm"):
            st.code("""
# Trích xuất 30 kỹ năng phổ biến nhất làm đặc trưng
all_skills = df['skills'].str.split(', ').explode().str.strip()
top_skills = all_skills.value_counts().head(30).index.tolist()

# Xây dựng ma trận nhị phân kỹ năng cho mỗi bản ghi tuyển dụng
import numpy as np
skill_matrix = np.zeros((len(df), len(top_skills)))
for idx, skills_str in enumerate(df['skills']):
    job_skills = [s.strip() for s in skills_str.split(',')]
    for s_idx, skill in enumerate(top_skills):
        if skill in job_skills:
            skill_matrix[idx, s_idx] = 1

# Áp dụng thuật toán K-Means để gom thành các nhóm nghề nghiệp
from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df['cluster'] = kmeans.fit_predict(skill_matrix)

# Giảm chiều dữ liệu xuống 2 chiều bằng PCA để trực quan hóa
from sklearn.decomposition import PCA
pca = PCA(n_components=2, random_state=42)
pca_result = pca.fit_transform(skill_matrix)
df['x'] = pca_result[:, 0]
df['y'] = pca_result[:, 1]
            """, language="python")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 4: BÁO CÁO PHÂN TÍCH TỰ ĐỘNG
# ==========================================
with tab_report:
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    st.subheader("📋 Báo cáo Thị trường lao động IT tự động (Executive Summary)")
    st.markdown("Báo cáo này được lập trình tự động dựa trên tập dữ liệu tuyển dụng đang hoạt động:")
    
    # Tính toán thông số cho báo cáo
    tot_count = len(df_filtered)
    all_s = df_filtered["skills"].str.split(", ").explode().str.strip()
    top_5_skills = all_s.value_counts().head(5).index.tolist()
    
    # Nhóm lương cao nhất theo Role
    role_salaries = df_filtered.groupby("role_category")["salary_usd"].mean().sort_values(ascending=False)
    highest_role = role_salaries.index[0]
    highest_sal = role_salaries.values[0]
    lowest_role = role_salaries.index[-1]
    lowest_sal = role_salaries.values[-1]
    
    # Tỷ lệ HCMC/HaNoi
    loc_counts = df_filtered["location"].value_counts()
    hcmc_ratio = (loc_counts.get("Ho Chi Minh City", 0) / tot_count) * 100 if tot_count > 0 else 0
    hanoi_ratio = (loc_counts.get("Ha Noi", 0) / tot_count) * 100 if tot_count > 0 else 0
    
    # Tính tương quan hệ số Pearson giữa EXP và SALARY
    correlation = df_filtered["experience_years"].corr(df_filtered["salary_usd"])
    
    # Tạo nội dung báo cáo bằng Markdown
    report_markdown = f"""# BÁO CÁO PHÂN TÍCH THỊ TRƯỜNG LAO ĐỘNG IT
*Ngày tạo báo cáo: {datetime.now().strftime("%d-%m-%Y")} | Người tạo: AI Data Analyst System*
*Nguồn dữ liệu đang xử lý: {st.session_state.df_source_name}*

---

## 1. Tổng Quan Thị Trường Lao Động IT
Dựa trên phân tích từ **{tot_count:,} tin tuyển dụng** phù hợp với bộ lọc hiện tại trên hệ thống, thị trường lao động IT đang thể hiện các chỉ số sức khỏe quan trọng như sau:
* **Mức lương trung bình thị trường:** **${avg_salary:,.0f} USD/tháng** (tương đương khoảng {avg_salary * 25400:,.0f} VND/tháng).
* **Hình thức làm việc linh hoạt (Remote):** Chiếm **{remote_ratio:.1f}%** tổng số lượng việc làm. Đây là tín hiệu rõ ràng cho thấy mô hình làm việc từ xa tiếp tục giữ vị thế tốt sau đại dịch đối với khối ngành công nghệ thông tin.

## 2. Kỹ Năng Công Nghệ & Nhu Cầu Tuyển Dụng
Nhóm kỹ năng có tần suất yêu cầu cao nhất phản ánh xu hướng công nghệ hiện nay. Top 5 kỹ năng được các nhà tuyển dụng yêu cầu nhiều nhất gồm:
1. **{top_5_skills[0] if len(top_5_skills) > 0 else 'N/A'}**
2. **{top_5_skills[1] if len(top_5_skills) > 1 else 'N/A'}**
3. **{top_5_skills[2] if len(top_5_skills) > 2 else 'N/A'}**
4. **{top_5_skills[3] if len(top_5_skills) > 3 else 'N/A'}**
5. **{top_5_skills[4] if len(top_5_skills) > 4 else 'N/A'}**

Sự thống trị của các kỹ năng này cho thấy nhà tuyển dụng tập trung tuyển lựa nhân tài có nền tảng vững vàng trong phát triển ứng dụng web hiện đại và cấu trúc cơ sở dữ liệu.

## 3. Phân Tích Cơ Cấu Lương Theo Vị Trí & Số Năm Kinh Nghiệm
* **Vai trò thu nhập cao nhất:** **{highest_role}** dẫn đầu thị trường với mức lương trung bình **${highest_sal:,.0f} USD/tháng**, theo sau là các vai trò thuộc nhóm thiết kế kiến trúc hệ thống và AI/ML.
* **Vai trò thu nhập thấp nhất:** **{lowest_role}** với mức lương trung bình **${lowest_sal:,.0f} USD/tháng**, thường dành cho các vị trí yêu cầu ít năm kinh nghiệm chuyên sâu hơn như vận hành kiểm thử (QA/QC) hoặc lập trình viên tập sự.
* **Mối tương quan giữa Kinh nghiệm & Lương:** Hệ số tương quan Pearson đo được là **r = {correlation:.2f}**. Điều này chứng minh mối tương quan thuận mạnh mẽ: Số năm kinh nghiệm tích lũy càng tăng, mức lương của nhân sự IT có xu hướng tăng rõ rệt và tuyến tính.

## 4. Phân Bổ Địa Lý Tuyển Dụng
Thị trường lao động IT Việt Nam tập trung cao độ tại hai thành phố lớn:
* **Thành phố Hồ Chí Minh:** Chiếm **{hcmc_ratio:.1f}%** nhu cầu tuyển dụng trong tệp dữ liệu. HCMC tiếp tục chứng tỏ vị thế là trung tâm kinh tế và công nghệ lớn nhất cả nước.
* **Hà Nội:** Chiếm **{hanoi_ratio:.1f}%** nhu cầu tuyển dụng.
* Các khu vực khác gồm Đà Nẵng và các vị trí làm việc hoàn toàn từ xa (Remote).

## 5. Khuyến Nghị Chiến Lược cho Ứng Viên & Doanh Nghiệp
* **Đối với Ứng viên:** Việc tập trung trang bị các kỹ năng như **{top_skill}** sẽ gia tăng cơ hội ứng tuyển. Đồng thời, nâng cao kinh nghiệm thực tế là chìa khóa vàng giúp gia tăng thu nhập nhanh nhất.
* **Đối với Doanh nghiệp:** Để thu hút nhân lực chất lượng cao, các doanh nghiệp cần thiết kế cơ chế lương thưởng cạnh tranh tiệm cận mức trung bình thị trường (${avg_salary:,.0f} USD) và tăng cường đưa ra các lựa chọn làm việc linh hoạt (Remote/Hybrid) để mở rộng tệp ứng tuyển.
"""
    
    st.markdown(report_markdown)
    
    st.write("---")
    # Nút tải báo cáo
    st.download_button(
        label="📥 Tải Báo cáo Insights (.MD)",
        data=report_markdown.encode("utf-8"),
        file_name="it_market_analysis_report.md",
        mime="text/markdown",
        width='stretch'
    )
    st.markdown('</div>', unsafe_allow_html=True)
