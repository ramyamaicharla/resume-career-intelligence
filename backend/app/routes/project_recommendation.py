"""Project Recommendation API routes."""

from fastapi import APIRouter

from app.models.project_recommendation import ProjectRecommendationsResponse
from app.services.project_recommendation import get_project_recommendations


router = APIRouter(
    prefix="/projects",
    tags=["project-recommendations"],
)


@router.get(
    "/recommendations",
    response_model=ProjectRecommendationsResponse,
)
async def project_recommendations(skill: str):
    """Get project recommendations for a skill."""

    return get_project_recommendations(skill)