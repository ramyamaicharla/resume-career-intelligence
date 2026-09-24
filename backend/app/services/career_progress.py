from app.models.career_progress import (
    CareerProgressRequest,
    CareerProgressResponse,
)


def calculate_career_progress(
    request: CareerProgressRequest,
) -> CareerProgressResponse:

    completed_skills = [
        skill.strip()
        for skill in request.completed_skills
        if skill and skill.strip()
    ]

    roadmap_skills = [
        skill.strip()
        for skill in request.roadmap_skills
        if skill and skill.strip()
    ]

    completed_normalized = {
        skill.lower()
        for skill in completed_skills
    }

    remaining_skills = [
        skill
        for skill in roadmap_skills
        if skill.lower() not in completed_normalized
    ]

    total_skills = len(roadmap_skills)

    completed_roadmap_skills = [
        skill
        for skill in roadmap_skills
        if skill.lower() in completed_normalized
    ]

    if total_skills == 0:
        progress_percentage = 0.0
    else:
        progress_percentage = round(
            (len(completed_roadmap_skills) / total_skills) * 100,
            2,
        )

    return CareerProgressResponse(
        target_role=request.target_role,
        completed_skills=completed_skills,
        remaining_skills=remaining_skills,
        current_phase=request.current_phase,
        progress_percentage=progress_percentage,
    )