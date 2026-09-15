"""Service for generating resume improvement suggestions."""

import json

from app.models.resume_improvement import (
    ResumeImprovementResponse,
    ResumeImprovementSuggestion,
)
from app.services.llm import generate_gemini_response


async def improve_resume(
    resume: dict,
    target_role: str,
    job_description: str,
) -> ResumeImprovementResponse:
    """Generate personalized resume improvement suggestions using Gemini."""

    prompt = f"""
You are an expert resume and career advisor.

Analyze the candidate's resume against the target role and job description.

Target Role:
{target_role}

Resume:
{json.dumps(resume, indent=2)}

Job Description:
{job_description}

Your task is to identify areas where the resume can be improved.

Requirements:

1. Suggest improvements only for information that already exists
   in the resume.
2. Never invent experience, projects, skills, achievements, metrics,
   companies, or responsibilities.
3. Focus on:
   - Weak bullet points
   - Passive wording
   - Missing action verbs
   - Missing measurable impact
   - Job-relevant keyword improvements
   - Clarity and professional wording
4. Preserve the candidate's actual meaning and experience.
5. Do not add skills that the candidate does not have.
6. Suggestions must be realistic and truthful.
7. If a metric is missing, suggest adding a metric only if the
   candidate can genuinely provide one.
8. Return only useful, actionable suggestions.
9. Avoid duplicate suggestions.

Return ONLY valid JSON in exactly this format:

{{
    "target_role": "{target_role}",
    "suggestions": [
        {{
            "section": "Experience",
            "original_text": "Original resume text",
            "suggested_text": "Improved resume text",
            "reason": "Why this improvement is recommended"
        }}
    ]
}}
"""

    response_text = await generate_gemini_response(prompt)

    try:
        data = json.loads(response_text)

        suggestions = [
            ResumeImprovementSuggestion(
                section=item["section"],
                original_text=item["original_text"],
                suggested_text=item["suggested_text"],
                reason=item["reason"],
            )
            for item in data.get("suggestions", [])
        ]

        return ResumeImprovementResponse(
            target_role=target_role,
            suggestions=suggestions,
        )

    except (json.JSONDecodeError, KeyError, TypeError):
        return ResumeImprovementResponse(
            target_role=target_role,
            suggestions=[],
        )