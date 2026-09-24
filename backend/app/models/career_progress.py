from pydantic import BaseModel, Field
from typing import List


class CareerProgressRequest(BaseModel):
    target_role: str
    roadmap_skills: List[str] = Field(default_factory=list)
    completed_skills: List[str] = Field(default_factory=list)
    current_phase: int = 1


class CareerProgressResponse(BaseModel):
    target_role: str
    completed_skills: List[str] = Field(default_factory=list)
    remaining_skills: List[str] = Field(default_factory=list)
    current_phase: int
    progress_percentage: float