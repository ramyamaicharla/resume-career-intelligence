"""Resume Improvement API routes."""

from fastapi import APIRouter

from app.models.resume_improvement import (
    ResumeImprovementRequest,
    ResumeImprovementResponse,
)
from app.services.resume_improvement import improve_resume


router = APIRouter(
    prefix="/resume",
    tags=["resume-improvement"],
)


@router.post(
    "/improve",
    response_model=ResumeImprovementResponse,
)
async def improve_resume_endpoint(
    request: ResumeImprovementRequest,
):
    """Generate personalized resume improvement suggestions."""

    return await improve_resume(
        resume=request.resume,
        target_role=request.target_role,
        job_description=request.job_description,
    )