"""Provider for learning resources."""

from typing import List

from app.models.learning_resources import LearningResource


RESOURCE_MAP = {
    "docker": [
        LearningResource(
            title="Docker Documentation",
            resource_type="Documentation",
            url="https://docs.docker.com/",
            skill="Docker",
        ),
    ],
    "aws": [
        LearningResource(
            title="AWS Documentation",
            resource_type="Documentation",
            url="https://docs.aws.amazon.com/",
            skill="AWS",
        ),
    ],
    "kubernetes": [
        LearningResource(
            title="Kubernetes Documentation",
            resource_type="Documentation",
            url="https://kubernetes.io/docs/",
            skill="Kubernetes",
        ),
    ],
    "python": [
        LearningResource(
            title="Python Documentation",
            resource_type="Documentation",
            url="https://docs.python.org/3/",
            skill="Python",
        ),
    ],
    "sql": [
        LearningResource(
            title="SQL Tutorial",
            resource_type="Tutorial",
            url="https://www.w3schools.com/sql/",
            skill="SQL",
        ),
    ],
    "deep learning": [
        LearningResource(
            title="Deep Learning Specialization",
            resource_type="Course",
            url="https://www.deeplearning.ai/courses/deep-learning-specialization/",
            skill="Deep Learning",
        ),
    ],
}


def get_resources_for_skill(skill: str) -> List[LearningResource]:
    """Return learning resources for the requested skill."""

    normalized_skill = skill.strip().lower()

    return RESOURCE_MAP.get(normalized_skill, [])