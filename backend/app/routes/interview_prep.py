"""Interview Preparation API routes."""

from fastapi import APIRouter

from app.models.interview_prep import (
    InterviewPreparationRequest,
    InterviewPreparationResponse,
)
from app.services.interview_prep import generate_interview_questions


router = APIRouter(
    prefix="/interview",
    tags=["interview-preparation"],
)


@router.post(
    "/questions",
    response_model=InterviewPreparationResponse,
)
async def interview_questions(
    request: InterviewPreparationRequest,
):
    """Generate personalized interview questions."""

    return await generate_interview_questions(request)