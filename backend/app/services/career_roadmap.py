"""Service for generating a deterministic Career Roadmap."""

from typing import List

from app.models.career_roadmap import (
    CareerRoadmapResponse,
    RoadmapPhase,
    RoadmapSkill,
)


def generate_career_roadmap(
    target_role: str,
    current_skills: List[str],
    missing_skills: List[str],
) -> CareerRoadmapResponse:
    """Generate a prioritized roadmap from missing skills."""

    high_priority_keywords = {
        "python",
        "sql",
        "machine learning",
        "deep learning",
        "docker",
        "aws",
        "kubernetes",
    }

    current_skill_set = {
        skill.strip().lower()
        for skill in current_skills
        if skill and skill.strip()
    }

    roadmap = []

    phases = []

    for index, skill in enumerate(missing_skills, start=1):
        phases.append(
            RoadmapPhase(
                phase=index,
                skill=skill,
                level="Beginner",
                goal=f"Learn the fundamentals of {skill} and practice them with a small project.",
            )
        )

    for skill in missing_skills:
        normalized_skill = skill.strip().lower()

        if normalized_skill in high_priority_keywords:
            priority = "High"
            reason = (
                f"{skill} is an important skill for building "
                f"job-ready capability as a {target_role}."
            )
        else:
            priority = "Medium"
            reason = (
                f"{skill} can strengthen your technical profile "
                f"for the {target_role} role."
            )

        roadmap.append(
            RoadmapSkill(
                skill=skill.strip(),
                priority=priority,
                reason=reason,
            )
        )

    recommendations = []

    if missing_skills:
        recommendations.append(
            "Start with the highest-priority missing skills."
        )

        recommendations.append(
            "Build practical projects while learning each new skill."
        )

        recommendations.append(
            "Add a skill to your resume only after gaining genuine "
            "hands-on experience."
        )
    else:
        recommendations.append(
            "Your current skills cover the provided requirements. "
            "Focus on advanced projects and interview preparation."
        )

    return CareerRoadmapResponse(
        target_role=target_role,
        current_skills=current_skills,
        missing_skills=missing_skills,
        roadmap=roadmap,
        phases=phases,
        recommendations=recommendations,
    )