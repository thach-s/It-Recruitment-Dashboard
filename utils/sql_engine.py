import duckdb
import pandas as pd
from typing import Tuple, Dict, List

def execute_sql_query(df: pd.DataFrame, query: str) -> Tuple[pd.DataFrame, str]:
    """
    Executes a SQL query against a registered pandas DataFrame using DuckDB.
    Returns a tuple of (result_dataframe, error_message).
    If successful, error_message is empty.
    If fails, result_dataframe is empty.
    """
    con = duckdb.connect(database=':memory:')
    try:
        # Register the dataframe as table "jobs"
        con.register('jobs', df)
        # Execute query
        result_df = con.execute(query).df()
        return result_df, ""
    except Exception as e:
        return pd.DataFrame(), str(e)
    finally:
        con.close()

def get_predefined_queries() -> List[Dict[str, str]]:
    """
    Returns a list of predefined SQL queries for the dashboard users.
    """
    return [
        {
            "name": "💰 Thống kê Lương & Số lượng tuyển dụng theo Vai trò",
            "query": """-- Thống kê tổng số lượng công việc, mức lương trung bình, tối thiểu, tối đa theo vai trò
SELECT 
    role_category AS "Vai trò", 
    COUNT(*) AS "Số lượng tuyển dụng", 
    ROUND(AVG(salary_usd), 0) AS "Lương TB (USD)",
    MIN(salary_usd) AS "Lương Thấp Nhất (USD)",
    MAX(salary_usd) AS "Lương Cao Nhất (USD)"
FROM jobs 
GROUP BY role_category 
ORDER BY "Lương TB (USD)" DESC;"""
        },
        {
            "name": "🔥 Top 10 công việc có mức lương cao nhất",
            "query": """-- Danh sách 10 vị trí có mức lương tuyển dụng cao nhất, yêu cầu kinh nghiệm tương ứng
SELECT 
    job_title AS "Tiêu đề công việc", 
    location AS "Địa điểm", 
    company_size AS "Quy mô công ty",
    experience_years AS "Kinh nghiệm (Năm)", 
    salary_usd AS "Mức lương (USD)"
FROM jobs 
ORDER BY salary_usd DESC 
LIMIT 10;"""
        },
        {
            "name": "🌐 Phân tích Hình thức làm việc (Work Mode): Tỷ lệ & Mức lương",
            "query": """-- Phân tích tỷ lệ việc làm và mức lương trung bình theo hình thức (Remote, Hybrid, On-site)
SELECT 
    work_mode AS "Hình thức làm việc", 
    COUNT(*) AS "Số lượng", 
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs), 2) || '%' AS "Tỷ lệ %",
    ROUND(AVG(salary_usd), 0) AS "Lương TB (USD)"
FROM jobs 
GROUP BY work_mode 
ORDER BY "Lương TB (USD)" DESC;"""
        },
        {
            "name": "📈 Khảo sát lương theo Cấp bậc Kinh nghiệm",
            "query": """-- Phân chia lương trung bình theo nhóm số năm kinh nghiệm thực tế
SELECT 
    CASE 
        WHEN experience_years = 0 THEN '0. Intern/Fresher (0 năm)'
        WHEN experience_years BETWEEN 1 AND 2 THEN '1. Junior (1-2 năm)'
        WHEN experience_years BETWEEN 3 AND 5 THEN '2. Mid-level (3-5 năm)'
        WHEN experience_years BETWEEN 6 AND 8 THEN '3. Senior (6-8 năm)'
        ELSE '4. Lead/Manager (>8 năm)'
    END AS "Cấp bậc",
    COUNT(*) AS "Số lượng tuyển",
    ROUND(AVG(salary_usd), 0) AS "Lương TB (USD)"
FROM jobs
GROUP BY 1
ORDER BY "Cấp bậc" ASC;"""
        },
        {
            "name": "🏢 Tương quan giữa Quy mô Công ty và Mức lương tuyển dụng",
            "query": """-- Phân tích xem quy mô công ty ảnh hưởng thế nào đến mức lương trung bình và kinh nghiệm yêu cầu
SELECT 
    company_size AS "Quy mô công ty",
    COUNT(*) AS "Số lượng tin tuyển",
    ROUND(AVG(experience_years), 1) AS "Kinh nghiệm TB (Năm)",
    ROUND(AVG(salary_usd), 0) AS "Lương TB (USD)"
FROM jobs
GROUP BY company_size
ORDER BY "Lương TB (USD)" DESC;"""
        }
    ]
