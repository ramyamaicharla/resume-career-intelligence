"use client";

import { useEffect, useState } from "react";

type CareerContext = {
    resume: Record<string, unknown>;
    target_role: string;
    job_description: string;
};

export default function ChatPage() {
    const [message, setMessage] = useState("");

    const [careerContext, setCareerContext] =
        useState<CareerContext>({
            resume: {},
            target_role: "",
            job_description: "",
        });

    const [response, setResponse] = useState("");
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const savedContext =
            localStorage.getItem(
                "career_assistant_context"
            );

        if (savedContext) {
            try {
                setCareerContext(
                    JSON.parse(savedContext)
                );
            } catch (error) {
                console.error(
                    "Failed to load career context:",
                    error
                );
            }
        }
    }, []);

    async function sendMessage() {
        if (!message.trim()) {
            return;
        }

        setLoading(true);
        setResponse("");

        try {
            const res = await fetch(
                "http://127.0.0.1:8000/chat",
                {
                    method: "POST",
                    headers: {
                        "Content-Type":
                            "application/json",
                    },
                    body: JSON.stringify({
                        message: message,
                        resume: careerContext.resume,
                        target_role:
                            careerContext.target_role,
                        job_description:
                            careerContext.job_description,
                    }),
                }
            );

            const data = await res.json();

            if (res.ok) {
                setResponse(data.response);
            } else {
                setResponse(
                    data.detail ||
                    "Something went wrong."
                );
            }
        } catch (error) {
            console.error(error);

            setResponse(
                "Unable to connect to backend."
            );
        } finally {
            setLoading(false);
        }
    }

    return (
        <main className="min-h-screen bg-slate-950 px-6 py-16 text-white">
            <div className="mx-auto max-w-4xl">

                {/* HEADER */}

                <div className="text-center">

                    <h1 className="text-4xl font-bold">
                        AI Career Assistant
                    </h1>

                    <p className="mt-4 text-slate-400">
                        Get personalized career guidance
                        based on your resume, target role,
                        and job description.
                    </p>

                </div>

                {/* CAREER CONTEXT */}

                <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">

                    <h2 className="text-xl font-semibold">
                        Career Context
                    </h2>

                    <div className="mt-4 space-y-3">

                        <div>
                            <p className="text-sm text-slate-500">
                                Target Role
                            </p>

                            <p className="mt-1 font-medium">
                                {careerContext.target_role ||
                                    "Not selected"}
                            </p>
                        </div>

                        <div>
                            <p className="text-sm text-slate-500">
                                Resume
                            </p>

                            <p className="mt-1 text-sm text-slate-300">
                                {Object.keys(
                                    careerContext.resume
                                ).length > 0
                                    ? "Resume data connected"
                                    : "Resume data not connected"}
                            </p>
                        </div>

                        <div>
                            <p className="text-sm text-slate-500">
                                Job Description
                            </p>

                            <p className="mt-1 text-sm text-slate-300">
                                {careerContext.job_description
                                    ? "Job description connected"
                                    : "Job description not connected"}
                            </p>
                        </div>

                    </div>

                </div>

                {/* CHAT INPUT */}

                <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">

                    <textarea
                        value={message}
                        onChange={(e) =>
                            setMessage(e.target.value)
                        }
                        placeholder="Ask your career question..."
                        className="min-h-32 w-full rounded-xl border border-slate-700 bg-slate-950 p-4 text-white outline-none focus:border-violet-500"
                    />

                    <button
                        onClick={sendMessage}
                        disabled={loading}
                        className="mt-4 rounded-xl bg-violet-600 px-6 py-3 font-semibold hover:bg-violet-500 disabled:opacity-50"
                    >
                        {loading
                            ? "Thinking..."
                            : "Ask Assistant"}
                    </button>

                </div>

                {/* AI RESPONSE */}

                {response && (
                    <div className="mt-8 rounded-2xl border border-violet-500/30 bg-slate-900 p-6">

                        <h2 className="text-xl font-semibold">
                            AI Career Assistant
                        </h2>

                        <p className="mt-4 whitespace-pre-wrap leading-7 text-slate-300">
                            {response}
                        </p>

                    </div>
                )}

            </div>
        </main>
    );
}