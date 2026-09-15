"""Pydantic schemas for Skill Gap Analysis."""

from typing import List
from pydantic import BaseModel, Field


class SkillGapResponse(BaseModel):
    """Response containing matched and missing skills."""

    matched_skills: List[str] = Field(
        default_factory=list,
        description="Skills already present in the candidate resume",
    )

    missing_skills: List[str] = Field(
        default_factory=list,
        description="Skills required by the target role but missing from the resume",
    )

    skill_gap_percentage: float = Field(
        ...,
        ge=0,
        le=100,
        description="Percentage of required skills missing from the resume",
    )

    recommendations: List[str] = Field(
        default_factory=list,
        description="Actionable recommendations for closing the skill gap",
    )