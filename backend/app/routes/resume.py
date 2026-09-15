"""Resume upload and parsing routes."""
from app.models.career_roadmap import CareerRoadmapRequest, CareerRoadmapResponse
from app.services.career_roadmap import generate_career_roadmap
from app.models.skill_gap import SkillGapResponse
from app.services.skill_gap_analyzer import analyze_skill_gap
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from app.models.resume import ResumeAnalyzeRequest, StructuredResume
from app.models.ats import ATSScoreRequest, ATSScoreResponse
from app.models.job_match import JobMatchRequest, JobMatchResponse
from app.services.resume_extractor import extract_structured_resume
from app.services.resume_parser import extract_text_from_pdf
from app.services.ats_scorer import calculate_ats_score
from app.services.job_matcher import match_resume_to_job

router = APIRouter(prefix="/resume", tags=["resume"])



class ResumeUploadResponse(BaseModel):
    filename: str
    pages: int
    text: str


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    """Accept a resume PDF, validate it, and extract text from all pages."""
    # 1. Validate filename and extension
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a PDF file (.pdf).",
        )

    # 2. Validate MIME type if provided
    if file.content_type and file.content_type not in (
        "application/pdf",
        "application/x-pdf",
        "application/octet-stream",  # some clients send this for pdf
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type '{file.content_type}'. Only PDF files are accepted.",
        )

    # 3. Read file into memory (no permanent storage)
    try:
        contents = await file.read()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not read uploaded file: {str(exc)}",
        ) from exc

    if not contents or len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded PDF file is empty.",
        )

    # 4. Extract text using PyMuPDF
    try:
        parsed_data = extract_text_from_pdf(contents)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        ) from val_err
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the PDF: {str(exc)}",
        ) from exc

    return ResumeUploadResponse(
        filename=file.filename,
        pages=parsed_data["pages"],
        text=parsed_data["text"],
    )


@router.post("/analyze", response_model=StructuredResume)
async def analyze_resume(request: ResumeAnalyzeRequest):
    """Analyze extracted resume text and convert it into validated structured data."""
    try:
        structured_data = await extract_structured_resume(request.text)
        return structured_data
    except ValueError as val_err:
        err_msg = str(val_err)
        if "GEMINI_API_KEY is not set" in err_msg:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=err_msg,
            ) from val_err
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg,
        ) from val_err
    except RuntimeError as run_err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(run_err),
        ) from run_err
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during resume analysis: {str(exc)}",
        ) from exc


@router.post("/ats-score", response_model=ATSScoreResponse)
async def score_resume_ats(request: ATSScoreRequest):
    """Calculate a deterministic ATS Compatibility Score for a structured resume."""
    return calculate_ats_score(request)


@router.post("/job-match", response_model=JobMatchResponse)
async def match_resume_to_job_description(request: JobMatchRequest):
    """Compare a candidate's structured resume against a target job description."""
    return match_resume_to_job(request.resume, request.job_description)


@router.post("/skill-gap", response_model=SkillGapResponse)
async def analyze_resume_skill_gap(
    resume: StructuredResume,
    required_skills: list[str],
):
    """Analyze skill gaps between a resume and target job requirements."""
    return analyze_skill_gap(resume, required_skills)


@router.post(
    "/career-roadmap",
    response_model=CareerRoadmapResponse,
)
async def create_career_roadmap(
    request: CareerRoadmapRequest,
):
    """Generate a personalized career roadmap."""

    return generate_career_roadmap(
        target_role=request.target_role,
        current_skills=request.current_skills,
        missing_skills=request.missing_skills,
    )