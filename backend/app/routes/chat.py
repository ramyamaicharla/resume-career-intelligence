"""Chat routes for Career Assistant."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.llm import get_career_assistant_response


router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        description="The user's career question",
    )

    resume: dict = Field(
        default_factory=dict,
        description="Structured resume data",
    )

    target_role: str = Field(
        default="",
        description="Target career role",
    )

    job_description: str = Field(
        default="",
        description="Target job description",
    )


class ChatResponse(BaseModel):
    response: str = Field(
        ...,
        description="The AI Career Assistant's personalized response",
    )


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat endpoint for personalized career advice."""

    try:
        context = f"""
Candidate Resume:
{request.resume}

Target Role:
{request.target_role}

Job Description:
{request.job_description}

User Question:
{request.message}
"""

        reply = await get_career_assistant_response(context)

        return ChatResponse(response=reply)

    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(val_err),
        ) from val_err

    except RuntimeError as run_err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(run_err),
        ) from run_err

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(exc)}",
        ) from exc