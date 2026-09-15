"use client";

import { useState } from "react";

type InterviewPreparationResult = {
    target_role: string;
    questions: {
        question: string;
        question_type: string;
        difficulty: string;
    }[];
};

type ResumeAnalysis = {
    name?: string;
    email?: string;
    phone?: string;
    location?: string;
    skills?: string[];
    education?: unknown[];
    experience?: unknown[];
    projects?: unknown[];
    certifications?: unknown[];
    links?: unknown[];
};

type ATSScore = {
    score: number;
    category_scores?: Record<string, number>;
    strengths?: string[];
    issues?: string[];
    recommendations?: string[];
};

type JobMatchResult = {
    overall_match_percentage?: number;
    matched_keywords?: string[];
    missing_keywords?: string[];
    matched_skills?: string[];
    missing_skills?: string[];
    recommendations?: string[];
};

type SkillGapResult = {
    matched_skills?: string[];
    missing_skills?: string[];
    skill_gap_percentage?: number;
    recommendations?: string[];
};

type CareerRoadmapSkill = {
    skill?: string;
    priority?: string;
    reason?: string;
};

type CareerRoadmapPhase = {
    phase?: number;
    skill?: string;
    level?: string;
    goal?: string;
};

type CareerRoadmapResult = {
    target_role?: string;
    current_skills?: string[];
    missing_skills?: string[];
    roadmap?: CareerRoadmapSkill[];
    phases?: CareerRoadmapPhase[];
    recommendations?: string[];
};

type LearningResource = {
    title?: string;
    description?: string;
    resource_type?: string;
    url?: string;
};

type LearningResourcesResult = {
    skill?: string;
    resources?: LearningResource[];
};

type ProjectRecommendation = {
    skill?: string;
    title?: string;
    project_title?: string;
    description?: string;
    skills?: string[];
    portfolio_value?: string;
};

type ProjectRecommendationsResult = {
    skill?: string;
    projects?: ProjectRecommendation[];
    recommendations?: ProjectRecommendation[];
};

export default function ResumePage() {
    const [file, setFile] = useState<File | null>(null);
    const [message, setMessage] = useState("");

    const [resumeText, setResumeText] = useState("");
    const [analysis, setAnalysis] =
        useState<ResumeAnalysis | null>(null);

    const [atsScore, setAtsScore] =
        useState<ATSScore | null>(null);

    const [targetRole, setTargetRole] = useState("");
    const [jobDescription, setJobDescription] = useState("");

    const [jobMatch, setJobMatch] =
        useState<JobMatchResult | null>(null);

    const [skillGap, setSkillGap] =
        useState<SkillGapResult | null>(null);

    const [careerRoadmap, setCareerRoadmap] =
        useState<CareerRoadmapResult | null>(null);

    const [learningResources, setLearningResources] =
        useState<LearningResourcesResult[]>([]);

    const [projectRecommendations, setProjectRecommendations] =
        useState<ProjectRecommendationsResult[]>([]);

    const [interviewPreparation, setInterviewPreparation] =
        useState<InterviewPreparationResult | null>(null);

    async function handleUpload() {
        if (!file) {
            setMessage("Please select a PDF resume.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        try {
            setMessage("Uploading resume...");

            setResumeText("");
            setAnalysis(null);
            setAtsScore(null);
            setJobMatch(null);
            setSkillGap(null);
            setCareerRoadmap(null);
            setLearningResources([]);
            setProjectRecommendations([]);
            setInterviewPreparation(null);

            const response = await fetch(
                "http://127.0.0.1:8000/resume/upload",
                {
                    method: "POST",
                    body: formData,
                }
            );

            if (!response.ok) {
                throw new Error("Upload failed");
            }

            const data = await response.json();

            setResumeText(data.text);

            setMessage(
                `Resume uploaded successfully. Pages: ${data.pages}`
            );
        } catch (error) {
            console.error(error);
            setMessage("Failed to upload resume.");
        }
    }

    async function handleAnalyze() {
        if (!resumeText) {
            setMessage("Please upload your resume first.");
            return;
        }

        try {
            setMessage("Analyzing resume...");

            const response = await fetch(
                "http://127.0.0.1:8000/resume/analyze",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        text: resumeText,
                    }),
                }
            );

            if (!response.ok) {
                throw new Error("Resume analysis failed");
            }

            const data = await response.json();

            setAnalysis(data);

            const atsResponse = await fetch(
                "http://127.0.0.1:8000/resume/ats-score",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(data),
                }
            );

            if (!atsResponse.ok) {
                throw new Error("ATS analysis failed");
            }

            const atsData = await atsResponse.json();

            setAtsScore(atsData);

            setMessage("Resume analyzed successfully!");
        } catch (error) {
            console.error(error);
            setMessage("Failed to analyze resume.");
        }
    }

    async function handleJobMatch() {
        if (!analysis) {
            setMessage("Please analyze your resume first.");
            return;
        }

        if (!targetRole.trim()) {
            setMessage("Please enter a target job role.");
            return;
        }

        if (!jobDescription.trim()) {
            setMessage("Please enter a job description.");
            return;
        }

        try {
            setMessage("Matching resume with job...");

            setJobMatch(null);
            setSkillGap(null);
            setCareerRoadmap(null);
            setLearningResources([]);
            setProjectRecommendations([]);
            setInterviewPreparation(null);

            /* --------------------------------
               JOB MATCH
            -------------------------------- */

            const response = await fetch(
                "http://127.0.0.1:8000/resume/job-match",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        resume: analysis,
                        job_description: jobDescription,
                    }),
                }
            );

            if (!response.ok) {
                const errorText = await response.text();

                console.error(
                    "Job Match Backend Error:",
                    errorText
                );

                throw new Error("Job matching failed");
            }

            const data = await response.json();

            console.log(
                "Job Match Result:",
                data
            );

            setJobMatch(data);

            /* --------------------------------
               SKILL GAP ANALYSIS
            -------------------------------- */

            const requiredSkills = [
                ...(data.matched_skills || []),
                ...(data.missing_skills || []),
            ];

            const skillGapResponse = await fetch(
                "http://127.0.0.1:8000/resume/skill-gap",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        resume: analysis,
                        required_skills: requiredSkills,
                    }),
                }
            );

            if (!skillGapResponse.ok) {
                const errorText =
                    await skillGapResponse.text();

                console.error(
                    "Skill Gap Backend Error:",
                    errorText
                );

                throw new Error(
                    "Skill Gap Analysis failed"
                );
            }

            const skillGapData =
                await skillGapResponse.json();

            console.log(
                "Skill Gap Result:",
                skillGapData
            );

            setSkillGap(skillGapData);

            /* --------------------------------
               CAREER ROADMAP
            -------------------------------- */

            const roadmapResponse = await fetch(
                "http://127.0.0.1:8000/resume/career-roadmap",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        target_role: targetRole,
                        current_skills:
                            skillGapData.matched_skills || [],
                        missing_skills:
                            skillGapData.missing_skills || [],
                    }),
                }
            );

            if (roadmapResponse.ok) {
                const roadmapData =
                    await roadmapResponse.json();

                console.log(
                    "Career Roadmap Result:",
                    roadmapData
                );

                setCareerRoadmap(roadmapData);
            } else {
                console.warn(
                    "Career Roadmap request failed."
                );
            }

            /* --------------------------------
               LEARNING RESOURCES
            -------------------------------- */

            const missingSkills =
                skillGapData.missing_skills || [];

            const resourceResults:
                LearningResourcesResult[] = [];

            for (const skill of missingSkills) {
                try {
                    const resourceResponse = await fetch(
                        `http://127.0.0.1:8000/learning/resources?skill=${encodeURIComponent(
                            skill
                        )}`
                    );

                    if (resourceResponse.ok) {
                        const resourceData =
                            await resourceResponse.json();

                        resourceResults.push(
                            resourceData
                        );
                    }
                } catch (resourceError) {
                    console.warn(
                        `Learning resource request failed for ${skill}:`,
                        resourceError
                    );
                }
            }

            setLearningResources(
                resourceResults
            );

            /* --------------------------------
               PROJECT RECOMMENDATIONS
            -------------------------------- */

            const projectResults:
                ProjectRecommendationsResult[] = [];

            for (const skill of missingSkills) {
                try {
                    const projectResponse = await fetch(
                        `http://127.0.0.1:8000/projects/recommendations?skill=${encodeURIComponent(
                            skill
                        )}`
                    );

                    if (projectResponse.ok) {
                        const projectData =
                            await projectResponse.json();

                        projectResults.push(
                            projectData
                        );
                    }
                } catch (projectError) {
                    console.warn(
                        `Project recommendation request failed for ${skill}:`,
                        projectError
                    );
                }
            }

            setProjectRecommendations(
                projectResults
            );

            /* --------------------------------
               PERSONALIZED INTERVIEW PREPARATION
            -------------------------------- */

            try {
                const interviewResponse =
                    await fetch(
                        "http://127.0.0.1:8000/interview/questions",
                        {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json",
                            },
                            body: JSON.stringify({
                                target_role: targetRole,
                                resume: analysis,
                                job_description: jobDescription,
                            }),
                        }
                    );

                if (interviewResponse.ok) {
                    const interviewData =
                        await interviewResponse.json();

                    console.log(
                        "Personalized Interview Preparation Result:",
                        interviewData
                    );

                    setInterviewPreparation(
                        interviewData
                    );
                } else {
                    const errorText =
                        await interviewResponse.text();

                    console.error(
                        "Interview Preparation Backend Error:",
                        errorText
                    );

                    setInterviewPreparation(null);
                }
            } catch (interviewError) {
                console.error(
                    "Interview Preparation request failed:",
                    interviewError
                );

                setInterviewPreparation(null);
            }

            localStorage.setItem(
                "career_assistant_context",
                JSON.stringify({
                    resume: analysis,
                    target_role: targetRole,
                    job_description: jobDescription,
                })
            );

            setMessage(
                "Job Match, Skill Gap, Career Roadmap, Learning Resources, Project Recommendations and Interview Preparation completed successfully!"
            );
        } catch (error) {
            console.error(error);

            setMessage(
                "Failed to complete Job Match / Skill Gap Analysis."
            );
        }
    }

    return (
        <main className="min-h-screen bg-slate-950 px-6 py-16 text-white">

            <div className="mx-auto max-w-5xl">

                {/* HEADER */}

                <div className="text-center">

                    <h1 className="text-4xl font-bold">
                        Resume Intelligence
                    </h1>

                    <p className="mx-auto mt-4 max-w-2xl text-slate-400">
                        Analyze your resume, check ATS compatibility,
                        match your profile with your target job,
                        identify your skill gaps,
                        and prepare for interviews.
                    </p>

                </div>

                {/* UPLOAD RESUME */}

                <div className="mt-10 rounded-2xl border border-slate-800 bg-slate-900 p-8">

                    <h2 className="text-2xl font-semibold">
                        Upload Resume
                    </h2>

                    <p className="mt-2 text-sm text-slate-400">
                        Upload your resume in PDF format.
                    </p>

                    <input
                        type="file"
                        accept=".pdf"
                        onChange={(event) =>
                            setFile(
                                event.target.files?.[0] || null
                            )
                        }
                        className="mt-6 block w-full rounded-lg border border-slate-700 bg-slate-950 p-3 text-sm text-slate-300"
                    />

                    <div className="mt-6 flex flex-col gap-4 sm:flex-row">

                        <button
                            type="button"
                            onClick={handleUpload}
                            className="rounded-lg bg-blue-500 px-6 py-3 font-semibold transition hover:bg-blue-600"
                        >
                            Upload Resume
                        </button>

                        <button
                            type="button"
                            onClick={handleAnalyze}
                            disabled={!resumeText}
                            className="rounded-lg bg-green-500 px-6 py-3 font-semibold transition hover:bg-green-600 disabled:cursor-not-allowed disabled:opacity-40"
                        >
                            Analyze Resume
                        </button>

                    </div>

                    {message && (
                        <div className="mt-5 rounded-lg border border-slate-700 bg-slate-950 p-4">

                            <p className="text-sm text-slate-300">
                                {message}
                            </p>

                        </div>
                    )}

                </div>

                {/* ATS SCORE */}

                {atsScore && (

                    <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-8">

                        <h2 className="text-2xl font-semibold">
                            ATS Compatibility Score
                        </h2>

                        <div className="mt-6 flex flex-col items-center gap-6 sm:flex-row">

                            <div className="flex h-32 w-32 items-center justify-center rounded-full border-8 border-blue-500">

                                <span className="text-4xl font-bold">
                                    {atsScore.score}
                                </span>

                            </div>

                            <div>

                                <p className="text-xl font-semibold">

                                    {atsScore.score >= 80
                                        ? "Strong Resume"
                                        : atsScore.score >= 60
                                            ? "Needs Improvement"
                                            : "Needs Major Improvement"}

                                </p>

                                <p className="mt-2 text-sm text-slate-400">
                                    Compatibility score based on resume
                                    structure and content.
                                </p>

                            </div>

                        </div>

                        {/* ATS ISSUES */}

                        {atsScore.issues &&
                            atsScore.issues.length > 0 && (

                                <div className="mt-8">

                                    <h3 className="text-lg font-semibold">
                                        Areas to Improve
                                    </h3>

                                    <ul className="mt-4 space-y-3">

                                        {atsScore.issues.map(
                                            (issue, index) => (

                                                <li
                                                    key={index}
                                                    className="rounded-lg border border-slate-800 bg-slate-950 p-4 text-sm text-slate-300"
                                                >
                                                    {issue}
                                                </li>

                                            )
                                        )}

                                    </ul>

                                </div>
                            )}

                        {/* ATS RECOMMENDATIONS */}

                        {atsScore.recommendations &&
                            atsScore.recommendations.length > 0 && (

                                <div className="mt-8">

                                    <h3 className="text-lg font-semibold">
                                        Recommendations
                                    </h3>

                                    <ul className="mt-4 space-y-3">

                                        {atsScore.recommendations.map(
                                            (recommendation, index) => (

                                                <li
                                                    key={index}
                                                    className="rounded-lg border border-slate-800 bg-slate-950 p-4 text-sm text-slate-300"
                                                >
                                                    {recommendation}
                                                </li>

                                            )
                                        )}

                                    </ul>

                                </div>
                            )}

                    </div>
                )}

                {/* TARGET JOB */}

                <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-8">

                    <h2 className="text-2xl font-semibold">
                        Target Job
                    </h2>

                    <p className="mt-2 text-sm text-slate-400">
                        Enter the job role and paste the job description
                        to compare it with your resume.
                    </p>

                    <label className="mt-6 block text-sm font-medium text-slate-300">
                        Target Job Role
                    </label>

                    <input
                        type="text"
                        value={targetRole}
                        onChange={(event) =>
                            setTargetRole(event.target.value)
                        }
                        placeholder="Example: Machine Learning Engineer"
                        className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 p-3 text-sm text-white outline-none focus:border-blue-500"
                    />

                    <label className="mt-6 block text-sm font-medium text-slate-300">
                        Job Description
                    </label>

                    <textarea
                        value={jobDescription}
                        onChange={(event) =>
                            setJobDescription(event.target.value)
                        }
                        placeholder="Paste the complete job description here..."
                        rows={10}
                        className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 p-3 text-sm text-white outline-none focus:border-purple-500"
                    />

                    <button
                        type="button"
                        onClick={handleJobMatch}
                        disabled={!analysis}
                        className="mt-6 rounded-lg bg-purple-500 px-6 py-3 font-semibold transition hover:bg-purple-600 disabled:cursor-not-allowed disabled:opacity-40"
                    >
                        Match Resume With Job
                    </button>

                </div>

                {/* JOB MATCH RESULT */}

                {jobMatch && (

                    <div className="mt-8 rounded-2xl border border-purple-500/30 bg-slate-900 p-8">

                        <h2 className="text-2xl font-semibold">
                            Job Match Analysis
                        </h2>

                        <div className="mt-6 flex flex-col items-center gap-6 sm:flex-row">

                            <div className="flex h-32 w-32 items-center justify-center rounded-full border-8 border-purple-500">

                                <span className="text-4xl font-bold">
                                    {jobMatch.overall_match_percentage ?? 0}%
                                </span>

                            </div>

                            <div>

                                <p className="text-xl font-semibold">
                                    {targetRole}
                                </p>

                                <p className="mt-2 text-sm text-slate-400">
                                    Resume compatibility with the
                                    selected job description.
                                </p>

                            </div>

                        </div>

                        {/* MATCHED KEYWORDS */}

                        <div className="mt-8">

                            <h3 className="text-lg font-semibold">
                                Matched Keywords
                            </h3>

                            {jobMatch.matched_keywords &&
                                jobMatch.matched_keywords.length > 0 ? (

                                <div className="mt-4 flex flex-wrap gap-2">

                                    {jobMatch.matched_keywords.map(
                                        (keyword, index) => (

                                            <span
                                                key={`${keyword}-${index}`}
                                                className="rounded-full bg-green-500/10 px-3 py-1 text-sm text-green-300"
                                            >
                                                {keyword}
                                            </span>

                                        )
                                    )}

                                </div>

                            ) : (

                                <p className="mt-3 text-sm text-slate-400">
                                    No matched keywords found.
                                </p>

                            )}

                        </div>

                        {/* MISSING KEYWORDS */}

                        <div className="mt-8">

                            <h3 className="text-lg font-semibold">
                                Missing Keywords
                            </h3>

                            {jobMatch.missing_keywords &&
                                jobMatch.missing_keywords.length > 0 ? (

                                <div className="mt-4 flex flex-wrap gap-2">

                                    {jobMatch.missing_keywords.map(
                                        (keyword, index) => (

                                            <span
                                                key={`${keyword}-${index}`}
                                                className="rounded-full bg-red-500/10 px-3 py-1 text-sm text-red-300"
                                            >
                                                {keyword}
                                            </span>

                                        )
                                    )}

                                </div>

                            ) : (

                                <p className="mt-3 text-sm text-green-400">
                                    No major missing keywords detected.
                                </p>

                            )}

                        </div>

                        {/* MATCHED TECHNICAL SKILLS */}

                        {jobMatch.matched_skills &&
                            jobMatch.matched_skills.length > 0 && (

                                <div className="mt-8">

                                    <h3 className="text-lg font-semibold">
                                        Matched Technical Skills
                                    </h3>

                                    <div className="mt-4 flex flex-wrap gap-2">

                                        {jobMatch.matched_skills.map(
                                            (skill, index) => (

                                                <span
                                                    key={`${skill}-${index}`}
                                                    className="rounded-full bg-blue-500/10 px-3 py-1 text-sm text-blue-300"
                                                >
                                                    {skill}
                                                </span>

                                            )
                                        )}

                                    </div>

                                </div>
                            )}

                        {/* MISSING TECHNICAL SKILLS */}

                        {jobMatch.missing_skills &&
                            jobMatch.missing_skills.length > 0 && (

                                <div className="mt-8">

                                    <h3 className="text-lg font-semibold">
                                        Missing Technical Skills
                                    </h3>

                                    <div className="mt-4 flex flex-wrap gap-2">

                                        {jobMatch.missing_skills.map(
                                            (skill, index) => (

                                                <span
                                                    key={`${skill}-${index}`}
                                                    className="rounded-full bg-orange-500/10 px-3 py-1 text-sm text-orange-300"
                                                >
                                                    {skill}
                                                </span>

                                            )
                                        )}

                                    </div>

                                </div>
                            )}

                        {/* JOB MATCH RECOMMENDATIONS */}

                        {jobMatch.recommendations &&
                            jobMatch.recommendations.length > 0 && (

                                <div className="mt-8">

                                    <h3 className="text-lg font-semibold">
                                        Job Match Recommendations
                                    </h3>

                                    <ul className="mt-4 space-y-3">

                                        {jobMatch.recommendations.map(
                                            (recommendation, index) => (

                                                <li
                                                    key={index}
                                                    className="rounded-lg border border-slate-800 bg-slate-950 p-4 text-sm text-slate-300"
                                                >
                                                    {recommendation}
                                                </li>

                                            )
                                        )}

                                    </ul>

                                </div>
                            )}

                    </div>
                )}

                {/* SKILL GAP ANALYSIS */}

                {skillGap && (

                    <div className="mt-8 rounded-2xl border border-cyan-500/30 bg-slate-900 p-8">

                        <h2 className="text-2xl font-semibold">
                            Skill Gap Analysis
                        </h2>

                        <p className="mt-2 text-sm text-slate-400">
                            Comparison of your current skills against
                            the skills identified from the target job.
                        </p>

                        <div className="mt-6 flex flex-col items-center gap-6 sm:flex-row">

                            <div className="flex h-32 w-32 items-center justify-center rounded-full border-8 border-cyan-500">

                                <span className="text-3xl font-bold">
                                    {skillGap.skill_gap_percentage ?? 0}%
                                </span>

                            </div>

                            <div>

                                <p className="text-xl font-semibold">
                                    Skill Gap
                                </p>

                                <p className="mt-2 text-sm text-slate-400">
                                    Percentage of required skills that
                                    are currently missing from your resume.
                                </p>

                            </div>

                        </div>

                        {/* MATCHED SKILLS */}

                        <div className="mt-8">

                            <h3 className="text-lg font-semibold">
                                Matched Skills
                            </h3>

                            {skillGap.matched_skills &&
                                skillGap.matched_skills.length > 0 ? (

                                <div className="mt-4 flex flex-wrap gap-2">

                                    {skillGap.matched_skills.map(
                                        (skill, index) => (

                                            <span
                                                key={`${skill}-${index}`}
                                                className="rounded-full bg-green-500/10 px-3 py-1 text-sm text-green-300"
                                            >
                                                ✓ {skill}
                                            </span>

                                        )
                                    )}

                                </div>

                            ) : (

                                <p className="mt-3 text-sm text-slate-400">
                                    No matched skills found.
                                </p>

                            )}

                        </div>

                        {/* MISSING SKILLS */}

                        <div className="mt-8">

                            <h3 className="text-lg font-semibold">
                                Missing Skills
                            </h3>

                            {skillGap.missing_skills &&
                                skillGap.missing_skills.length > 0 ? (

                                <div className="mt-4 flex flex-wrap gap-2">

                                    {skillGap.missing_skills.map(
                                        (skill, index) => (

                                            <span
                                                key={`${skill}-${index}`}
                                                className="rounded-full bg-red-500/10 px-3 py-1 text-sm text-red-300"
                                            >
                                                ✗ {skill}
                                            </span>

                                        )
                                    )}

                                </div>

                            ) : (

                                <p className="mt-3 text-sm text-green-400">
                                    No skill gaps detected.
                                </p>

                            )}

                        </div>

                        {/* SKILL GAP RECOMMENDATIONS */}

                        {skillGap.recommendations &&
                            skillGap.recommendations.length > 0 && (

                                <div className="mt-8">

                                    <h3 className="text-lg font-semibold">
                                        Skill Gap Recommendations
                                    </h3>

                                    <ul className="mt-4 space-y-3">

                                        {skillGap.recommendations.map(
                                            (recommendation, index) => (

                                                <li
                                                    key={index}
                                                    className="rounded-lg border border-slate-800 bg-slate-950 p-4 text-sm text-slate-300"
                                                >
                                                    {recommendation}
                                                </li>

                                            )
                                        )}

                                    </ul>

                                </div>
                            )}

                    </div>
                )}

                {/* CAREER ROADMAP */}

                {careerRoadmap && (

                    <div className="mt-8 rounded-2xl border border-emerald-500/30 bg-slate-900 p-8">

                        <h2 className="text-2xl font-semibold">
                            Personalized Career Roadmap
                        </h2>

                        <p className="mt-2 text-sm text-slate-400">
                            A practical roadmap based on your target role
                            and identified skill gaps.
                        </p>

                        {careerRoadmap.target_role && (

                            <div className="mt-6 rounded-lg border border-slate-800 bg-slate-950 p-4">

                                <p className="text-sm text-slate-500">
                                    Target Role
                                </p>

                                <p className="mt-1 text-lg font-semibold">
                                    {careerRoadmap.target_role}
                                </p>

                            </div>
                        )}

                        {careerRoadmap.current_skills &&
                            careerRoadmap.current_skills.length > 0 && (

                                <div className="mt-8">

                                    <h3 className="text-lg font-semibold">
                                        Current Skills
                                    </h3>

                                    <div className="mt-4 flex flex-wrap gap-2">

                                        {careerRoadmap.current_skills.map(
                                            (skill, index) => (

                                                <span
                                                    key={`${skill}-${index}`}
                                                    className="rounded-full bg-green-500/10 px-3 py-1 text-sm text-green-300"
                                                >
                                                    ✓ {skill}
                                                </span>

                                            )
                                        )}

                                    </div>

                                </div>
                            )}

                        {careerRoadmap.missing_skills &&
                            careerRoadmap.missing_skills.length > 0 && (

                                <div className="mt-8">

                                    <h3 className="text-lg font-semibold">
                                        Skills to Learn
                                    </h3>

                                    <div className="mt-4 flex flex-wrap gap-2">

                                        {careerRoadmap.missing_skills.map(
                                            (skill, index) => (

                                                <span
                                                    key={`${skill}-${index}`}
                                                    className="rounded-full bg-orange-500/10 px-3 py-1 text-sm text-orange-300"
                                                >
                                                    {skill}
                                                </span>

                                            )
                                        )}

                                    </div>

                                </div>
                            )}

                        {careerRoadmap.roadmap &&
                            careerRoadmap.roadmap.length > 0 && (

                                <div className="mt-8">

                                    <h3 className="text-lg font-semibold">
                                        Prioritized Skills
                                    </h3>

                                    <div className="mt-4 space-y-4">

                                        {careerRoadmap.roadmap.map(
                                            (item, index) => (

                                                <div
                                                    key={`${item.skill}-${index}`}
                                                    className="rounded-lg border border-slate-800 bg-slate-950 p-5"
                                                >

                                                    <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">

                                                        <h4 className="font-semibold">
                                                            {item.skill}
                                                        </h4>

                                                        <span className="rounded-full bg-blue-500/10 px-3 py-1 text-xs font-medium text-blue-300">
                                                            {item.priority || "Medium"} Priority
                                                        </span>

                                                    </div>

                                                    {item.reason && (

                                                        <p className="mt-2 text-sm leading-6 text-slate-400">
                                                            {item.reason}
                                                        </p>

                                                    )}

                                                </div>
                                            )
                                        )}

                                    </div>

                                </div>
                            )}

                        {careerRoadmap.phases &&
                            careerRoadmap.phases.length > 0 && (

                                <div className="mt-8">

                                    <h3 className="text-lg font-semibold">
                                        Learning Phases
                                    </h3>

                                    <div className="mt-4 space-y-4">

                                        {careerRoadmap.phases.map(
                                            (phase, index) => (

                                                <div
                                                    key={`${phase.phase}-${phase.skill}-${index}`}
                                                    className="rounded-lg border border-slate-800 bg-slate-950 p-5"
                                                >

                                                    <p className="text-sm font-medium text-emerald-300">
                                                        Phase {phase.phase ?? index + 1}
                                                    </p>

                                                    <h4 className="mt-2 text-lg font-semibold">
                                                        {phase.skill}
                                                    </h4>

                                                    {phase.level && (

                                                        <p className="mt-1 text-sm text-blue-300">
                                                            Level: {phase.level}
                                                        </p>

                                                    )}

                                                    {phase.goal && (

                                                        <p className="mt-3 text-sm leading-6 text-slate-400">
                                                            {phase.goal}
                                                        </p>

                                                    )}

                                                </div>
                                            )
                                        )}

                                    </div>

                                </div>
                            )}

                        {careerRoadmap.recommendations &&
                            careerRoadmap.recommendations.length > 0 && (

                                <div className="mt-8">

                                    <h3 className="text-lg font-semibold">
                                        Roadmap Recommendations
                                    </h3>

                                    <ul className="mt-4 space-y-3">

                                        {careerRoadmap.recommendations.map(
                                            (recommendation, index) => (

                                                <li
                                                    key={index}
                                                    className="rounded-lg border border-slate-800 bg-slate-950 p-4 text-sm text-slate-300"
                                                >
                                                    {recommendation}
                                                </li>

                                            )
                                        )}

                                    </ul>

                                </div>
                            )}

                    </div>
                )}

                {/* LEARNING RESOURCES */}

                {skillGap && (

                    <div className="mt-8 rounded-2xl border border-blue-500/30 bg-slate-900 p-8">

                        <h2 className="text-2xl font-semibold">
                            Learning Resources
                        </h2>

                        <p className="mt-2 text-sm text-slate-400">
                            Curated learning resources for the skills
                            identified as missing from your resume.
                        </p>

                        {skillGap.missing_skills &&
                            skillGap.missing_skills.length > 0 ? (

                            <div className="mt-6 space-y-6">

                                {skillGap.missing_skills.map(
                                    (skill, index) => {

                                        const result =
                                            learningResources.find(
                                                (item) =>
                                                    item.skill?.toLowerCase() ===
                                                    skill.toLowerCase()
                                            );

                                        const resources =
                                            result?.resources || [];

                                        return (

                                            <div
                                                key={`${skill}-${index}`}
                                                className="rounded-lg border border-slate-800 bg-slate-950 p-5"
                                            >

                                                <h3 className="text-lg font-semibold">
                                                    {skill}
                                                </h3>

                                                {resources.length > 0 ? (

                                                    <div className="mt-4 space-y-3">

                                                        {resources.map(
                                                            (
                                                                resource,
                                                                resourceIndex
                                                            ) => (

                                                                <div
                                                                    key={`${resource.title}-${resourceIndex}`}
                                                                    className="rounded-lg border border-slate-800 bg-slate-900 p-4"
                                                                >

                                                                    <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">

                                                                        <div>

                                                                            <h4 className="font-medium">
                                                                                {resource.title ||
                                                                                    "Learning Resource"}
                                                                            </h4>

                                                                            {resource.resource_type && (

                                                                                <p className="mt-1 text-xs text-blue-300">
                                                                                    {resource.resource_type}
                                                                                </p>

                                                                            )}

                                                                        </div>

                                                                        {resource.url && (

                                                                            <a
                                                                                href={resource.url}
                                                                                target="_blank"
                                                                                rel="noopener noreferrer"
                                                                                className="shrink-0 rounded-lg bg-blue-500 px-4 py-2 text-center text-sm font-medium text-white transition hover:bg-blue-600"
                                                                            >
                                                                                Open Resource
                                                                            </a>

                                                                        )}

                                                                    </div>

                                                                    {resource.description && (

                                                                        <p className="mt-3 text-sm leading-6 text-slate-400">
                                                                            {resource.description}
                                                                        </p>

                                                                    )}

                                                                </div>

                                                            )
                                                        )}

                                                    </div>

                                                ) : (

                                                    <p className="mt-3 text-sm text-slate-400">
                                                        No curated resource is currently available for this skill.
                                                    </p>

                                                )}

                                            </div>
                                        );
                                    }
                                )}

                            </div>

                        ) : (

                            <p className="mt-6 text-sm text-green-400">
                                No missing skills were identified.
                            </p>

                        )}

                    </div>
                )}

                {/* PROJECT RECOMMENDATIONS */}

                {skillGap && (

                    <div className="mt-8 rounded-2xl border border-emerald-500/30 bg-slate-900 p-8">

                        <h2 className="text-2xl font-semibold">
                            Project Recommendations
                        </h2>

                        <p className="mt-2 text-sm text-slate-400">
                            Practical portfolio projects you can build
                            to close your missing-skill gaps.
                        </p>

                        {skillGap.missing_skills &&
                            skillGap.missing_skills.length > 0 ? (

                            <div className="mt-6 space-y-6">

                                {skillGap.missing_skills.map(
                                    (skill, index) => {

                                        const result =
                                            projectRecommendations.find(
                                                (item) =>
                                                    item.skill?.toLowerCase() ===
                                                    skill.toLowerCase()
                                            );

                                        const projects =
                                            result?.projects ||
                                            result?.recommendations ||
                                            [];

                                        return (

                                            <div
                                                key={`${skill}-${index}`}
                                                className="rounded-lg border border-slate-800 bg-slate-950 p-5"
                                            >

                                                <h3 className="text-lg font-semibold">
                                                    {skill}
                                                </h3>

                                                {projects.length > 0 ? (

                                                    <div className="mt-4 grid gap-4">

                                                        {projects.map(
                                                            (
                                                                project,
                                                                projectIndex
                                                            ) => (

                                                                <div
                                                                    key={`${project.title || project.project_title || "project"}-${projectIndex}`}
                                                                    className="rounded-lg border border-slate-800 bg-slate-900 p-5"
                                                                >

                                                                    <h4 className="text-lg font-medium">
                                                                        {project.title ||
                                                                            project.project_title ||
                                                                            "Portfolio Project"}
                                                                    </h4>

                                                                    {project.description && (

                                                                        <p className="mt-2 text-sm leading-6 text-slate-400">
                                                                            {project.description}
                                                                        </p>

                                                                    )}

                                                                    {project.skills &&
                                                                        project.skills.length > 0 && (

                                                                            <div className="mt-4 flex flex-wrap gap-2">

                                                                                {project.skills.map(
                                                                                    (
                                                                                        projectSkill,
                                                                                        skillIndex
                                                                                    ) => (

                                                                                        <span
                                                                                            key={`${projectSkill}-${skillIndex}`}
                                                                                            className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1 text-xs text-slate-300"
                                                                                        >
                                                                                            {projectSkill}
                                                                                        </span>

                                                                                    )
                                                                                )}

                                                                            </div>

                                                                        )}

                                                                    {project.portfolio_value && (

                                                                        <p className="mt-4 text-sm text-emerald-300">
                                                                            Portfolio Value: {project.portfolio_value}
                                                                        </p>

                                                                    )}

                                                                </div>

                                                            )
                                                        )}

                                                    </div>

                                                ) : (

                                                    <p className="mt-4 text-sm text-slate-500">
                                                        No curated project recommendation is available for this skill yet.
                                                    </p>

                                                )}

                                            </div>
                                        );
                                    }
                                )}

                            </div>

                        ) : (

                            <p className="mt-6 text-sm text-slate-500">
                                No missing skills were identified,
                                so project recommendations are not needed yet.
                            </p>

                        )}

                    </div>
                )}

                {/* INTERVIEW PREPARATION */}

                {interviewPreparation && (

                    <div className="mt-8 rounded-2xl border border-violet-500/30 bg-slate-900 p-8">

                        <h2 className="text-2xl font-semibold">
                            Interview Preparation
                        </h2>

                        <p className="mt-2 text-sm text-slate-400">
                            Personalized interview questions generated
                            from your resume, target role, and job description.
                        </p>

                        {/* TARGET ROLE */}

                        <div className="mt-6 rounded-lg border border-slate-800 bg-slate-950 p-4">

                            <p className="text-sm text-slate-500">
                                Target Role
                            </p>

                            <p className="mt-1 text-lg font-semibold">
                                {interviewPreparation.target_role}
                            </p>

                        </div>

                        {/* QUESTIONS */}

                        {interviewPreparation.questions &&
                            interviewPreparation.questions.length > 0 ? (

                            <div className="mt-6 space-y-4">

                                {interviewPreparation.questions.map(
                                    (item, index) => (

                                        <div
                                            key={`${item.question}-${index}`}
                                            className="rounded-xl border border-slate-800 bg-slate-950 p-5"
                                        >

                                            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">

                                                <span className="text-sm font-medium text-violet-300">
                                                    Question {index + 1}
                                                </span>

                                                <div className="flex flex-wrap gap-2">

                                                    <span className="rounded-full bg-blue-500/10 px-3 py-1 text-xs text-blue-300">
                                                        {item.question_type}
                                                    </span>

                                                    <span className="rounded-full bg-orange-500/10 px-3 py-1 text-xs text-orange-300">
                                                        {item.difficulty}
                                                    </span>

                                                </div>

                                            </div>

                                            <p className="mt-4 text-base leading-7 text-slate-200">
                                                {item.question}
                                            </p>

                                        </div>

                                    )
                                )}

                            </div>

                        ) : (

                            <p className="mt-6 text-sm text-slate-400">
                                No personalized interview questions
                                were generated for this target role.
                            </p>

                        )}

                    </div>
                )}

                {/* RESUME PROFILE */}

                {analysis && (

                    <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-8">

                        <h2 className="text-2xl font-semibold">
                            Resume Profile
                        </h2>

                        <div className="mt-6 space-y-6">

                            {/* NAME */}

                            <div>

                                <p className="text-sm text-slate-500">
                                    Name
                                </p>

                                <p className="mt-1 text-lg">
                                    {analysis.name ||
                                        "Not found"}
                                </p>

                            </div>

                            {/* EMAIL */}

                            <div>

                                <p className="text-sm text-slate-500">
                                    Email
                                </p>

                                <p className="mt-1">
                                    {analysis.email ||
                                        "Not found"}
                                </p>

                            </div>

                            {/* PHONE */}

                            <div>

                                <p className="text-sm text-slate-500">
                                    Phone
                                </p>

                                <p className="mt-1">
                                    {analysis.phone ||
                                        "Not found"}
                                </p>

                            </div>

                            {/* LOCATION */}

                            <div>

                                <p className="text-sm text-slate-500">
                                    Location
                                </p>

                                <p className="mt-1">
                                    {analysis.location ||
                                        "Not found"}
                                </p>

                            </div>

                            {/* SKILLS */}

                            <div>

                                <p className="text-sm text-slate-500">
                                    Skills
                                </p>

                                <div className="mt-3 flex flex-wrap gap-2">

                                    {analysis.skills &&
                                        analysis.skills.length > 0 ? (

                                        analysis.skills.map(
                                            (skill, index) => (

                                                <span
                                                    key={`${skill}-${index}`}
                                                    className="rounded-full bg-blue-500/10 px-3 py-1 text-sm text-blue-300"
                                                >
                                                    {skill}
                                                </span>

                                            )
                                        )

                                    ) : (

                                        <p className="text-sm text-slate-400">
                                            No skills found
                                        </p>

                                    )}

                                </div>

                            </div>

                        </div>

                    </div>
                )}

            </div>

        </main>
    );
}