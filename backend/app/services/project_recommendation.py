"""Service for generating project recommendations."""

from typing import List

from app.models.project_recommendation import (
    ProjectRecommendation,
    ProjectRecommendationsResponse,
)


def get_project_recommendations(
    skill: str,
) -> ProjectRecommendationsResponse:
    """Return portfolio project recommendations for a skill."""

    normalized_skill = skill.strip().lower()

    project_map = {
        "docker": [
            ProjectRecommendation(
                title="Containerized Machine Learning API",
                description=(
                    "Build a machine learning prediction API with FastAPI "
                    "and package the application using Docker."
                ),
                skills=["Docker", "FastAPI", "Python", "Machine Learning"],
                portfolio_value=(
                    "Demonstrates containerization and deployment skills "
                    "for machine learning applications."
                ),
            ),
        ],
        "aws": [
            ProjectRecommendation(
                title="Cloud-Based ML Deployment",
                description=(
                    "Deploy a machine learning API on AWS and expose it "
                    "through a simple production-style workflow."
                ),
                skills=["AWS", "Python", "FastAPI", "Machine Learning"],
                portfolio_value=(
                    "Demonstrates practical cloud deployment knowledge "
                    "for machine learning workloads."
                ),
            ),
        ],

        "deep learning": [
    ProjectRecommendation(
        title="Deep Learning Image Classification API",
        description=(
            "Build a deep learning image classification model using "
            "TensorFlow or PyTorch and expose predictions through a FastAPI service."
        ),
        skills=[
            "Deep Learning",
            "TensorFlow",
            "PyTorch",
            "Python",
            "FastAPI",
        ],
        portfolio_value=(
            "Demonstrates practical deep learning model development, "
            "inference, and API deployment skills."
        ),
    ),
],

        "kubernetes": [
            ProjectRecommendation(
                title="Kubernetes ML Service",
                description=(
                    "Deploy a containerized machine learning API using "
                    "Kubernetes and configure basic service management."
                ),
                skills=[
                    "Kubernetes",
                    "Docker",
                    "FastAPI",
                    "Machine Learning",
                ],
                portfolio_value=(
                    "Demonstrates container orchestration and deployment "
                    "skills relevant to ML engineering."
                ),
            ),
        ],
        "python": [
            ProjectRecommendation(
                title="End-to-End Data Science Project",
                description=(
                    "Build a complete data science application using "
                    "Python for data processing, modeling, and prediction."
                ),
                skills=["Python", "Pandas", "NumPy", "Scikit-learn"],
                portfolio_value=(
                    "Demonstrates practical Python and machine learning "
                    "development skills."
                ),
            ),
        ],
    }

    projects: List[ProjectRecommendation] = project_map.get(
        normalized_skill,
        [],
    )

    return ProjectRecommendationsResponse(
        skill=skill,
        projects=projects,
    )