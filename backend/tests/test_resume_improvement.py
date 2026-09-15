"""Tests for Resume Improvement service."""

import pytest

from app.services import resume_improvement


@pytest.mark.asyncio
async def test_improve_resume():
    """Test resume improvement response using mocked Gemini output."""

    async def mock_gemini_response(prompt: str) -> str:
        return """
        {
            "target_role": "Machine Learning Engineer",
            "suggestions": [
                {
                    "section": "Experience",
                    "original_text": "Learning Python, SQL and Machine Learning.",
                    "suggested_text": "Developed hands-on skills in Python, SQL and Machine Learning through practical training projects.",
                    "reason": "Uses stronger action-oriented wording while preserving the actual experience."
                }
            ]
        }
        """

    resume_improvement.generate_gemini_response = mock_gemini_response

    result = await resume_improvement.improve_resume(
        resume={
            "name": "RAMYA MAICHARLA",
            "skills": [
                "Python",
                "SQL",
                "Machine Learning",
            ],
        },
        target_role="Machine Learning Engineer",
        job_description="Python, SQL, Machine Learning, FastAPI, Docker and AWS.",
    )

    assert result.target_role == "Machine Learning Engineer"
    assert len(result.suggestions) == 1
    assert result.suggestions[0].section == "Experience"