"""Deterministic, rule-based ATS Compatibility Scorer.

Calculates a transparent, deterministic ATS Compatibility Score (0 to 100)
for structured resume data without using Gemini or any LLM.
"""
import re
from typing import Dict, List, Set, Tuple
from app.models.resume import StructuredResume
from app.models.ats import ATSScoreResponse

# Curated list of strong action verbs commonly sought by ATS and technical recruiters
ACTION_VERBS: Set[str] = {
    "accelerated", "accomplished", "achieved", "acquired", "acted", "adapted",
    "administered", "advanced", "advised", "allocated", "analyzed", "appraised",
    "architected", "assembled", "assessed", "assigned", "assisted", "attained",
    "audited", "augmented", "authored", "automated", "benchmarked", "boosted",
    "budgeted", "built", "calculated", "calibrated", "centralized", "championed",
    "co-founded", "collaborated", "compiled", "composed", "computed", "conceptualized",
    "conducted", "configured", "consolidated", "constructed", "consulted", "contained",
    "contributed", "converted", "coordinated", "crafted", "created", "customized",
    "debugged", "decreased", "defined", "delegated", "delivered", "deployed",
    "designed", "developed", "devised", "diagnosed", "directed", "discovered",
    "distributed", "documented", "doubled", "drafted", "drove", "eliminated",
    "enabled", "enacted", "engineered", "enhanced", "established", "estimated",
    "evaluated", "executed", "expanded", "expedited", "experimented", "explored",
    "facilitated", "finalized", "fine-tuned", "forecasted", "formulated", "founded",
    "generated", "governed", "guided", "halted", "handled", "headed", "identified",
    "implemented", "improved", "increased", "indexed", "initiated", "innovated",
    "inspected", "installed", "instituted", "instructed", "integrated", "interfaced",
    "introduced", "invented", "investigated", "isolated", "launched", "lead",
    "led", "leveraged", "maintained", "managed", "maximized", "mentored",
    "migrated", "minimized", "modeled", "modernized", "monitored", "negotiated",
    "obtained", "operated", "optimized", "orchestrated", "organized", "originated",
    "overhauled", "oversaw", "partnered", "performed", "pioneered", "planned",
    "prepared", "presented", "produced", "programmed", "promoted", "proposed",
    "prototyped", "published", "re-engineered", "rebuilt", "recommended", "reconciled",
    "redesigned", "reduced", "refactored", "refined", "regulated", "remodeled",
    "reorganized", "repaired", "replaced", "researched", "resolved", "restructured",
    "retrieved", "revamped", "reviewed", "revitalized", "routed", "scaled",
    "scheduled", "secured", "selected", "separated", "simplified", "simulated",
    "solved", "spearheaded", "standardized", "streamlined", "strengthened", "structured",
    "supervised", "supported", "surpassed", "synthesized", "systematized", "tested",
    "tracked", "trained", "transformed", "transitioned", "translated", "troubleshot",
    "unified", "upgraded", "utilized", "validated", "verified", "yielded"
}

# Regex patterns for measurable achievements
MEASURABLE_PATTERNS = [
    re.compile(r"\b\d+(?:\.\d+)?%\b"),  # e.g., 20%, 99.9%
    re.compile(r"\$\s*\d+(?:,\d{3})*(?:\.\d+)?(?:\s*(?:k|m|b|million|billion))?\b", re.IGNORECASE),  # e.g., $100k, $1.5M
    re.compile(r"\b\d+\s*(?:\+|k|m|b|x)\b", re.IGNORECASE),  # e.g., 10k, 5x, 100+
    re.compile(r"\b(?:reduced|increased|improved|decreased|saved|scaled|boosted|cut|grew)\b.*?\b\d+", re.IGNORECASE),
    re.compile(r"\b\d+\s*(?:users|clients|customers|requests|queries|transactions|records|students|engineers|team members|hours|ms|milliseconds|seconds|minutes|days)\b", re.IGNORECASE),
]

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_DIGITS_REGEX = re.compile(r"\d")
PLACEHOLDER_REGEX = re.compile(r"\b(?:lorem\s+ipsum|tbd|n/a|na|placeholder|xxx|todo|none)\b", re.IGNORECASE)
UNUSUAL_CHARS_REGEX = re.compile(r"[^\x00-\x7F\u2010-\u2015\u2018-\u201F\u2022\u2023\u25E6\u2043\u2219\n\r\t]")


def _score_contact_information(
    resume: StructuredResume
) -> Tuple[int, List[str], List[str], List[str]]:
    """Score Contact Information category (Max 10 points)."""
    score = 0
    strengths: List[str] = []
    issues: List[str] = []
    recommendations: List[str] = []

    # 1. Candidate Name (3 points)
    if resume.name and len(resume.name.strip()) >= 2:
        score += 3
        strengths.append("Full candidate name is clearly stated.")
    else:
        issues.append(
            "Missing candidate name (-3 points): ATS parsers require the candidate's full name to create an applicant profile."
        )
        recommendations.append(
            "Add your full professional name prominently at the top of your resume."
        )

    # 2. Email Address (4 points)
    if resume.email and resume.email.strip():
        email_clean = resume.email.strip()
        if EMAIL_REGEX.match(email_clean):
            score += 4
            strengths.append("Professional and valid email address provided.")
        else:
            score += 2
            issues.append(
                "Invalid email format (-2 points): Provided email does not appear to follow standard email formatting."
            )
            recommendations.append(
                "Format your email address in standard format (e.g. name@example.com)."
            )
    else:
        issues.append(
            "Missing email address (-4 points): ATS systems require a valid email to contact you and track your application."
        )
        recommendations.append(
            "Include an active, professional email address in your contact header."
        )

    # 3. Phone Number (3 points)
    if resume.phone and len(PHONE_DIGITS_REGEX.findall(resume.phone)) >= 7:
        score += 3
        strengths.append("Direct contact phone number provided for recruiter outreach.")
    else:
        issues.append(
            "Missing phone number (-3 points): A contact phone number is needed for recruiter phone screens."
        )
        recommendations.append(
            "Include an active contact phone number with country or area code."
        )

    return score, strengths, issues, recommendations


def _score_skills_section(
    resume: StructuredResume
) -> Tuple[int, List[str], List[str], List[str]]:
    """Score Skills Section category (Max 20 points)."""
    strengths: List[str] = []
    issues: List[str] = []
    recommendations: List[str] = []

    valid_skills = [s.strip() for s in resume.skills if s and s.strip()]
    count = len(valid_skills)

    if count >= 10:
        score = 20
        strengths.append(
            f"Strong skills section with {count} technical and domain competencies."
        )
    elif count >= 7:
        score = 16
        issues.append(
            f"Moderate skills list (-4 points): Found {count} skills. Standard ATS filters typically target 10 or more domain-relevant keywords."
        )
        recommendations.append(
            "Add 3-4 more relevant technical and domain skills to improve ATS keyword matching."
        )
    elif count >= 4:
        score = 10
        issues.append(
            f"Too few skills (-10 points): Found only {count} skills. Resumes with fewer than 7 skills risk being filtered out by automated keyword searches."
        )
        recommendations.append(
            "Expand your skills section with relevant frameworks, tools, languages, and technical concepts (target 10+ skills)."
        )
    elif count >= 1:
        score = 5
        issues.append(
            f"Critically low skill count (-15 points): Detected only {count} skill(s). ATS search algorithms rely heavily on skill keywords."
        )
        recommendations.append(
            "Include a dedicated skills section listing languages, frameworks, developer tools, and domain concepts."
        )
    else:
        score = 0
        issues.append(
            "Missing skills section (-20 points): No skills were identified in the resume. ATS parsers match candidate profiles primarily through skill keywords."
        )
        recommendations.append(
            "Add a prominent 'Technical Skills' section listing your programming languages, tools, frameworks, and domain expertise."
        )

    return score, strengths, issues, recommendations


def _score_experience_section(
    resume: StructuredResume
) -> Tuple[int, List[str], List[str], List[str]]:
    """Score Experience Section category (Max 20 points)."""
    strengths: List[str] = []
    issues: List[str] = []
    recommendations: List[str] = []

    valid_experiences = [exp for exp in resume.experience if exp]
    if not valid_experiences:
        return (
            0,
            [],
            [
                "Missing experience section (-20 points): No professional work experience detected. Work experience is a primary factor in ATS scoring."
            ],
            [
                "Add your work experience, internships, or relevant technical roles detailing your responsibilities and achievements."
            ],
        )

    score = 0

    # 1. Role and Employer specification (6 points max)
    missing_role_or_company = sum(
        1 for exp in valid_experiences
        if not (exp.role and exp.role.strip() and exp.company and exp.company.strip())
    )
    if missing_role_or_company == 0:
        score += 6
        strengths.append(
            "Clear job titles and employer names across all experience entries."
        )
    else:
        pts = max(0, 6 - (missing_role_or_company * 2))
        score += pts
        lost = 6 - pts
        issues.append(
            f"Incomplete job experience entries (-{lost} points): Found {missing_role_or_company} experience entry/entries missing a job title or company name."
        )
        recommendations.append(
            "Ensure every work experience entry clearly states both your job title and employer name."
        )

    # 2. Dates / Timeline (4 points max)
    missing_dates = sum(
        1 for exp in valid_experiences
        if not ((exp.start_date and exp.start_date.strip()) or (exp.end_date and exp.end_date.strip()))
    )
    if missing_dates == 0:
        score += 4
        strengths.append("Employment dates and chronology clearly documented.")
    else:
        pts = max(0, 4 - (missing_dates * 2))
        score += pts
        lost = 4 - pts
        issues.append(
            f"Missing employment dates (-{lost} points): Found {missing_dates} experience entry/entries without dates. ATS systems calculate tenure from dates."
        )
        recommendations.append(
            "Add clear start and end dates (e.g., 'June 2022 - Present' or '2021 - 2023') to each position."
        )

    # 3. Responsibilities provided (4 points max)
    all_bullets = [
        resp.strip()
        for exp in valid_experiences
        for resp in exp.responsibilities
        if resp and resp.strip()
    ]
    total_bullets = len(all_bullets)

    if total_bullets >= 2 * len(valid_experiences) or total_bullets >= 3:
        score += 4
        strengths.append(
            f"Detailed bullet points outlining responsibilities and accomplishments ({total_bullets} total)."
        )
    elif total_bullets >= 1:
        score += 2
        issues.append(
            f"Sparse experience descriptions (-2 points): Found only {total_bullets} bullet point(s) across experiences."
        )
        recommendations.append(
            "Provide at least 3-4 bullet points per role detailing your accomplishments and contributions."
        )
    else:
        issues.append(
            "Empty responsibilities (-4 points): Work experience entries lack descriptive bullet points."
        )
        recommendations.append(
            "Add descriptive bullet points detailing your key tasks and contributions in each role."
        )

    # 4. Action-oriented descriptions (3 points max)
    action_bullets = 0
    for bullet in all_bullets:
        words = re.findall(r"[a-zA-Z]+", bullet.lower())
        if words and any(w in ACTION_VERBS for w in words[:4]):
            action_bullets += 1

    if action_bullets >= 2 or (total_bullets > 0 and (action_bullets / total_bullets) >= 0.4):
        score += 3
        strengths.append(
            "Action-oriented bullet points utilizing strong power verbs in experience."
        )
    else:
        issues.append(
            "Lack of action-oriented language in experience (-3 points): Descriptions rely on passive wording rather than strong action verbs."
        )
        recommendations.append(
            "Begin each bullet point with a strong action verb (e.g., 'Developed', 'Engineered', 'Spearheaded') illustrating direct ownership."
        )

    # 5. Measurable achievements (3 points max)
    metric_bullets = sum(
        1 for bullet in all_bullets
        if any(pattern.search(bullet) for pattern in MEASURABLE_PATTERNS)
    )
    if metric_bullets >= 1:
        score += 3
        strengths.append(
            "Measurable achievements with quantifiable impact detected in work experience."
        )
    else:
        issues.append(
            "Missing measurable achievements (-3 points): Experience entries lack quantifiable metrics (e.g., '% improved', '$ saved', 'X users reached')."
        )
        recommendations.append(
            "Quantify your achievements using metrics, percentages, numbers, or timeframes (e.g., 'Improved pipeline throughput by 35%')."
        )

    return score, strengths, issues, recommendations


def _score_projects_section(
    resume: StructuredResume
) -> Tuple[int, List[str], List[str], List[str]]:
    """Score Projects Section category (Max 15 points)."""
    strengths: List[str] = []
    issues: List[str] = []
    recommendations: List[str] = []

    valid_projects = [p for p in resume.projects if p]
    if not valid_projects:
        return (
            0,
            [],
            [
                "Missing projects section (-15 points): No technical projects found. Projects demonstrate hands-on application of your skills."
            ],
            [
                "Add 2-3 relevant projects showcasing your technical stack, architecture, and problem-solving abilities."
            ],
        )

    score = 0

    # 1. Project Title & Detailed Description (6 points max)
    missing_name_count = sum(
        1 for p in valid_projects if not (p.name and p.name.strip())
    )
    short_desc_count = sum(
        1 for p in valid_projects if not (p.description and len(p.description.strip()) >= 15)
    )

    name_pts = max(0, 3 - (missing_name_count * 2))
    if name_pts < 3:
        lost = 3 - name_pts
        issues.append(
            f"Missing project names (-{lost} points): Found {missing_name_count} project entry/entries without a title."
        )
        recommendations.append("Give each project a distinct, descriptive title.")

    desc_pts = max(0, 3 - (short_desc_count * 2))
    if desc_pts < 3:
        lost = 3 - desc_pts
        issues.append(
            f"Brief or missing project descriptions (-{lost} points): Found {short_desc_count} project(s) with short or missing descriptions."
        )
        recommendations.append(
            "Provide a 1-2 sentence overview for each project explaining its core objective and architecture."
        )

    score += (name_pts + desc_pts)
    if name_pts == 3 and desc_pts == 3:
        strengths.append("Projects have clear titles and detailed descriptions.")

    # 2. Technologies specified (4 points max)
    projects_with_tech = sum(
        1 for p in valid_projects
        if p.technologies and any(t.strip() for t in p.technologies)
    )
    if projects_with_tech == len(valid_projects):
        score += 4
        strengths.append("Tech stacks and tools explicitly specified for projects.")
    elif projects_with_tech > 0:
        score += 2
        issues.append(
            "Incomplete technology tags in projects (-2 points): Some projects do not specify the tech stack used."
        )
        recommendations.append(
            "Explicitly list the languages, frameworks, and tools used for each project (e.g., Python, FastAPI, Docker)."
        )
    else:
        issues.append(
            "Missing technologies in projects (-4 points): Projects do not list the tools or technologies utilized."
        )
        recommendations.append(
            "Specify the key technologies, libraries, and frameworks used in each project."
        )

    # 3. Action-oriented or measurable content in projects (3 points max)
    has_action_or_metric = False
    for p in valid_projects:
        desc = (p.description or "").lower()
        words = set(re.findall(r"[a-zA-Z]+", desc))
        if words.intersection(ACTION_VERBS) or any(pat.search(desc) for pat in MEASURABLE_PATTERNS):
            has_action_or_metric = True
            break

    if has_action_or_metric:
        score += 3
        strengths.append("Project descriptions highlight active development and tangible functionality.")
    else:
        issues.append(
            "Passive project descriptions (-3 points): Project summaries lack action verbs or tangible results."
        )
        recommendations.append(
            "Describe what you built, how you implemented it, and any measurable outcomes achieved."
        )

    # 4. Project Links (2 points max)
    has_project_link = any(p.link and p.link.strip() for p in valid_projects)
    has_code_link = any(
        l.url and any(token in l.url.lower() for token in ["github", "gitlab", "demo", "portfolio"])
        for l in resume.links
    )

    if has_project_link or has_code_link:
        score += 2
        strengths.append("Project repository or live demo links provided.")
    else:
        issues.append(
            "Missing project links (-2 points): No repository (GitHub) or live demo links provided for projects."
        )
        recommendations.append(
            "Include GitHub or live demo links for your projects to verify your code and practical implementation."
        )

    return score, strengths, issues, recommendations


def _score_education_section(
    resume: StructuredResume
) -> Tuple[int, List[str], List[str], List[str]]:
    """Score Education Section category (Max 10 points)."""
    strengths: List[str] = []
    issues: List[str] = []
    recommendations: List[str] = []

    valid_education = [edu for edu in resume.education if edu]
    if not valid_education:
        return (
            0,
            [],
            [
                "Missing education section (-10 points): No academic qualifications or degrees listed. Education is a mandatory screening filter for many ATS systems."
            ],
            [
                "Add your educational background, including your degree, major/field of study, and institution name."
            ],
        )

    score = 0

    # 1. Institution Name (4 points max)
    missing_institution = sum(
        1 for edu in valid_education if not (edu.institution and edu.institution.strip())
    )
    if missing_institution == 0:
        score += 4
        strengths.append("Academic institution clearly identified.")
    else:
        issues.append(
            "Missing institution name (-4 points): Educational entry lacks the name of the college or university."
        )
        recommendations.append("List the full name of the university or college attended.")

    # 2. Degree and Field of Study (4 points max)
    has_both = all(
        (edu.degree and edu.degree.strip()) and (edu.field_of_study and edu.field_of_study.strip())
        for edu in valid_education
    )
    has_any = any(
        (edu.degree and edu.degree.strip()) or (edu.field_of_study and edu.field_of_study.strip())
        for edu in valid_education
    )

    if has_both:
        score += 4
        strengths.append("Degree and field of study clearly documented.")
    elif has_any:
        score += 2
        issues.append(
            "Incomplete degree details (-2 points): Missing either degree level (e.g. Bachelor's) or field of study (e.g. Computer Science)."
        )
        recommendations.append(
            "Specify both your degree qualification and field of study in each education item."
        )
    else:
        issues.append(
            "Missing degree and major (-4 points): Educational entry does not state the degree or field of study."
        )
        recommendations.append("Specify your degree qualification and field of study.")

    # 3. Graduation Date / Enrollment Year (2 points max)
    has_dates = any(
        (edu.start_date and edu.start_date.strip()) or (edu.end_date and edu.end_date.strip())
        for edu in valid_education
    )
    if has_dates:
        score += 2
        strengths.append("Graduation or attendance dates included.")
    else:
        issues.append(
            "Missing graduation date (-2 points): Graduation year or attendance period is missing."
        )
        recommendations.append("Include your graduation year (or expected graduation date).")

    return score, strengths, issues, recommendations


def _score_certifications_section(
    resume: StructuredResume
) -> Tuple[int, List[str], List[str], List[str]]:
    """Score Certifications category (Max 5 points)."""
    strengths: List[str] = []
    issues: List[str] = []
    recommendations: List[str] = []

    valid_certs = [
        c for c in resume.certifications
        if c and (c.name or c.issuer)
    ]

    if not valid_certs:
        return (
            0,
            [],
            [
                "Missing certifications (-5 points): No industry certifications or credentials detected."
            ],
            [
                "Add relevant professional certifications (e.g., AWS Certified, TensorFlow Developer, Google Cloud, Coursera certificates) to validate specialized skills."
            ],
        )

    has_complete = any(
        c.name and c.name.strip() and c.issuer and c.issuer.strip()
        for c in valid_certs
    )
    has_named = any(c.name and c.name.strip() for c in valid_certs)

    if has_complete:
        score = 5
        strengths.append("Professional certifications from recognized issuers detected.")
    elif has_named:
        score = 3
        issues.append(
            "Missing certification issuer (-2 points): Certification entry has a title but lacks the issuing body."
        )
        recommendations.append(
            "Specify the issuing authority for your certifications (e.g., AWS, Coursera, DeepLearning.AI)."
        )
    else:
        score = 0
        issues.append(
            "Empty certification entries (-5 points): Certification items contain no title or credential name."
        )
        recommendations.append("Provide the full credential name and issuing organization.")

    return score, strengths, issues, recommendations


def _score_resume_completeness(
    resume: StructuredResume
) -> Tuple[int, List[str], List[str], List[str]]:
    """Score Resume Completeness category (Max 10 points)."""
    strengths: List[str] = []
    issues: List[str] = []
    recommendations: List[str] = []
    score = 0

    # 1. Core Section Coverage (4 points max: 1 pt each for Contact, Skills, Experience, Education)
    core_checks = [
        ("Contact Information", bool(resume.name and resume.name.strip() and resume.email and resume.email.strip())),
        ("Skills Section", bool(resume.skills and any(s.strip() for s in resume.skills))),
        ("Experience Section", bool(resume.experience and any(exp for exp in resume.experience))),
        ("Education", bool(resume.education and any(edu for edu in resume.education))),
    ]
    present_core = sum(1 for _, is_present in core_checks if is_present)
    score += present_core

    if present_core == 4:
        strengths.append("Comprehensive coverage of all primary resume sections.")
    else:
        for name, is_present in core_checks:
            if not is_present:
                issues.append(
                    f"Missing core section ({name}) (-1 points): High-priority core section is not populated."
                )
                recommendations.append(f"Add the {name} to complete your primary resume profile.")

    # 2. Location specified (2 points max)
    if resume.location and resume.location.strip():
        score += 2
        strengths.append("Geographic location provided for ATS regional matching.")
    else:
        issues.append(
            "Missing location (-2 points): Location (city, state, or 'Remote') helps ATS filters match geographic job requirements."
        )
        recommendations.append(
            "Add your city and state/country or indicate willingness for remote work."
        )

    # 3. Profile links provided (2 points max)
    has_links = bool(resume.links and any(l.url and l.url.strip() for l in resume.links))
    if has_links:
        score += 2
        strengths.append("Professional links (e.g., LinkedIn, GitHub, or portfolio) included.")
    else:
        issues.append(
            "Missing professional links (-2 points): No LinkedIn, GitHub, or portfolio link provided."
        )
        recommendations.append("Add links to your LinkedIn profile and GitHub or personal portfolio.")

    # 4. Content Integrity / No Placeholders & No Empty Sections (2 points max)
    all_text_snippets: List[str] = []
    if resume.name:
        all_text_snippets.append(resume.name)
    if resume.location:
        all_text_snippets.append(resume.location)
    all_text_snippets.extend(resume.skills)
    for exp in resume.experience:
        if exp.company:
            all_text_snippets.append(exp.company)
        if exp.role:
            all_text_snippets.append(exp.role)
        all_text_snippets.extend(exp.responsibilities)
    for proj in resume.projects:
        if proj.name:
            all_text_snippets.append(proj.name)
        if proj.description:
            all_text_snippets.append(proj.description)
        all_text_snippets.extend(proj.technologies)
    for edu in resume.education:
        if edu.institution:
            all_text_snippets.append(edu.institution)
        if edu.degree:
            all_text_snippets.append(edu.degree)
        if edu.field_of_study:
            all_text_snippets.append(edu.field_of_study)

    has_empty_items = (
        any(not any([edu.institution, edu.degree, edu.field_of_study]) for edu in resume.education)
        or any(not any([exp.company, exp.role, exp.responsibilities]) for exp in resume.experience)
        or any(not any([proj.name, proj.description, proj.technologies]) for proj in resume.projects)
        or any(not any([cert.name, cert.issuer]) for cert in resume.certifications)
    )

    if not all_text_snippets:
        issues.append(
            "Empty sections detected (-2 points): Resume contains no text content across sections."
        )
        recommendations.append(
            "Populate resume sections with your background, skills, experience, and education."
        )
    elif has_empty_items or any(PLACEHOLDER_REGEX.search(snip) for snip in all_text_snippets):
        issues.append(
            "Empty or placeholder sections detected (-2 points): Found empty entries or placeholder text (e.g. 'N/A', 'TBD')."
        )
        recommendations.append(
            "Remove placeholder text and ensure all listed items contain complete information."
        )
    else:
        score += 2
        strengths.append("No placeholder text or empty section artifacts detected.")

    return score, strengths, issues, recommendations



def _score_ats_friendly_indicators(
    resume: StructuredResume
) -> Tuple[int, List[str], List[str], List[str]]:
    """Score ATS-friendly Indicators category (Max 10 points)."""
    strengths: List[str] = []
    issues: List[str] = []
    recommendations: List[str] = []
    score = 0

    # 1. Clear Section Headings & Organization (3 points max)
    distinct_sections = 0
    if resume.skills and any(s.strip() for s in resume.skills):
        distinct_sections += 1
    if resume.experience and any(exp for exp in resume.experience):
        distinct_sections += 1
    if resume.education and any(edu for edu in resume.education):
        distinct_sections += 1
    if resume.projects and any(proj for proj in resume.projects):
        distinct_sections += 1

    if distinct_sections >= 3:
        score += 3
        strengths.append("Clear, standardized section structure optimal for ATS parsing.")
    elif distinct_sections >= 2:
        score += 1
        issues.append(
            "Limited section structure (-2 points): Resume has few distinct sections, risking parsing ambiguity."
        )
        recommendations.append(
            "Organize your resume with standard headings: Contact Information, Technical Skills, Professional Experience, Projects, and Education."
        )
    else:
        issues.append(
            "Unclear or fragmented section structure (-3 points): Standard ATS parsers require distinctly defined sections."
        )
        recommendations.append(
            "Organize your resume with standard headings: Contact Information, Technical Skills, Professional Experience, Projects, and Education."
        )

    # Gather all bullet points & descriptions for linguistic checks
    content_snippets: List[str] = []
    for exp in resume.experience:
        content_snippets.extend(exp.responsibilities)
    for proj in resume.projects:
        if proj.description:
            content_snippets.append(proj.description)

    # 2. Action-Oriented Language Across Resume (3 points max)
    action_verbs_found: Set[str] = set()
    for snip in content_snippets:
        words = set(re.findall(r"[a-zA-Z]+", snip.lower()))
        action_verbs_found.update(words.intersection(ACTION_VERBS))

    distinct_verb_count = len(action_verbs_found)
    if distinct_verb_count >= 4:
        score += 3
        strengths.append("Dynamic, action-oriented language used throughout experience and projects.")
    elif distinct_verb_count >= 2:
        score += 2
        issues.append(
            "Limited action verb variety (-1 points): Descriptions rely on a limited set of action verbs."
        )
        recommendations.append(
            "Start responsibility bullets and project descriptions with impactful action verbs like 'Engineered', 'Optimized', and 'Delivered'."
        )
    elif distinct_verb_count == 1:
        score += 1
        issues.append(
            "Sparse action verbs (-2 points): Descriptions rely heavily on passive language rather than active verbs."
        )
        recommendations.append(
            "Start your responsibility bullets and project descriptions with impactful action verbs like 'Engineered', 'Optimized', and 'Delivered'."
        )
    else:
        issues.append(
            "Missing action verbs (-3 points): Descriptions do not use strong action verbs."
        )
        recommendations.append(
            "Revise bullets to start with strong action verbs demonstrating proactive achievements."
        )

    # 3. Measurable Results Where Applicable (2 points max)
    has_metrics = any(
        any(pat.search(snip) for pat in MEASURABLE_PATTERNS)
        for snip in content_snippets
    )
    if has_metrics:
        score += 2
        strengths.append("Quantifiable metrics and measurable outcomes detected.")
    else:
        issues.append(
            "Missing measurable results (-2 points): Resume lacks quantifiable metrics demonstrating the impact of your work."
        )
        recommendations.append(
            "Incorporate specific numbers, percentages, and metrics to prove the scale and effectiveness of your contributions."
        )

    # 4. Clean Text / Avoid Excessive Special Characters (2 points max)
    all_text = " ".join(
        [resume.name or "", resume.location or "", resume.email or "", resume.phone or ""]
        + resume.skills
        + [resp for exp in resume.experience for resp in exp.responsibilities]
        + [proj.description or "" for proj in resume.projects]
    ).strip()

    if not all_text:
        issues.append(
            "Missing text content (-2 points): No parseable text detected to evaluate typography and character encoding."
        )
        recommendations.append(
            "Add standard textual content across your resume sections."
        )
    else:
        unusual_matches = UNUSUAL_CHARS_REGEX.findall(all_text)
        if len(unusual_matches) <= 2:
            score += 2
            strengths.append("Clean text formatting free of excessive special characters or unparseable symbols.")
        else:
            issues.append(
                f"Excessive special characters or symbols (-2 points): Detected {len(unusual_matches)} non-standard decorative or special character(s) that can cause ATS parsing errors."
            )
            recommendations.append(
                "Avoid icons, emojis, or decorative symbols; stick to standard alphanumeric characters and standard bullet points."
            )

    return score, strengths, issues, recommendations



def calculate_ats_score(resume: StructuredResume) -> ATSScoreResponse:
    """Calculate a transparent, deterministic ATS Compatibility Score for a parsed resume.

    Scores 8 categories summing to 100 points:
    - Contact Information: 10 points
    - Skills Section: 20 points
    - Experience Section: 20 points
    - Projects Section: 15 points
    - Education: 10 points
    - Certifications: 5 points
    - Resume Completeness: 10 points
    - ATS-friendly indicators: 10 points

    Args:
        resume: Validated structured resume data.

    Returns:
        ATSScoreResponse: Deterministic score, category breakdowns, strengths,
            issues with point deductions, and actionable recommendations.
    """
    cat_contact, str_contact, iss_contact, rec_contact = _score_contact_information(resume)
    cat_skills, str_skills, iss_skills, rec_skills = _score_skills_section(resume)
    cat_exp, str_exp, iss_exp, rec_exp = _score_experience_section(resume)
    cat_proj, str_proj, iss_proj, rec_proj = _score_projects_section(resume)
    cat_edu, str_edu, iss_edu, rec_edu = _score_education_section(resume)
    cat_cert, str_cert, iss_cert, rec_cert = _score_certifications_section(resume)
    cat_comp, str_comp, iss_comp, rec_comp = _score_resume_completeness(resume)
    cat_ats, str_ats, iss_ats, rec_ats = _score_ats_friendly_indicators(resume)

    category_scores: Dict[str, int] = {
        "contact_information": cat_contact,
        "skills_section": cat_skills,
        "experience_section": cat_exp,
        "projects_section": cat_proj,
        "education": cat_edu,
        "certifications": cat_cert,
        "resume_completeness": cat_comp,
        "ats_friendly_indicators": cat_ats,
    }

    total_score = sum(category_scores.values())
    total_score = max(0, min(100, total_score))

    strengths = (
        str_contact
        + str_skills
        + str_exp
        + str_proj
        + str_edu
        + str_cert
        + str_comp
        + str_ats
    )

    issues = (
        iss_contact
        + iss_skills
        + iss_exp
        + iss_proj
        + iss_edu
        + iss_cert
        + iss_comp
        + iss_ats
    )

    recommendations = (
        rec_contact
        + rec_skills
        + rec_exp
        + rec_proj
        + rec_edu
        + rec_cert
        + rec_comp
        + rec_ats
    )

    return ATSScoreResponse(
        score=total_score,
        category_scores=category_scores,
        strengths=strengths,
        issues=issues,
        recommendations=recommendations,
    )
