"""Service for deterministic Skill Gap Analysis."""

from typing import List

from app.models.resume import StructuredResume
from app.models.skill_gap import SkillGapResponse


def normalize_skill(skill: str) -> str:
    """Normalize a skill for case-insensitive comparison."""
    return " ".join(skill.strip().lower().split())


def analyze_skill_gap(
    resume: StructuredResume,
    required_skills: List[str],
) -> SkillGapResponse:
    """Compare resume skills against skills required for a target role."""

    resume_skill_map = {
        normalize_skill(skill): skill.strip()
        for skill in resume.skills
        if skill and skill.strip()
    }

    required_skill_map = {
        normalize_skill(skill): skill.strip()
        for skill in required_skills
        if skill and skill.strip()
    }

    matched_skills = []
    missing_skills = []

    for normalized_skill, original_skill in required_skill_map.items():
        if normalized_skill in resume_skill_map:
            matched_skills.append(resume_skill_map[normalized_skill])
        else:
            missing_skills.append(original_skill)

    total_required = len(required_skill_map)

    if total_required == 0:
        skill_gap_percentage = 0.0
    else:
        skill_gap_percentage = round(
            (len(missing_skills) / total_required) * 100,
            2,
        )

    recommendations = []

    if missing_skills:
        recommendations.append(
            "Prioritize learning the missing skills required for the target role."
        )

        recommendations.append(
            "Build practical projects using the missing skills to demonstrate "
            "hands-on experience."
        )

        recommendations.append(
            "Update the resume only after genuinely gaining experience with "
            "the missing skills."
        )
    else:
        recommendations.append(
            "No major skill gaps were detected against the provided requirements."
        )

    return SkillGapResponse(
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        skill_gap_percentage=skill_gap_percentage,
        recommendations=recommendations,
    )