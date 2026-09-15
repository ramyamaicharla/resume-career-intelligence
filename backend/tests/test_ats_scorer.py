"""Tests for ATS Compatibility Scoring module."""
import re
from fastapi.testclient import TestClient
from app.main import app
from app.models.resume import (
    EducationItem,
    ExperienceItem,
    ProjectItem,
    CertificationItem,
    LinkItem,
    StructuredResume,
)
from app.models.ats import ATSScoreRequest, ATSScoreResponse
from app.services.ats_scorer import calculate_ats_score

client = TestClient(app)


def test_perfect_resume_scores_100():
    """Verify that a comprehensive, high-quality resume achieves a full 100 ATS Compatibility Score."""
    resume = StructuredResume(
        name="Alex Mercer",
        email="alex.mercer@example.com",
        phone="+1-555-123-4567",
        location="San Francisco, CA",
        skills=[
            "Python", "FastAPI", "Docker", "Kubernetes", "PostgreSQL",
            "Machine Learning", "PyTorch", "AWS", "Git", "REST APIs", "CI/CD"
        ],
        education=[
            EducationItem(
                institution="University of California, Berkeley",
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                start_date="2018",
                end_date="2022",
                gpa="3.9"
            )
        ],
        experience=[
            ExperienceItem(
                company="TechCorp Inc",
                role="Senior Machine Learning Engineer",
                location="San Francisco, CA",
                start_date="2022",
                end_date="Present",
                responsibilities=[
                    "Architected and deployed distributed inference pipeline scaling to 50k daily requests.",
                    "Optimized model inference latency by 45% using TensorRT and quantization.",
                    "Led a cross-functional team of 5 engineers to deliver real-time recommendation engine."
                ]
            )
        ],
        projects=[
            ProjectItem(
                name="AI Career Guidance System",
                description="Engineered an end-to-end resume intelligence pipeline increasing parsing accuracy by 30%.",
                technologies=["Python", "FastAPI", "PyTorch", "Docker"],
                link="https://github.com/alexmercer/career-platform"
            )
        ],
        certifications=[
            CertificationItem(
                name="AWS Certified Solutions Architect",
                issuer="Amazon Web Services",
                date="2023"
            )
        ],
        links=[
            LinkItem(platform="LinkedIn", url="https://linkedin.com/in/alexmercer"),
            LinkItem(platform="GitHub", url="https://github.com/alexmercer")
        ]
    )

    result = calculate_ats_score(resume)

    assert result.score == 100
    assert result.category_scores["contact_information"] == 10
    assert result.category_scores["skills_section"] == 20
    assert result.category_scores["experience_section"] == 20
    assert result.category_scores["projects_section"] == 15
    assert result.category_scores["education"] == 10
    assert result.category_scores["certifications"] == 5
    assert result.category_scores["resume_completeness"] == 10
    assert result.category_scores["ats_friendly_indicators"] == 10
    assert len(result.issues) == 0
    assert len(result.strengths) > 0
    assert sum(result.category_scores.values()) == 100


def test_empty_resume_scores_0_and_accounts_for_all_lost_points():
    """Verify that an empty resume gets 0 and every lost point is accounted for."""
    empty_resume = StructuredResume()
    result = calculate_ats_score(empty_resume)

    assert result.score == 0
    assert result.category_scores["contact_information"] == 0
    assert result.category_scores["skills_section"] == 0
    assert result.category_scores["experience_section"] == 0
    assert result.category_scores["projects_section"] == 0
    assert result.category_scores["education"] == 0
    assert result.category_scores["certifications"] == 0
    assert result.category_scores["resume_completeness"] == 0
    assert result.category_scores["ats_friendly_indicators"] == 0

    # Overall score equals sum of category scores
    assert result.score == sum(result.category_scores.values())


    # Verify that all deductions in issues match (100 - score)
    deduction_matches = [
        int(m.group(1))
        for issue in result.issues
        for m in [re.search(r"-\s*(\d+)\s*points", issue)]
        if m
    ]
    total_deducted = sum(deduction_matches)
    assert total_deducted == (100 - result.score)


def test_contact_information_deductions():
    """Verify detailed point deductions for contact info: name (3), email (4), phone (3)."""
    # 1. Missing phone only
    res_no_phone = StructuredResume(
        name="John Doe",
        email="john.doe@example.com",
    )
    score_res = calculate_ats_score(res_no_phone)
    assert score_res.category_scores["contact_information"] == 7
    assert any("Missing phone number (-3 points)" in issue for issue in score_res.issues)

    # 2. Invalid email format
    res_bad_email = StructuredResume(
        name="John Doe",
        email="invalid-email-address",
        phone="1234567890"
    )
    score_res_bad_email = calculate_ats_score(res_bad_email)
    assert score_res_bad_email.category_scores["contact_information"] == 8
    assert any("Invalid email format (-2 points)" in issue for issue in score_res_bad_email.issues)


def test_skills_thresholds():
    """Verify deterministic skill brackets: 10+ (20), 7-9 (16), 4-6 (10), 1-3 (5), 0 (0)."""
    # 10 skills
    r10 = StructuredResume(skills=[f"Skill {i}" for i in range(10)])
    assert calculate_ats_score(r10).category_scores["skills_section"] == 20

    # 8 skills
    r8 = StructuredResume(skills=[f"Skill {i}" for i in range(8)])
    s8 = calculate_ats_score(r8)
    assert s8.category_scores["skills_section"] == 16
    assert any("Moderate skills list (-4 points)" in issue for issue in s8.issues)

    # 5 skills
    r5 = StructuredResume(skills=[f"Skill {i}" for i in range(5)])
    s5 = calculate_ats_score(r5)
    assert s5.category_scores["skills_section"] == 10
    assert any("Too few skills (-10 points)" in issue for issue in s5.issues)

    # 2 skills
    r2 = StructuredResume(skills=[f"Skill {i}" for i in range(2)])
    s2 = calculate_ats_score(r2)
    assert s2.category_scores["skills_section"] == 5
    assert any("Critically low skill count (-15 points)" in issue for issue in s2.issues)

    # 0 skills
    r0 = StructuredResume(skills=[])
    s0 = calculate_ats_score(r0)
    assert s0.category_scores["skills_section"] == 0
    assert any("Missing skills section (-20 points)" in issue for issue in s0.issues)


def test_experience_checks():
    """Verify action verbs and measurable results in experience."""
    # Experience without action verbs or metrics
    passive_exp = StructuredResume(
        experience=[
            ExperienceItem(
                company="Acme Corp",
                role="Software Developer",
                start_date="2020",
                end_date="2022",
                responsibilities=[
                    "Responsible for general bug fixes in the web application.",
                    "Attended weekly engineering meetings."
                ]
            )
        ]
    )
    res = calculate_ats_score(passive_exp)
    assert any("Lack of action-oriented language in experience (-3 points)" in issue for issue in res.issues)
    assert any("Missing measurable achievements (-3 points)" in issue for issue in res.issues)

    # Experience with action verbs and metrics
    active_exp = StructuredResume(
        experience=[
            ExperienceItem(
                company="Acme Corp",
                role="Software Developer",
                start_date="2020",
                end_date="2022",
                responsibilities=[
                    "Engineered optimized database queries improving response time by 40%.",
                    "Spearheaded redesign of checkout service handling 25k daily transactions."
                ]
            )
        ]
    )
    res_active = calculate_ats_score(active_exp)
    assert not any("Lack of action-oriented language in experience" in issue for issue in res_active.issues)
    assert not any("Missing measurable achievements" in issue for issue in res_active.issues)
    assert res_active.category_scores["experience_section"] == 20


def test_projects_checks():
    """Verify project tech stack, description, and link validation."""
    # Projects missing tech and links
    proj_sparse = StructuredResume(
        projects=[
            ProjectItem(
                name="Chatbot",
                description="Built an interactive assistant."
            )
        ]
    )
    res = calculate_ats_score(proj_sparse)
    assert any("Missing technologies in projects (-4 points)" in issue for issue in res.issues)
    assert any("Missing project links (-2 points)" in issue for issue in res.issues)



def test_certifications_checks():
    """Verify certifications with and without issuer."""
    # Cert with issuer -> 5 pts
    c1 = StructuredResume(
        certifications=[CertificationItem(name="CKA", issuer="Linux Foundation")]
    )
    assert calculate_ats_score(c1).category_scores["certifications"] == 5

    # Cert without issuer -> 3 pts (-2 points)
    c2 = StructuredResume(
        certifications=[CertificationItem(name="CKA")]
    )
    res_c2 = calculate_ats_score(c2)
    assert res_c2.category_scores["certifications"] == 3
    assert any("Missing certification issuer (-2 points)" in issue for issue in res_c2.issues)


def test_excessive_special_characters_check():
    """Verify detection of unparseable/decorative symbols."""
    resume_with_symbols = StructuredResume(
        name="John Doe",
        skills=["Python 🚀", "FastAPI ★", "Docker ⚡", "SQL ✔", "AWS ❄"]
    )
    res = calculate_ats_score(resume_with_symbols)
    assert any("Excessive special characters or symbols (-2 points)" in issue for issue in res.issues)


def test_api_endpoint_ats_score_direct_payload():
    """Test POST /resume/ats-score endpoint with direct structured resume data."""
    payload = {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "phone": "555-987-6543",
        "location": "New York, NY",
        "skills": ["Python", "FastAPI", "Docker", "SQL", "Pandas", "NumPy", "Git", "Redis", "Linux", "AWS"],
        "education": [
            {
                "institution": "MIT",
                "degree": "B.S.",
                "field_of_study": "Computer Science",
                "start_date": "2019",
                "end_date": "2023"
            }
        ],
        "experience": [
            {
                "company": "DataCorp",
                "role": "Data Engineer",
                "start_date": "2023",
                "end_date": "Present",
                "responsibilities": [
                    "Engineered ETL pipelines processing 10M daily events with 99.9% uptime.",
                    "Optimized SQL queries reducing average latency by 35%."
                ]
            }
        ],
        "projects": [
            {
                "name": "Stream Processing Engine",
                "description": "Architected real-time stream processing platform with sub-second latency.",
                "technologies": ["Python", "Kafka", "Docker"],
                "link": "https://github.com/janedoe/stream-engine"
            }
        ],
        "certifications": [
            {
                "name": "AWS Certified Data Engineer",
                "issuer": "Amazon Web Services"
            }
        ],
        "links": [
            {
                "platform": "GitHub",
                "url": "https://github.com/janedoe"
            }
        ]
    }

    response = client.post("/resume/ats-score", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "score" in data
    assert "category_scores" in data
    assert "strengths" in data
    assert "issues" in data
    assert "recommendations" in data

    assert data["score"] == 100
    assert sum(data["category_scores"].values()) == data["score"]


def test_api_endpoint_ats_score_wrapped_payload():
    """Test POST /resume/ats-score endpoint with wrapped {'resume': {...}} payload."""
    payload = {
        "resume": {
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "phone": "555-987-6543",
            "skills": ["Python", "FastAPI"]
        }
    }

    response = client.post("/resume/ats-score", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data["score"], int)
    assert 0 <= data["score"] <= 100
    assert sum(data["category_scores"].values()) == data["score"]


def test_existing_endpoints_unbroken():
    """Verify that root, health, and existing endpoints remain functional."""
    root_resp = client.get("/")
    assert root_resp.status_code == 200

    health_resp = client.get("/health")
    assert health_resp.status_code == 200
