"""Pydantic schemas for Interview Preparation."""

from typing import List

from pydantic import BaseModel, Field


class InterviewQuestion(BaseModel):
    """An interview question."""

    question: str = Field(
        ...,
        description="Interview question",
    )

    question_type: str = Field(
        ...,
        description="Technical, Behavioral, Resume-Based, or Job-Description-Based",
    )

    difficulty: str = Field(
        ...,
        description="Easy, Medium, or Hard",
    )


class InterviewPreparationRequest(BaseModel):
    """Request for personalized interview preparation."""

    target_role: str = Field(
        ...,
        description="Target job role",
    )

    resume: dict = Field(
        default_factory=dict,
        description="Structured resume data",
    )

    job_description: str = Field(
        default="",
        description="Target job description",
    )


class InterviewPreparationResponse(BaseModel):
    """Interview preparation questions."""

    target_role: str

    questions: List[InterviewQuestion] = Field(
        default_factory=list,
        description="Personalized interview questions",
    )