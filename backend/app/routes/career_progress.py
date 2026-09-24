from fastapi import APIRouter

from app.models.career_progress import (
    CareerProgressRequest,
    CareerProgressResponse,
)
from app.services.career_progress import calculate_career_progress


router = APIRouter(
    prefix="/career-progress",
    tags=["career-progress"],
)


@router.post(
    "/",
    response_model=CareerProgressResponse,
)
async def career_progress(
    request: CareerProgressRequest,
):
    return calculate_career_progress(request)