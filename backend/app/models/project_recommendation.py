"""Pydantic schemas for Project Recommendations."""

from typing import List

from pydantic import BaseModel, Field


class ProjectRecommendation(BaseModel):
    """A recommended project for a missing skill."""

    title: str = Field(
        ...,
        description="Project title",
    )

    description: str = Field(
        ...,
        description="What the project should build",
    )

    skills: List[str] = Field(
        default_factory=list,
        description="Skills practiced in the project",
    )

    portfolio_value: str = Field(
        ...,
        description="Why this project is valuable for a portfolio",
    )


class ProjectRecommendationsResponse(BaseModel):
    """Recommended projects for a skill."""

    skill: str

    projects: List[ProjectRecommendation] = Field(
        default_factory=list,
        description="Recommended portfolio projects",
    )