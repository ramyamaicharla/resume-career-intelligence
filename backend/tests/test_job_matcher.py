"""Tests for Resume-to-Job-Description Matching module."""
from fastapi.testclient import TestClient
from app.main import app
from app.models.resume import (
    EducationItem,
    ExperienceItem,
    ProjectItem,
    StructuredResume,
)
from app.models.job_match import JobMatchRequest, JobMatchResponse
from app.services.job_matcher import match_resume_to_job

client = TestClient(app)


def _create_sample_resume():
    return StructuredResume(
        name="Taylor Dev",
        email="taylor.dev@example.com",
        phone="+1-555-987-6543",
        location="Seattle, WA",
        skills=["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
        experience=[
            ExperienceItem(
                company="CloudTech Solutions",
                role="Backend Software Engineer",
                start_date="2022",
                end_date="Present",
                responsibilities=[
                    "Built scalable REST APIs and microservices using Python and FastAPI.",
                    "Managed PostgreSQL database schemas and optimized complex query performance.",
                    "Configured CI/CD pipelines and deployed containerized services to AWS.",
                ],
            )
        ],
        projects=[
            ProjectItem(
                name="E-Commerce API",
                description="Engineered high availability backend handling payment processing and inventory management.",
                technologies=["Python", "Docker", "Redis"],
            )
        ],
        education=[
            EducationItem(
                institution="University of Washington",
                degree="Bachelor of Science",
                field_of_study="Computer Science",
            )
        ],
    )


def test_full_match_scenario():
    """Verify 100% match when candidate covers all requested JD skills and domain keywords."""
    resume = _create_sample_resume()
    jd = """
    We are seeking a Backend Engineer with experience in Python, FastAPI, Docker, and AWS.
    Must be proficient with PostgreSQL, REST APIs, Microservices, and CI/CD pipelines.
    """

    result = match_resume_to_job(resume, jd)

    assert isinstance(result, JobMatchResponse)
    assert result.overall_match_percentage == 100
    assert len(result.missing_skills) == 0
    assert len(result.missing_keywords) == 0
    assert "Python" in result.matched_skills
    assert "FastAPI" in result.matched_skills
    assert "PostgreSQL" in result.matched_skills
    assert "Docker" in result.matched_skills
    assert "AWS" in result.matched_skills
    assert "REST APIs" in result.matched_keywords
    assert "Microservices" in result.matched_keywords
    assert "CI/CD" in result.matched_keywords
    assert any("Strong alignment detected" in rec for rec in result.recommendations)


def test_partial_match_scenario():
    """Verify accurate percentage and gap detection for partial match."""
    resume = _create_sample_resume()
    jd = """
    Requirements:
    - Python and FastAPI development
    - Experience with Kubernetes (k8s) and Terraform for infrastructure
    - GraphQL API development
    - PostgreSQL database management
    """

    result = match_resume_to_job(resume, jd)

    assert result.overall_match_percentage > 0
    assert result.overall_match_percentage < 100

    # Matched skills
    assert "Python" in result.matched_skills
    assert "FastAPI" in result.matched_skills
    assert "PostgreSQL" in result.matched_skills

    # Missing skills - not in resume
    assert "Kubernetes" in result.missing_skills
    assert "Terraform" in result.missing_skills
    assert "GraphQL" in result.missing_skills

    # Recommendations must label missing skills as not found in resume
    assert any("not found in your resume" in rec for rec in result.recommendations)


def test_zero_match_scenario():
    """Verify 0% match when resume and JD have no overlapping skills or keywords."""
    resume = StructuredResume(
        name="Mobile Dev",
        skills=["Swift", "Kotlin"],
        experience=[
            ExperienceItem(
                company="App Co",
                role="iOS Developer",
                responsibilities=["Developed iOS applications using Swift."],
            )
        ],
    )
    jd = "Looking for a Ruby on Rails developer with Elixir and MariaDB experience."

    result = match_resume_to_job(resume, jd)

    assert result.overall_match_percentage == 0
    assert len(result.matched_skills) == 0
    assert len(result.matched_keywords) == 0
    assert "Ruby on Rails" in result.missing_skills
    assert "Elixir" in result.missing_skills
    assert "MariaDB" in result.missing_skills


def test_alias_normalization_and_case_insensitivity():
    """Verify normalization of common variants (e.g. k8s -> Kubernetes, postgres -> PostgreSQL)."""
    resume = StructuredResume(
        name="Dev",
        skills=["python", "k8s", "postgres", "node.js", "reactjs", "ci/cd"],
    )
    jd = """
    Looking for a developer with Node.js, React, Kubernetes, PostgreSQL, and continuous integration (CI/CD) experience.
    """

    result = match_resume_to_job(resume, jd)

    # Canonical names should match regardless of punctuation/casing variations
    assert "Node.js" in result.matched_skills
    assert "React" in result.matched_skills
    assert "Kubernetes" in result.matched_skills
    assert "PostgreSQL" in result.matched_skills
    assert "CI/CD" in result.matched_skills
    assert result.overall_match_percentage == 100


def test_false_positive_prevention():
    """Verify common English words ('go', 'next', 'java' in javascript) don't cause false positives."""
    resume = StructuredResume(
        name="Junior Dev",
        skills=["JavaScript"],
        experience=[
            ExperienceItem(
                company="Startup",
                role="Web Intern",
                responsibilities=["Help team go beyond expectations next quarter."],
            )
        ],
    )
    # JD with English phrases "go", "next" without the programming languages
    jd = "We want candidates who will go above and beyond next year."

    result = match_resume_to_job(resume, jd)

    # Should NOT falsely identify "Go" or "Next.js"
    assert "Go" not in result.matched_skills
    assert "Next.js" not in result.matched_skills
    assert "Go" not in result.missing_skills


def test_recommendations_never_assume_lack_of_skill():
    """Ensure recommendations label gaps strictly as 'not found in resume' and don't invent experience."""
    resume = StructuredResume(
        name="Candidate",
        skills=["Python"],
    )
    jd = "Requires Python, Docker, and Kubernetes."

    result = match_resume_to_job(resume, jd)

    rec_text = " ".join(result.recommendations)
    assert "not found in" in rec_text.lower()
    # Must NOT claim candidate lacks or is incapable of the skill
    assert "candidate lacks" not in rec_text.lower()
    assert "you lack" not in rec_text.lower()


def test_post_job_match_endpoint_nested_format():
    """Test POST /resume/job-match with explicit nested {'resume': ..., 'job_description': ...} format."""
    payload = {
        "resume": {
            "name": "Jane Doe",
            "skills": ["Python", "FastAPI", "Docker"],
            "experience": [
                {
                    "company": "Tech Corp",
                    "role": "Software Engineer",
                    "responsibilities": ["Built microservices in Python."],
                }
            ],
        },
        "job_description": "Seeking Python engineer with Docker and Microservices experience.",
    }

    response = client.post("/resume/job-match", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "overall_match_percentage" in data
    assert "matched_keywords" in data
    assert "missing_keywords" in data
    assert "matched_skills" in data
    assert "missing_skills" in data
    assert "recommendations" in data

    assert data["overall_match_percentage"] == 100
    assert "Python" in data["matched_skills"]
    assert "Docker" in data["matched_skills"]
    assert "Microservices" in data["matched_keywords"]


def test_post_job_match_endpoint_flattened_format():
    """Test POST /resume/job-match with flattened format where resume fields are at root alongside job_description."""
    payload = {
        "name": "John Smith",
        "skills": ["React", "TypeScript"],
        "job_description": "Frontend developer with React, TypeScript, and Tailwind CSS.",
    }

    response = client.post("/resume/job-match", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "React" in data["matched_skills"]
    assert "TypeScript" in data["matched_skills"]
    assert "Tailwind CSS" in data["missing_skills"]
    assert data["overall_match_percentage"] == 67  # 2 matched out of 3 total detected


def test_post_job_match_endpoint_validation_error():
    """Test POST /resume/job-match returns 422 if job_description is missing."""
    payload = {
        "resume": {
            "name": "Candidate",
            "skills": ["Python"],
        }
    }
    response = client.post("/resume/job-match", json=payload)
    assert response.status_code == 422


def test_existing_endpoints_preserved():
    """Verify that existing endpoints remain intact and callable."""
    # 1. Health check
    health_resp = client.get("/health")
    assert health_resp.status_code == 200

    # 2. ATS score endpoint
    ats_resp = client.post(
        "/resume/ats-score",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "phone": "555-123-4567",
            "skills": ["Python", "FastAPI", "Docker", "AWS", "PostgreSQL", "Git", "Redis", "Linux", "CI/CD", "REST APIs"],
        },
    )
    assert ats_resp.status_code == 200
    assert "score" in ats_resp.json()


if __name__ == "__main__":
    test_full_match_scenario()
    test_partial_match_scenario()
    test_zero_match_scenario()
    test_alias_normalization_and_case_insensitivity()
    test_false_positive_prevention()
    test_recommendations_never_assume_lack_of_skill()
    test_post_job_match_endpoint_nested_format()
    test_post_job_match_endpoint_flattened_format()
    test_post_job_match_endpoint_validation_error()
    test_existing_endpoints_preserved()
    print("All test cases passed successfully!")
