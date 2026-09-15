"""Learning Resources API routes."""

from fastapi import APIRouter

from app.models.learning_resources import LearningResourcesResponse
from app.services.learning_resources import get_learning_resources


router = APIRouter(
    prefix="/learning",
    tags=["learning-resources"],
)


@router.get(
    "/resources",
    response_model=LearningResourcesResponse,
)
async def learning_resources(skill: str):
    """Get learning resources for a skill."""

    return get_learning_resources(skill)