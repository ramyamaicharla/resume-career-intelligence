"""Pydantic schemas for Learning Resources."""

from typing import List

from pydantic import BaseModel, Field


class LearningResource(BaseModel):
    """A learning resource for a skill."""

    title: str = Field(
        ...,
        description="Name of the learning resource",
    )

    resource_type: str = Field(
        ...,
        description="Type of resource such as Course, Documentation, Tutorial, or Project",
    )

    url: str = Field(
        ...,
        description="URL of the learning resource",
    )

    skill: str = Field(
        ...,
        description="Skill covered by the resource",
    )


class LearningResourcesResponse(BaseModel):
    """Response containing learning resources for a skill."""

    skill: str

    resources: List[LearningResource] = Field(
        default_factory=list,
        description="Recommended learning resources",
    )