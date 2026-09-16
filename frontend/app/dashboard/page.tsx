"use client";

import { useEffect, useState } from "react";

type LearningResource = {
    title: string;
    resource_type: string;
    url: string;
    skill: string;
};

type ProjectRecommendation = {
    title: string;
    description: string;
    skills: string[];
    portfolio_value: string;
};

type CareerRoadmap = {
    target_role?: string;

    roadmap?: {
        skill: string;
        priority: string;
        reason: string;
    }[];

    phases?: {
        phase: number;
        skill: string;
        level: string;
        goal: string;
    }[];

    recommendations?: string[];
};

export default function DashboardPage() {
    const [atsScore, setAtsScore] = useState("--");
    const [jobMatch, setJobMatch] = useState("--");
    const [skillGap, setSkillGap] = useState("--");
    const [missingSkills, setMissingSkills] = useState<string[]>([]);

    const [careerRoadmap, setCareerRoadmap] =
        useState<CareerRoadmap | null>(null);

    const [learningResources, setLearningResources] =
        useState<Record<string, LearningResource[]>>({});

    const [projectRecommendations, setProjectRecommendations] =
        useState<Record<string, ProjectRecommendation[]>>({});

    useEffect(() => {
        const loadDashboardData = async () => {
            const score = localStorage.getItem("ats_score");
            const jobMatchData = localStorage.getItem("job_match");
            const skillGapData = localStorage.getItem("skill_gap");
            const roadmapData = localStorage.getItem("career_roadmap");

            /* --------------------------------
               ATS SCORE
            -------------------------------- */

            if (score) {
                setAtsScore(score);
            }

            /* --------------------------------
               JOB MATCH
            -------------------------------- */

            if (jobMatchData) {
                const data = JSON.parse(jobMatchData);

                setJobMatch(
                    String(
                        data.overall_match_percentage ?? "--"
                    )
                );
            }

            /* --------------------------------
               SKILL GAP
            -------------------------------- */

            if (skillGapData) {
                const data = JSON.parse(skillGapData);

                setSkillGap(
                    String(
                        data.skill_gap_percentage ?? "--"
                    )
                );

                setMissingSkills(
                    data.missing_skills ?? []
                );
            }

            /* --------------------------------
               CAREER ROADMAP
            -------------------------------- */

            if (roadmapData) {
                const data = JSON.parse(roadmapData);

                setCareerRoadmap(data);

                const resourcesBySkill: Record<
                    string,
                    LearningResource[]
                > = {};

                const projectsBySkill: Record<
                    string,
                    ProjectRecommendation[]
                > = {};

                for (const phase of data.phases ?? []) {
                    /* --------------------------------
                       LEARNING RESOURCES
                    -------------------------------- */

                    const resourceResponse = await fetch(
                        `http://127.0.0.1:8000/learning/resources?skill=${encodeURIComponent(
                            phase.skill
                        )}`
                    );

                    if (resourceResponse.ok) {
                        const resourceData =
                            await resourceResponse.json();

                        resourcesBySkill[phase.skill] =
                            resourceData.resources ?? [];
                    }

                    /* --------------------------------
                       PROJECT RECOMMENDATIONS
                    -------------------------------- */

                    const projectResponse = await fetch(
                        `http://127.0.0.1:8000/projects/recommendations?skill=${encodeURIComponent(
                            phase.skill
                        )}`
                    );

                    if (projectResponse.ok) {
                        const projectData =
                            await projectResponse.json();

                        projectsBySkill[phase.skill] =
                            projectData.projects ?? [];
                    }
                }

                setLearningResources(
                    resourcesBySkill
                );

                setProjectRecommendations(
                    projectsBySkill
                );

                console.log(
                    "Learning Resources:",
                    resourcesBySkill
                );

                console.log(
                    "Project Recommendations:",
                    projectsBySkill
                );
            }
        };

        loadDashboardData();
    }, []);

    return (
        <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
            <div className="mx-auto max-w-7xl">

                {/* --------------------------------
                   PAGE HEADER
                -------------------------------- */}

                <h1 className="text-3xl font-bold">
                    Career Intelligence Dashboard
                </h1>

                <p className="mt-2 text-slate-400">
                    Your resume, job match, skill gaps, and career roadmap
                    in one place.
                </p>

                {/* --------------------------------
                   SCORE CARDS
                -------------------------------- */}

                <section className="mt-8 grid gap-6 md:grid-cols-3">

                    {/* ATS */}

                    <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
                        <p className="text-sm text-slate-400">
                            ATS Compatibility
                        </p>

                        <p className="mt-2 text-4xl font-bold">
                            {atsScore}
                        </p>
                    </div>

                    {/* JOB MATCH */}

                    <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
                        <p className="text-sm text-slate-400">
                            Job Match
                        </p>

                        <p className="mt-2 text-4xl font-bold">
                            {jobMatch}%
                        </p>
                    </div>

                    {/* SKILL GAP */}

                    <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
                        <p className="text-sm text-slate-400">
                            Skill Gap
                        </p>

                        <p className="mt-2 text-4xl font-bold">
                            {skillGap}%
                        </p>
                    </div>

                </section>

                {/* --------------------------------
                   MISSING SKILLS + CAREER ROADMAP
                -------------------------------- */}

                <section className="mt-8 grid gap-6 md:grid-cols-2">

                    {/* --------------------------------
                       MISSING SKILLS
                    -------------------------------- */}

                    <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">

                        <h2 className="text-xl font-semibold">
                            Missing Skills
                        </h2>

                        <div className="mt-3 text-slate-400">

                            {missingSkills.length > 0 ? (

                                <ul className="mt-4 space-y-2">

                                    {missingSkills.map(
                                        (skill) => (
                                            <li
                                                key={skill}
                                                className="text-slate-300"
                                            >
                                                • {skill}
                                            </li>
                                        )
                                    )}

                                </ul>

                            ) : (

                                <p className="mt-4 text-slate-400">
                                    No missing skills detected.
                                </p>

                            )}

                        </div>

                    </div>

                    {/* --------------------------------
                       CAREER ROADMAP
                    -------------------------------- */}

                    <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">

                        <h2 className="text-xl font-semibold">
                            Career Roadmap
                        </h2>

                        {careerRoadmap?.phases &&
                            careerRoadmap.phases.length > 0 ? (

                            <div className="mt-4 space-y-4">

                                {careerRoadmap.phases.map(
                                    (phase) => (

                                        <div
                                            key={phase.phase}
                                            className="rounded-lg border border-slate-800 bg-slate-950 p-4"
                                        >

                                            {/* PHASE */}

                                            <p className="text-sm text-slate-400">
                                                Phase {phase.phase}
                                            </p>

                                            {/* SKILL */}

                                            <h3 className="mt-1 font-semibold">
                                                {phase.skill}
                                            </h3>

                                            {/* PRIORITY */}

                                            <p className="mt-1 text-sm text-slate-400">
                                                Priority:{" "}
                                                {careerRoadmap.roadmap?.find(
                                                    (item) =>
                                                        item.skill.toLowerCase() ===
                                                        phase.skill.toLowerCase()
                                                )?.priority ?? "Medium"}
                                            </p>

                                            {/* REASON */}

                                            <p className="mt-2 text-sm text-slate-300">
                                                Reason:{" "}
                                                {careerRoadmap.roadmap?.find(
                                                    (item) =>
                                                        item.skill.toLowerCase() ===
                                                        phase.skill.toLowerCase()
                                                )?.reason ??
                                                    "This skill is relevant to your target role."}
                                            </p>

                                            {/* LEVEL */}

                                            <p className="mt-1 text-sm text-slate-400">
                                                Level: {phase.level}
                                            </p>

                                            {/* GOAL */}

                                            <p className="mt-2 text-sm text-slate-300">
                                                {phase.goal}
                                            </p>

                                        </div>

                                    )
                                )}

                                {/* --------------------------------
                                   ROADMAP RECOMMENDATIONS
                                -------------------------------- */}

                                {careerRoadmap.recommendations &&
                                    careerRoadmap.recommendations.length > 0 && (

                                        <div className="mt-6 border-t border-slate-800 pt-4">

                                            <h3 className="font-semibold">
                                                Recommendations
                                            </h3>

                                            <ul className="mt-3 space-y-2">

                                                {careerRoadmap.recommendations.map(
                                                    (
                                                        recommendation,
                                                        index
                                                    ) => (

                                                        <li
                                                            key={index}
                                                            className="text-sm text-slate-300"
                                                        >
                                                            • {recommendation}
                                                        </li>

                                                    )
                                                )}

                                            </ul>

                                        </div>

                                    )}

                            </div>

                        ) : (

                            <p className="mt-3 text-slate-400">
                                Your personalized roadmap will appear here.
                            </p>

                        )}

                    </div>

                </section>

                {/* --------------------------------
                   LEARNING RESOURCES
                -------------------------------- */}

                <section className="mt-8 rounded-xl border border-slate-800 bg-slate-900 p-6">

                    <h2 className="text-xl font-semibold">
                        Learning Resources
                    </h2>

                    {Object.keys(learningResources).length > 0 ? (

                        <div className="mt-4 space-y-6">

                            {Object.entries(
                                learningResources
                            ).map(
                                ([skill, resources]) => (

                                    <div key={skill}>

                                        <h3 className="font-semibold">
                                            {skill}
                                        </h3>

                                        <div className="mt-2 space-y-2">

                                            {resources.map(
                                                (resource) => (

                                                    <a
                                                        key={resource.url}
                                                        href={resource.url}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="block text-blue-400 hover:underline"
                                                    >
                                                        {resource.title}
                                                    </a>

                                                )
                                            )}

                                        </div>

                                    </div>

                                )
                            )}

                        </div>

                    ) : (

                        <p className="mt-3 text-slate-400">
                            Learning resources will appear here.
                        </p>

                    )}

                </section>

                {/* --------------------------------
                   PROJECT RECOMMENDATIONS
                -------------------------------- */}

                <section className="mt-8 rounded-xl border border-slate-800 bg-slate-900 p-6">

                    <h2 className="text-xl font-semibold">
                        Project Recommendations
                    </h2>

                    {Object.keys(projectRecommendations).length > 0 ? (

                        <div className="mt-4 space-y-6">

                            {Object.entries(
                                projectRecommendations
                            ).map(
                                ([skill, projects]) => (

                                    <div key={skill}>

                                        <h3 className="text-lg font-semibold">
                                            {skill}
                                        </h3>

                                        <div className="mt-3 space-y-4">

                                            {projects.map(
                                                (project) => (

                                                    <div
                                                        key={project.title}
                                                        className="rounded-lg border border-slate-800 bg-slate-950 p-4"
                                                    >

                                                        {/* PROJECT TITLE */}

                                                        <h4 className="font-semibold">
                                                            {project.title}
                                                        </h4>

                                                        {/* DESCRIPTION */}

                                                        <p className="mt-2 text-sm text-slate-300">
                                                            {project.description}
                                                        </p>

                                                        {/* SKILLS */}

                                                        {project.skills &&
                                                            project.skills.length > 0 && (

                                                                <p className="mt-2 text-sm text-slate-400">
                                                                    Skills:{" "}
                                                                    {project.skills.join(
                                                                        ", "
                                                                    )}
                                                                </p>

                                                            )}

                                                        {/* PORTFOLIO VALUE */}

                                                        <p className="mt-2 text-sm text-slate-400">
                                                            Portfolio Value:{" "}
                                                            {project.portfolio_value}
                                                        </p>

                                                    </div>

                                                )
                                            )}

                                        </div>

                                    </div>

                                )
                            )}

                        </div>

                    ) : (

                        <p className="mt-3 text-slate-400">
                            Project recommendations will appear here.
                        </p>

                    )}

                </section>

            </div>
        </main>
    );
}