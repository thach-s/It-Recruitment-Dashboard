import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from typing import Tuple, Dict, Any, List

def train_salary_predictor(df: pd.DataFrame) -> Tuple[Pipeline, float, float]:
    """
    Trains a Random Forest Regressor to predict salary based on job characteristics.
    Returns:
        - pipeline: Trained scikit-learn Pipeline
        - r2: R-squared score on test set
        - mae: Mean Absolute Error on test set (USD)
    """
    # Select features and target
    features = ["experience_years", "location", "role_category", "company_size", "work_mode"]
    target = "salary_usd"
    
    X = df[features]
    y = df[target]
    
    # Split into train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Preprocessor for categorical columns
    categorical_features = ["location", "role_category", "company_size", "work_mode"]
    numerical_features = ["experience_years"]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", numerical_features),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features)
        ]
    )
    
    # Create the pipeline
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", RandomForestRegressor(n_estimators=50, max_depth=8, random_state=42))
        ]
    )
    
    # Train
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    y_pred = pipeline.predict(X_test)
    
    # Metrics
    from sklearn.metrics import r2_score, mean_absolute_error
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    
    return pipeline, float(r2), float(mae)

def predict_user_salary(
    model: Pipeline,
    experience_years: int,
    location: str,
    role_category: str,
    company_size: str,
    work_mode: str
) -> float:
    """
    Predicts a salary based on user input features.
    """
    input_data = pd.DataFrame([{
        "experience_years": experience_years,
        "location": location,
        "role_category": role_category,
        "company_size": company_size,
        "work_mode": work_mode
    }])
    
    prediction = model.predict(input_data)[0]
    return float(prediction)

def perform_skill_clustering(df: pd.DataFrame, n_clusters: int = 4) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    """
    Performs K-Means clustering on jobs based on their skills.
    Uses PCA to reduce dimensions for plotting.
    Returns:
        - plot_df: DataFrame with X, Y coordinates, Job Title, Cluster, and Skills
        - cluster_insights: List of descriptions for each cluster
    """
    # 1. Parse skills and create a binary matrix (One-Hot Encoding of skills)
    # Split skills by comma and clean whitespace
    all_skills_series = df["skills"].str.split(", ").explode().str.strip()
    # Get top 30 most frequent skills to avoid high dimensionality noise
    top_skills = all_skills_series.value_counts().head(30).index.tolist()
    
    # Create binary skill matrix
    skill_matrix = np.zeros((len(df), len(top_skills)))
    for idx, skills_str in enumerate(df["skills"]):
        job_skills = [s.strip() for s in skills_str.split(",")]
        for s_idx, skill in enumerate(top_skills):
            if skill in job_skills:
                skill_matrix[idx, s_idx] = 1
                
    # 2. Perform K-Means Clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(skill_matrix)
    
    # 3. Reduce dimensionality to 2D using PCA
    pca = PCA(n_components=2, random_state=42)
    pca_result = pca.fit_transform(skill_matrix)
    
    # 4. Prepare plotting dataframe
    plot_df = pd.DataFrame({
        "x": pca_result[:, 0],
        "y": pca_result[:, 1],
        "cluster": [f"Nhóm {c + 1}" for c in clusters],
        "job_title": df["job_title"],
        "role_category": df["role_category"],
        "skills": df["skills"],
        "salary_usd": df["salary_usd"]
    })
    
    # 5. Extract insights (Top skills for each cluster)
    cluster_insights = []
    for c in range(n_clusters):
        cluster_indices = np.where(clusters == c)[0]
        cluster_skills = skill_matrix[cluster_indices]
        
        # Calculate skill frequencies in this cluster
        skill_frequencies = cluster_skills.sum(axis=0)
        sorted_skill_indices = np.argsort(skill_frequencies)[::-1]
        
        # Get top 5 skills for this cluster
        top_cluster_skills = [top_skills[i] for i in sorted_skill_indices[:5] if skill_frequencies[i] > 0]
        
        # Determine main roles in this cluster
        cluster_roles = df.iloc[cluster_indices]["role_category"].value_counts().head(2)
        roles_desc = " & ".join(cluster_roles.index.tolist())
        
        avg_sal = df.iloc[cluster_indices]["salary_usd"].mean()
        avg_exp = df.iloc[cluster_indices]["experience_years"].mean()
        
        cluster_insights.append({
            "cluster_name": f"Nhóm {c + 1}",
            "top_skills": top_cluster_skills,
            "representative_roles": roles_desc,
            "avg_salary": float(avg_sal),
            "avg_exp": float(avg_exp),
            "count": len(cluster_indices)
        })
        
    return plot_df, cluster_insights
