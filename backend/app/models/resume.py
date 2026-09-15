"""Pydantic schemas for structured resume data."""
from typing import List, Optional
from pydantic import BaseModel, Field


class EducationItem(BaseModel):
    institution: Optional[str] = Field(
        default=None,
        description="Name of the university, college, or educational institution",
    )
    degree: Optional[str] = Field(
        default=None,
        description="Degree or level of qualification (e.g., Bachelor of Science, Master of Science)",
    )
    field_of_study: Optional[str] = Field(
        default=None,
        description="Major, specialization, or field of study",
    )
    start_date: Optional[str] = Field(
        default=None,
        description="Start date or enrollment year",
    )
    end_date: Optional[str] = Field(
        default=None,
        description="End date, graduation year, or 'Expected 2026'",
    )
    gpa: Optional[str] = Field(
        default=None,
        description="GPA or academic honors if mentioned",
    )


class ExperienceItem(BaseModel):
    company: Optional[str] = Field(
        default=None,
        description="Name of the employer or company",
    )
    role: Optional[str] = Field(
        default=None,
        description="Job title or position held",
    )
    location: Optional[str] = Field(
        default=None,
        description="Location of the job (e.g. city, state, country, or 'Remote')",
    )
    start_date: Optional[str] = Field(
        default=None,
        description="Start date or year",
    )
    end_date: Optional[str] = Field(
        default=None,
        description="End date, year, or 'Present'",
    )
    responsibilities: List[str] = Field(
        default_factory=list,
        description="Bullet points describing accomplishments, duties, or responsibilities",
    )


class ProjectItem(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="Title or name of the project",
    )
    description: Optional[str] = Field(
        default=None,
        description="Brief summary of what the project does or achieves",
    )
    technologies: List[str] = Field(
        default_factory=list,
        description="List of tools, programming languages, or frameworks used",
    )
    link: Optional[str] = Field(
        default=None,
        description="URL, GitHub repository, or live demo link if provided",
    )


class CertificationItem(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="Name of the certification or credential",
    )
    issuer: Optional[str] = Field(
        default=None,
        description="Issuing organization (e.g., AWS, Coursera, Google)",
    )
    date: Optional[str] = Field(
        default=None,
        description="Date earned or validity period",
    )


class LinkItem(BaseModel):
    platform: Optional[str] = Field(
        default=None,
        description="Platform or label (e.g. LinkedIn, GitHub, Portfolio, Website)",
    )
    url: Optional[str] = Field(
        default=None,
        description="Full URL string",
    )


class StructuredResume(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="Full name of the candidate",
    )
    email: Optional[str] = Field(
        default=None,
        description="Email address",
    )
    phone: Optional[str] = Field(
        default=None,
        description="Phone number",
    )
    location: Optional[str] = Field(
        default=None,
        description="Current location or address",
    )
    skills: List[str] = Field(
        default_factory=list,
        description="Technical, computational, and domain skills explicitly listed",
    )
    education: List[EducationItem] = Field(
        default_factory=list,
        description="List of educational qualifications",
    )
    experience: List[ExperienceItem] = Field(
        default_factory=list,
        description="List of professional work experiences",
    )
    projects: List[ProjectItem] = Field(
        default_factory=list,
        description="List of relevant technical projects",
    )
    certifications: List[CertificationItem] = Field(
        default_factory=list,
        description="List of certifications or licenses",
    )
    links: List[LinkItem] = Field(
        default_factory=list,
        description="List of profile or portfolio links",
    )


class ResumeAnalyzeRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        description="Extracted resume text to be parsed and structured",
    )
