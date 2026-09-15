"""Pydantic schemas for Career Roadmap."""

from typing import List

from pydantic import BaseModel, Field


class RoadmapPhase(BaseModel):
    """A learning phase in the career roadmap."""

    phase: int = Field(
        ...,
        description="Phase number",
    )

    skill: str = Field(
        ...,
        description="Skill to learn",
    )

    level: str = Field(
        ...,
        description="Learning level: Beginner, Intermediate, or Advanced",
    )

    goal: str = Field(
        ...,
        description="What the learner should achieve in this phase",
    )


class RoadmapSkill(BaseModel):
    """A skill included in the career roadmap."""

    skill: str = Field(
        ...,
        description="Skill to learn",
    )

    priority: str = Field(
        ...,
        description="Learning priority: High, Medium, or Low",
    )

    reason: str = Field(
        ...,
        description="Why this skill is important for the target role",
    )


class CareerRoadmapResponse(BaseModel):
    """Response containing a personalized career roadmap."""

    target_role: str

    current_skills: List[str] = Field(
        default_factory=list,
    )

    missing_skills: List[str] = Field(
        default_factory=list,
    )

    roadmap: List[RoadmapSkill] = Field(
        default_factory=list,
    )

    phases: List[RoadmapPhase] = Field(
        default_factory=list,
    )

    recommendations: List[str] = Field(
        default_factory=list,
    )


class CareerRoadmapRequest(BaseModel):
    """Request for generating a personalized career roadmap."""

    target_role: str

    current_skills: List[str] = Field(
        default_factory=list,
    )

    missing_skills: List[str] = Field(
        default_factory=list,
    )
