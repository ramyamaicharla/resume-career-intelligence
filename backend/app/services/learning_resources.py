"""Service for providing learning resources."""

from app.models.learning_resources import LearningResourcesResponse
from app.services.resource_provider import get_resources_for_skill


def get_learning_resources(skill: str) -> LearningResourcesResponse:
    """Return learning resources for a skill."""

    resources = get_resources_for_skill(skill)

    return LearningResourcesResponse(
        skill=skill,
        resources=resources,
    )