"""Service for generating personalized interview preparation questions."""

import json

from app.models.interview_prep import (
    InterviewPreparationRequest,
    InterviewPreparationResponse,
    InterviewQuestion,
)
from app.services.llm import generate_gemini_response


async def generate_interview_questions(
    request: InterviewPreparationRequest,
) -> InterviewPreparationResponse:
    """Generate personalized interview questions using Gemini."""

    prompt = f"""
You are an expert technical interviewer.

Generate personalized interview questions for a candidate based on
their resume, target role, and job description.

Target Role:
{request.target_role}

Resume:
{json.dumps(request.resume, indent=2)}

Job Description:
{request.job_description}

Requirements:

1. Generate exactly 10 interview questions.
2. Questions must be personalized to this candidate.
3. Use only information that actually exists in the resume.
4. Never invent projects, skills, experience, companies, or achievements.
5. Include these question types:
   - Technical
   - Resume-Based
   - Job-Description-Based
   - Behavioral
6. Include Easy, Medium, and Hard questions.
7. Resume-Based questions must refer to actual projects,
   technologies, skills, education, or experience in the resume.
8. Job-Description-Based questions must be based on important
   requirements from the provided job description.
9. Technical questions must be relevant to the target role.
10. Behavioral questions should be relevant to the candidate's
    projects, learning journey, and experience.
11. Avoid duplicate or nearly identical questions.
12. Make questions realistic for an actual interview.

Return ONLY valid JSON in exactly this format:

{{
    "target_role": "{request.target_role}",
    "questions": [
        {{
            "question": "Question text",
            "question_type": "Technical",
            "difficulty": "Medium"
        }}
    ]
}}
"""

    response_text = await generate_gemini_response(prompt)

    try:
        data = json.loads(response_text)

        questions = [
            InterviewQuestion(
                question=item["question"],
                question_type=item["question_type"],
                difficulty=item["difficulty"],
            )
            for item in data.get("questions", [])
        ]

        return InterviewPreparationResponse(
            target_role=request.target_role,
            questions=questions,
        )

    except (json.JSONDecodeError, KeyError, TypeError):
        return InterviewPreparationResponse(
            target_role=request.target_role,
            questions=[],
        )