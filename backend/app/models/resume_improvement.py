"""Pydantic schemas for Resume Improvement."""

from typing import List

from pydantic import BaseModel, Field


class ResumeImprovementSuggestion(BaseModel):
    """A single resume improvement suggestion."""

    section: str = Field(
        ...,
        description="Resume section containing the issue",
    )

    original_text: str = Field(
        ...,
        description="Original resume text",
    )

    suggested_text: str = Field(
        ...,
        description="Improved resume text",
    )

    reason: str = Field(
        ...,
        description="Why the improvement is recommended",
    )


class ResumeImprovementRequest(BaseModel):
    """Request for resume improvement."""

    resume: dict = Field(
        default_factory=dict,
        description="Structured resume data",
    )

    target_role: str = Field(
        ...,
        description="Target career role",
    )

    job_description: str = Field(
        default="",
        description="Target job description",
    )


class ResumeImprovementResponse(BaseModel):
    """Response containing resume improvement suggestions."""

    target_role: str

    suggestions: List[ResumeImprovementSuggestion] = Field(
        default_factory=list,
    )