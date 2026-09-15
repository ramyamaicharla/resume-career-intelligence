"""Deterministic, rule-based Resume-to-Job-Description Matching Engine.

Compares a candidate's structured resume against a target Job Description (JD)
using keyword extraction, alias normalization, and gap-oriented recommendations
without calling any LLMs or external APIs.
"""
import re
from dataclasses import dataclass
from typing import Dict, List, Pattern, Set, Tuple
from app.models.resume import StructuredResume
from app.models.job_match import JobMatchResponse


@dataclass(frozen=True)
class KeywordItem:
    """Represents a cataloged technical skill or domain keyword."""
    canonical: str
    category: str  # "languages", "frameworks", "databases", "cloud", "tools", "domain"
    is_skill: bool  # True for hard technical skills/tools/cloud/db/languages; False for domain/role concepts
    pattern: Pattern[str]


# ---------------------------------------------------------------------------
# Curated Taxonomy of Technical Skills and Domain Keywords
# ---------------------------------------------------------------------------
RAW_KEYWORD_DEFINITIONS: List[Tuple[str, str, bool, str]] = [
    # 1. Programming Languages
    ("Python", "languages", True, r"\bpython\b"),
    ("JavaScript", "languages", True, r"\b(?:javascript|ecmascript|es6)\b"),
    ("TypeScript", "languages", True, r"\btypescript\b"),
    ("Java", "languages", True, r"\bjava\b(?!\s*script)"),
    ("C++", "languages", True, r"\b(?:c\+\+|cpp)\b"),
    ("C#", "languages", True, r"\b(?:c#|csharp|c\s*sharp)\b"),
    ("Go", "languages", True, r"\b(?:golang|go\s+language|go\s+lang)\b|\bgo(?=\s*(?:/|,|\band\b)\s*(?:python|rust|java|c\+\+|node|typescript|backend|cloud))\b"),
    ("Rust", "languages", True, r"\brust\b"),
    ("Ruby", "languages", True, r"\bruby\b"),
    ("PHP", "languages", True, r"\bphp\b"),
    ("Swift", "languages", True, r"\bswift\b"),
    ("Kotlin", "languages", True, r"\bkotlin\b"),
    ("Scala", "languages", True, r"\bscala\b"),
    ("R", "languages", True, r"\b(?:r\s+language|r\s+programming|r-project)\b|\br(?=\s*(?:/|,)\s*(?:python|sql|sas|matlab|spss))\b"),
    ("SQL", "languages", True, r"\bsql\b"),
    ("HTML", "languages", True, r"\bhtml5?\b"),
    ("CSS", "languages", True, r"(?<!tailwind\s)\bcss3?\b"),
    ("Bash / Shell", "languages", True, r"\b(?:bash|shell\s+scripting|zsh|powershell)\b"),
    ("Dart", "languages", True, r"\bdart\b"),
    ("Elixir", "languages", True, r"\belixir\b"),

    # 2. Frameworks & Libraries
    ("React", "frameworks", True, r"\breact(?:\.js|js)?\b(?!\s*native)"),
    ("React Native", "frameworks", True, r"\breact\s+native\b"),
    ("Next.js", "frameworks", True, r"\bnext(?:\.js|js)\b"),
    ("Angular", "frameworks", True, r"\bangular(?:\.js|js)?\b"),
    ("Vue.js", "frameworks", True, r"\bvue(?:\.js|js)?\b"),
    ("Node.js", "frameworks", True, r"\bnode(?:\.js|js)\b"),
    ("Express.js", "frameworks", True, r"\bexpress(?:\.js|js)\b"),
    ("NestJS", "frameworks", True, r"\bnest(?:\.js|js)\b"),
    ("Django", "frameworks", True, r"\bdjango\b"),
    ("FastAPI", "frameworks", True, r"\bfastapi\b"),
    ("Flask", "frameworks", True, r"\bflask\b"),
    ("Spring Boot", "frameworks", True, r"\b(?:spring\s+boot|springboot|spring\s+framework)\b"),
    (".NET", "frameworks", True, r"\b(?:\.net(?:\s+core)?|dotnet(?:\s+core)?|asp\.net)\b"),
    ("Ruby on Rails", "frameworks", True, r"\b(?:ruby\s+on\s+rails|rails)\b"),
    ("PyTorch", "frameworks", True, r"\b(?:pytorch|torch)\b"),
    ("TensorFlow", "frameworks", True, r"\b(?:tensorflow|tf)\b"),
    ("Keras", "frameworks", True, r"\bkeras\b"),
    ("Scikit-Learn", "frameworks", True, r"\b(?:scikit-learn|sklearn)\b"),
    ("Pandas", "frameworks", True, r"\bpandas\b"),
    ("NumPy", "frameworks", True, r"\bnumpy\b"),
    ("Tailwind CSS", "frameworks", True, r"\btailwind(?:\s*css)?\b"),
    ("Bootstrap", "frameworks", True, r"\bbootstrap\b"),
    ("Redux", "frameworks", True, r"\bredux(?:\s+toolkit)?\b"),
    ("GraphQL", "frameworks", True, r"\bgraphql\b"),
    ("jQuery", "frameworks", True, r"\bjquery\b"),
    ("Svelte", "frameworks", True, r"\b(?:svelte|sveltekit)\b"),
    ("Celery", "frameworks", True, r"\bcelery\b"),

    # 3. Databases & Caching
    ("PostgreSQL", "databases", True, r"\b(?:postgresql|postgres|psql)\b"),
    ("MySQL", "databases", True, r"\bmysql\b"),
    ("MongoDB", "databases", True, r"\b(?:mongodb|mongo)\b"),
    ("Redis", "databases", True, r"\bredis\b"),
    ("Cassandra", "databases", True, r"\bcassandra\b"),
    ("SQLite", "databases", True, r"\bsqlite3?\b"),
    ("DynamoDB", "databases", True, r"\bdynamodb\b"),
    ("Oracle", "databases", True, r"\boracle(?:\s+db|\s+database|\s+sql)?\b"),
    ("Elasticsearch", "databases", True, r"\b(?:elasticsearch|elastic\s+search)\b"),
    ("Neo4j", "databases", True, r"\bneo4j\b"),
    ("Snowflake", "databases", True, r"\bsnowflake\b"),
    ("BigQuery", "databases", True, r"\bbigquery\b"),
    ("MariaDB", "databases", True, r"\bmariadb\b"),
    ("Firebase", "databases", True, r"\b(?:firebase|firestore)\b"),
    ("Supabase", "databases", True, r"\bsupabase\b"),
    ("Microsoft SQL Server", "databases", True, r"\b(?:mssql|sql\s+server|microsoft\s+sql\s+server)\b"),

    # 4. Cloud Technologies & Infrastructure
    ("AWS", "cloud", True, r"\b(?:aws|amazon\s+web\s+services)\b"),
    ("Azure", "cloud", True, r"\b(?:azure|microsoft\s+azure)\b"),
    ("GCP", "cloud", True, r"\b(?:gcp|google\s+cloud(?:\s+platform)?)\b"),
    ("Terraform", "cloud", True, r"\bterraform\b"),
    ("CloudFormation", "cloud", True, r"\bcloudformation\b"),
    ("Serverless", "cloud", True, r"\bserverless\b"),
    ("AWS Lambda", "cloud", True, r"\b(?:aws\s+lambda|lambda\s+functions?)\b"),
    ("Docker", "cloud", True, r"\b(?:docker|containerization|containers)\b"),
    ("Kubernetes", "cloud", True, r"\b(?:kubernetes|k8s)\b"),
    ("ECS", "cloud", True, r"\b(?:amazon\s+ecs|aws\s+ecs)\b"),
    ("EKS", "cloud", True, r"\b(?:amazon\s+eks|aws\s+eks)\b"),
    ("Cloudflare", "cloud", True, r"\bcloudflare\b"),
    ("Heroku", "cloud", True, r"\bheroku\b"),
    ("OpenShift", "cloud", True, r"\bopenshift\b"),

    # 5. Tools, DevOps & Message Brokers
    ("Git", "tools", True, r"\bgit\b(?!\s*(?:hub|lab))"),
    ("GitHub", "tools", True, r"\bgithub\b"),
    ("GitLab", "tools", True, r"\bgitlab\b"),
    ("Jenkins", "tools", True, r"\bjenkins\b"),
    ("CI/CD", "tools", True, r"\b(?:ci\s*[/\\-]?\s*cd|continuous\s+integration|continuous\s+deployment)\b"),
    ("Linux", "tools", True, r"\b(?:linux|unix|ubuntu|debian|centos|redhat)\b"),
    ("Postman", "tools", True, r"\bpostman\b"),
    ("Ansible", "tools", True, r"\bansible\b"),
    ("Prometheus", "tools", True, r"\bprometheus\b"),
    ("Grafana", "tools", True, r"\bgrafana\b"),
    ("Datadog", "tools", True, r"\bdatadog\b"),
    ("Webpack", "tools", True, r"\bwebpack\b"),
    ("Vite", "tools", True, r"\bvite\b"),
    ("Kafka", "tools", True, r"\b(?:kafka|apache\s+kafka)\b"),
    ("RabbitMQ", "tools", True, r"\brabbitmq\b"),
    ("Airflow", "tools", True, r"\b(?:airflow|apache\s+airflow)\b"),
    ("Nginx", "tools", True, r"\bnginx\b"),
    ("Jira", "tools", True, r"\bjira\b"),

    # 6. Role, Architecture & Domain Keywords
    ("REST APIs", "domain", False, r"\b(?:rest(?:ful)?\s*apis?|restful)\b"),
    ("Microservices", "domain", False, r"\bmicro[\s-]?services?\b"),
    ("Agile", "domain", False, r"\bagile\b"),
    ("Scrum", "domain", False, r"\bscrum\b"),
    ("DevOps", "domain", False, r"\bdev[\s-]?ops\b"),
    ("System Design", "domain", False, r"\bsystem(?:s)?\s+design\b"),
    ("Distributed Systems", "domain", False, r"\bdistributed\s+systems?\b"),
    ("High Availability", "domain", False, r"\bhigh\s+availability\b"),
    ("Scalability", "domain", False, r"\bscalab(?:ility|le)\b"),
    ("Unit Testing", "domain", False, r"\bunit\s+test(?:ing|s)?\b"),
    ("Integration Testing", "domain", False, r"\bintegration\s+test(?:ing|s)?\b"),
    ("TDD", "domain", False, r"\b(?:tdd|test[\s-]driven\s+development)\b"),
    ("Object-Oriented Programming", "domain", False, r"\b(?:oop|object[\s-]oriented\s+programming)\b"),
    ("Machine Learning", "domain", False, r"\bmachine\s+learning\b"),
    ("Deep Learning", "domain", True, r"\bdeep\s+learning\b"),
    ("NLP", "domain", False, r"\b(?:natural\s+language\s+processing|\bnlp\b)\b"),
    ("Computer Vision", "domain", False, r"\bcomputer\s+vision\b"),
    ("Data Engineering", "domain", False, r"\bdata\s+engineering\b"),
    ("ETL", "domain", False, r"\b(?:etl|extract[\s-]transform[\s-]load)\b"),
    ("Data Modeling", "domain", False, r"\bdata\s+model(?:ing|ling)\b"),
    ("Cybersecurity", "domain", False, r"\b(?:cybersecurity|information\s+security|appsec|application\s+security)\b"),
    ("OAuth / JWT", "domain", False, r"\b(?:oauth2?|jwt|json\s+web\s+tokens?|sso|single\s+sign[\s-]on)\b"),
    ("WebSockets", "domain", False, r"\bwebsockets?\b"),
]

# Compile catalog into KeywordItem objects
KEYWORD_CATALOG: List[KeywordItem] = [
    KeywordItem(
        canonical=name,
        category=category,
        is_skill=is_skill,
        pattern=re.compile(regex_str, re.IGNORECASE),
    )
    for name, category, is_skill, regex_str in RAW_KEYWORD_DEFINITIONS
]


def _build_resume_text_corpus(resume: StructuredResume) -> str:
    """Aggregate all text segments from a structured resume into a single searchable corpus."""
    corpus_parts: List[str] = []

    # Explicit skills
    if resume.skills:
        corpus_parts.extend(resume.skills)

    # Work experience
    for exp in resume.experience:
        if exp.role:
            corpus_parts.append(exp.role)
        if exp.company:
            corpus_parts.append(exp.company)
        corpus_parts.extend(exp.responsibilities)

    # Projects
    for proj in resume.projects:
        if proj.name:
            corpus_parts.append(proj.name)
        if proj.description:
            corpus_parts.append(proj.description)
        corpus_parts.extend(proj.technologies)

    # Certifications
    for cert in resume.certifications:
        if cert.name:
            corpus_parts.append(cert.name)
        if cert.issuer:
            corpus_parts.append(cert.issuer)

    # Education
    for edu in resume.education:
        if edu.degree:
            corpus_parts.append(edu.degree)
        if edu.field_of_study:
            corpus_parts.append(edu.field_of_study)
        if edu.institution:
            corpus_parts.append(edu.institution)

    return " \n ".join(corpus_parts)


def _get_normalized_candidate_skill_tokens(resume: StructuredResume) -> Set[str]:
    """Extract normalized skill tokens explicitly declared in resume skills or project technologies."""
    tokens: Set[str] = set()
    for s in resume.skills:
        if s and s.strip():
            tokens.add(s.strip().lower())
    for proj in resume.projects:
        for tech in proj.technologies:
            if tech and tech.strip():
                tokens.add(tech.strip().lower())
    return tokens


def _keyword_matches_resume(
    keyword: KeywordItem,
    resume_corpus: str,
    normalized_skills: Set[str],
) -> bool:
    """Determine whether a cataloged keyword item is present in candidate resume data."""
    # 1. Direct match in explicitly declared skills (case-insensitive)
    if keyword.canonical.lower() in normalized_skills:
        return True

    # 2. Check if regex pattern matches anywhere in the resume text corpus
    if keyword.pattern.search(resume_corpus):
        return True

    return False


def _extract_jd_keywords(
    job_description: str,
    resume: StructuredResume,
) -> Tuple[List[KeywordItem], Dict[str, str]]:
    """Scan Job Description and identify all requested cataloged keywords, plus any custom resume skills present in JD.

    Returns:
        A tuple of (detected_catalog_keywords, custom_skill_names_in_jd).
    """
    detected_catalog: List[KeywordItem] = []
    catalog_canonicals: Set[str] = set()

    # 1. Scan catalog items against the job description
    for item in KEYWORD_CATALOG:
        if item.pattern.search(job_description):
            detected_catalog.append(item)
            catalog_canonicals.add(item.canonical.lower())

    # 2. Check for dynamic resume skills present in JD that might not be in the catalog
    custom_skills_matched: Dict[str, str] = {}
    for raw_skill in resume.skills:
        skill_clean = raw_skill.strip()
        if not skill_clean or len(skill_clean) < 2:
            continue
        skill_lower = skill_clean.lower()
        if skill_lower in catalog_canonicals:
            continue
        # Check if the dynamic skill appears as a distinct word in JD
        dynamic_pattern = re.compile(rf"\b{re.escape(skill_clean)}\b", re.IGNORECASE)
        if dynamic_pattern.search(job_description):
            custom_skills_matched[skill_lower] = skill_clean

    return detected_catalog, custom_skills_matched


def _generate_recommendations(
    missing_skills: List[str],
    missing_keywords: List[str],
    matched_skills: List[str],
    overall_match_percentage: int,
    total_detected: int,
) -> List[str]:
    """Produce actionable recommendations strictly based on detected gaps ('not found in resume')."""
    recommendations: List[str] = []

    # Case 1: Job description contains no recognizable keywords
    if total_detected == 0:
        recommendations.append(
            "The provided job description did not contain recognizable technical skills or domain keywords. "
            "Please provide a more detailed job description containing role requirements and qualifications to calculate an accurate match."
        )
        return recommendations

    # Case 2: Full 100% match
    if overall_match_percentage == 100 or (not missing_skills and not missing_keywords):
        recommendations.append(
            "Strong alignment detected: Your resume covers all key technical skills and domain keywords identified in the target job description."
        )
        if matched_skills:
            sample_matched = ", ".join(matched_skills[:4])
            recommendations.append(
                f"Ensure that key competencies such as {sample_matched} are supported by quantifiable achievements and impact metrics in your experience bullet points."
            )
        return recommendations

    # Case 3: Missing Technical Skills
    if missing_skills:
        sample_missing_skills = missing_skills[:5]
        skills_str = ", ".join(sample_missing_skills)
        recommendations.append(
            f"The job description highlights key technical skills ({skills_str}) that were not found in your resume. "
            f"If you have hands-on experience with these technologies, consider adding them explicitly to your skills section."
        )
        if len(missing_skills) > 5:
            remaining_skills = ", ".join(missing_skills[5:10])
            recommendations.append(
                f"Additional technical skills requested in the role but not found in your resume include: {remaining_skills}. "
                f"If applicable, highlight relevant academic coursework, certifications, or personal projects utilizing them."
            )

    # Case 4: Missing Domain / Architecture / Methodology Keywords
    # Separate domain keywords from skills
    missing_domain_keywords = [kw for kw in missing_keywords if kw not in missing_skills]
    if missing_domain_keywords:
        sample_domain = ", ".join(missing_domain_keywords[:4])
        recommendations.append(
            f"Role and methodology keywords ({sample_domain}) were emphasized in the job description but not found in your resume. "
            f"If you have applied these practices in prior roles or projects, incorporate them into your responsibilities and summary."
        )

    # General gap advisory - explicitly emphasizes "not found in resume" without inventing skills
    recommendations.append(
        "All missing items listed above are categorized as 'not found in resume'. "
        "Review each missing keyword to determine where you have authentic experience, and incorporate truthful mentions into your resume to improve keyword alignment."
    )

    return recommendations


def match_resume_to_job(resume: StructuredResume, job_description: str) -> JobMatchResponse:
    """Compare a candidate's structured resume against a target job description deterministically.

    Calculates:
      - overall_match_percentage
      - matched_keywords
      - missing_keywords
      - matched_skills
      - missing_skills
      - recommendations

    Does NOT use LLMs/Gemini. Follows deterministic rule-based matching with canonical normalization.
    """
    if not job_description or not job_description.strip():
        return JobMatchResponse(
            overall_match_percentage=0,
            matched_keywords=[],
            missing_keywords=[],
            matched_skills=[],
            missing_skills=[],
            recommendations=[
                "Target job description is empty. Please provide the job description text to perform matching."
            ],
        )

    # 1. Build resume text corpus and extract normalized skills
    resume_corpus = _build_resume_text_corpus(resume)
    normalized_candidate_skills = _get_normalized_candidate_skill_tokens(resume)

    # 2. Extract keywords from Job Description
    detected_catalog_items, custom_skills_in_jd = _extract_jd_keywords(job_description, resume)

    matched_keywords_set: Set[str] = set()
    missing_keywords_set: Set[str] = set()
    matched_skills_set: Set[str] = set()
    missing_skills_set: Set[str] = set()

    # 3. Process cataloged keywords detected in JD
    for item in detected_catalog_items:
        is_matched = _keyword_matches_resume(item, resume_corpus, normalized_candidate_skills)

        if is_matched:
            matched_keywords_set.add(item.canonical)
            if item.is_skill:
                matched_skills_set.add(item.canonical)
        else:
            missing_keywords_set.add(item.canonical)
            if item.is_skill:
                missing_skills_set.add(item.canonical)

    # 4. Process custom candidate skills that were detected in the JD
    for skill_lower, skill_canonical in custom_skills_in_jd.items():
        matched_keywords_set.add(skill_canonical)
        matched_skills_set.add(skill_canonical)

    total_detected_keywords = len(matched_keywords_set) + len(missing_keywords_set)

    # 5. Compute overall match percentage deterministically
    if total_detected_keywords > 0:
        overall_match_percentage = round((len(matched_keywords_set) / total_detected_keywords) * 100)
    else:
        overall_match_percentage = 0

    # 6. Sort results alphabetically for consistency and determinism
    matched_keywords = sorted(list(matched_keywords_set), key=lambda x: x.lower())
    missing_keywords = sorted(list(missing_keywords_set), key=lambda x: x.lower())
    matched_skills = sorted(list(matched_skills_set), key=lambda x: x.lower())
    missing_skills = sorted(list(missing_skills_set), key=lambda x: x.lower())

    # 7. Generate gap-focused recommendations
    recommendations = _generate_recommendations(
        missing_skills=missing_skills,
        missing_keywords=missing_keywords,
        matched_skills=matched_skills,
        overall_match_percentage=overall_match_percentage,
        total_detected=total_detected_keywords,
    )

    return JobMatchResponse(
        overall_match_percentage=overall_match_percentage,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        recommendations=recommendations,
    )
