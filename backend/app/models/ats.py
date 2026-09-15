"""Pydantic schemas for ATS Compatibility Scoring."""
from typing import Any, Dict, List
from pydantic import BaseModel, Field, model_validator
from app.models.resume import StructuredResume


class ATSScoreResponse(BaseModel):
    """ATS Compatibility Score response model.

    Evaluates resume parseability, keyword density, and formatting against standard
    Applicant Tracking System (ATS) heuristics. Does not represent a specific commercial
    vendor's proprietary algorithm.
    """

    score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall ATS Compatibility Score (0 to 100)",
    )
    category_scores: Dict[str, int] = Field(
        ...,
        description="Deterministic score breakdown by category",
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="List of positive ATS-friendly attributes identified in the resume",
    )
    issues: List[str] = Field(
        default_factory=list,
        description="List of detected issues with explicit point deductions and reasons",
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Actionable recommendations to improve ATS compatibility",
    )


class ATSScoreRequest(StructuredResume):
    """Request payload for ATS Compatibility Scoring.

    Supports both direct StructuredResume objects and wrapped payloads e.g. {'resume': {...}}.
    """

    @model_validator(mode="before")
    @classmethod
    def unwrap_resume_wrapper(cls, data: Any) -> Any:
        if isinstance(data, dict) and "resume" in data and isinstance(data["resume"], dict):
            return data["resume"]
        return data
