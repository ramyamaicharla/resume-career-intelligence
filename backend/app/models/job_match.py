"""Pydantic schemas for Resume-to-Job-Description Matching."""
from typing import Any, List
from pydantic import BaseModel, Field, model_validator
from app.models.resume import StructuredResume


class JobMatchRequest(BaseModel):
    """Request payload for matching a structured resume against a target job description."""

    resume: StructuredResume = Field(
        ...,
        description="Candidate's structured resume data",
    )
    job_description: str = Field(
        ...,
        min_length=1,
        description="Target job description text",
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_request_payload(cls, data: Any) -> Any:
        """Support both nested {'resume': {...}, 'job_description': '...'}
        and flattened payloads where resume attributes are at root alongside 'job_description'.
        """
        if isinstance(data, dict):
            # If 'resume' is already explicitly provided
            if "resume" in data and isinstance(data["resume"], dict):
                return data
            # If 'job_description' is present, package remaining fields as resume
            if "job_description" in data:
                jd = data["job_description"]
                resume_data = {k: v for k, v in data.items() if k != "job_description"}
                return {"resume": resume_data, "job_description": jd}
        return data


class JobMatchResponse(BaseModel):
    """Response payload for Resume-to-Job-Description match results."""

    overall_match_percentage: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall match percentage between resume and job description (0 to 100)",
    )
    matched_keywords: List[str] = Field(
        default_factory=list,
        description="All job description keywords found in the resume",
    )
    missing_keywords: List[str] = Field(
        default_factory=list,
        description="Job description keywords not found in the resume",
    )
    matched_skills: List[str] = Field(
        default_factory=list,
        description="Technical skills from the job description found in the resume",
    )
    missing_skills: List[str] = Field(
        default_factory=list,
        description="Technical skills from the job description not found in the resume",
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Actionable recommendations strictly based on detected gaps ('not found in resume')",
    )
