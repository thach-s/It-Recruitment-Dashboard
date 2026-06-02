import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_it_recruitment_data(n_samples=1000, seed=42):
    """
    Generates a realistic IT recruitment dataset for Vietnam/Global market in 2026.
    """
    np.random.seed(seed)
    random.seed(seed)
    
    # 1. Job Titles and their base salaries & skill pools
    job_profiles = {
        "AI/ML Engineer": {
            "base_salary": 2000,
            "skills": ["Python", "PyTorch", "TensorFlow", "Scikit-Learn", "SQL", "Docker", "Hugging Face", "LLMs", "Git"],
            "prob": 0.12
        },
        "Python Backend Developer": {
            "base_salary": 1400,
            "skills": ["Python", "FastAPI", "Django", "PostgreSQL", "Redis", "Docker", "AWS", "Git", "REST API"],
            "prob": 0.15
        },
        "Frontend Developer (React/Vue)": {
            "base_salary": 1100,
            "skills": ["JavaScript", "TypeScript", "React", "Vue.js", "HTML5", "CSS3", "TailwindCSS", "Git", "Redux"],
            "prob": 0.18
        },
        "DevOps Engineer": {
            "base_salary": 1800,
            "skills": ["Docker", "Kubernetes", "AWS", "Terraform", "CI/CD", "Linux", "Python", "Bash", "Prometheus"],
            "prob": 0.10
        },
        "Data Analyst": {
            "base_salary": 1000,
            "skills": ["Python", "SQL", "Power BI", "Tableau", "Excel", "Pandas", "Statistics", "A/B Testing"],
            "prob": 0.12
        },
        "Java Developer": {
            "base_salary": 1300,
            "skills": ["Java", "Spring Boot", "MySQL", "Hibernate", "Microservices", "Docker", "Git", "Maven"],
            "prob": 0.13
        },
        "Mobile App Developer": {
            "base_salary": 1200,
            "skills": ["Flutter", "React Native", "Swift", "Kotlin", "Dart", "Git", "REST API", "Firebase"],
            "prob": 0.08
        },
        "QA/QC Automation Engineer": {
            "base_salary": 900,
            "skills": ["Selenium", "Python", "Java", "Postman", "CI/CD", "Cypress", "Jira", "SQL"],
            "prob": 0.07
        },
        "Solutions Architect": {
            "base_salary": 2800,
            "skills": ["AWS", "Azure", "System Design", "Microservices", "Security", "Kubernetes", "Enterprise Architecture"],
            "prob": 0.05
        }
    }
    
    titles = list(job_profiles.keys())
    probs = [job_profiles[t]["prob"] for t in titles]
    # Normalize probabilities to sum to 1
    probs = np.array(probs) / sum(probs)
    
    data = []
    
    locations = ["Ho Chi Minh City", "Ha Noi", "Da Nang", "Remote"]
    location_probs = [0.45, 0.35, 0.12, 0.08]
    
    company_sizes = ["Small (Startup)", "Medium (SME)", "Large (Enterprise)"]
    company_size_probs = [0.25, 0.50, 0.25]
    
    job_types = ["Full-time", "Contract", "Internship"]
    job_type_probs = [0.85, 0.10, 0.05]
    
    work_modes = ["On-site", "Hybrid", "Remote"]
    
    # Start date for postings
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    
    for i in range(n_samples):
        # Select title
        title = np.random.choice(titles, p=probs)
        profile = job_profiles[title]
        
        # Experience (years) - beta distribution to make it right-skewed (more juniors than seniors)
        exp_years = int(np.random.beta(2, 5) * 15) # 0 to 15 years
        
        # Adjust job title with seniority levels based on experience
        if exp_years == 0 and "Solutions Architect" not in title:
            title_with_level = f"Junior {title} (Intern/Fresh)" if title != "Solutions Architect" else title
            # Interns can have 0 exp
        elif exp_years <= 2:
            title_with_level = f"Junior {title}"
        elif exp_years <= 5:
            title_with_level = f"Mid-level {title}"
        elif exp_years <= 8:
            title_with_level = f"Senior {title}"
        else:
            title_with_level = f"Lead/Principal {title}" if "Architect" not in title else title
            
        # Select location
        loc = np.random.choice(locations, p=location_probs)
        
        # Select work mode
        if loc == "Remote":
            work_mode = "Remote"
        else:
            work_mode = np.random.choice(work_modes, p=[0.40, 0.45, 0.15])
            if work_mode == "Remote":
                # update location to Remote if work mode is remote sometimes
                if random.random() > 0.5:
                    loc = "Remote"
        
        # Select company size
        company_size = np.random.choice(company_sizes, p=company_size_probs)
        
        # Select job type
        job_type = np.random.choice(job_types, p=job_type_probs)
        if job_type == "Internship":
            exp_years = 0
            title_with_level = f"Intern {title}"
            
        # Calculate Salary based on Title, Experience, Location, Company Size
        base = profile["base_salary"]
        
        # Salary increment per year of experience (linear + log components for realistic dimishing returns)
        exp_bonus = 400 * exp_years - 15 * (exp_years ** 1.5)
        
        # Location adjustments
        loc_mult = 1.0
        if loc == "Ho Chi Minh City":
            loc_mult = 1.10
        elif loc == "Ha Noi":
            loc_mult = 1.02
        elif loc == "Da Nang":
            loc_mult = 0.90
        elif loc == "Remote":
            loc_mult = 1.05
            
        # Company size adjustments
        size_mult = 1.0
        if company_size == "Large (Enterprise)":
            size_mult = 1.15
        elif company_size == "Small (Startup)":
            size_mult = 0.92
            
        # Job Type adjustments
        type_mult = 1.0
        if job_type == "Internship":
            base = 300 # flat base for interns
            exp_bonus = 0
            size_mult = 1.0
            
        # Calculate final expected salary
        expected_salary = (base + exp_bonus) * loc_mult * size_mult
        
        # Add random variation (noise) ~ 15% standard deviation
        salary_usd = int(np.random.normal(expected_salary, expected_salary * 0.12))
        
        # Apply salary floors
        if job_type == "Internship":
            salary_usd = max(200, min(600, salary_usd))
        else:
            salary_usd = max(500, salary_usd) # No full-time IT job under $500
            
        # Skills selection (Pick 3 to 6 skills from the profile's skill pool + 1 or 2 general skills)
        n_skills = random.randint(3, 6)
        profile_skills = list(profile["skills"])
        selected_skills = random.sample(profile_skills, min(n_skills, len(profile_skills)))
        
        # General IT skills pool
        general_skills = ["Git", "Agile", "Scrum", "Communication", "English", "Problem Solving", "Teamwork"]
        n_general = random.randint(1, 2)
        selected_general = random.sample(general_skills, n_general)
        
        # Merge and remove duplicates
        all_selected_skills = list(set(selected_skills + selected_general))
        skills_str = ", ".join(all_selected_skills)
        
        # Generate post date
        days_ago = random.randint(0, 59)
        posted_date = (end_date - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        data.append({
            "job_id": f"IT-{i+1:04d}",
            "job_title": title_with_level,
            "role_category": title,
            "skills": skills_str,
            "experience_years": exp_years,
            "salary_usd": salary_usd,
            "location": loc,
            "company_size": company_size,
            "job_type": job_type,
            "work_mode": work_mode,
            "posted_date": posted_date
        })
        
    df = pd.DataFrame(data)
    # Sort by posted date descending
    df = df.sort_values(by="posted_date", ascending=False).reset_index(drop=True)
    return df

if __name__ == "__main__":
    df = generate_it_recruitment_data(10)
    print(df.head())
