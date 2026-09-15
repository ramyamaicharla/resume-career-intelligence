import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      {/* Navigation */}
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6">
        <div className="text-xl font-bold tracking-tight">
          Career<span className="text-blue-400">AI</span>
        </div>

        <button
          type="button"
          className="rounded-lg border border-slate-700 px-5 py-2 text-sm font-medium transition hover:bg-slate-800"
        >
          Sign In
        </button>
      </nav>

      {/* Hero Section */}
      <section className="mx-auto flex max-w-7xl flex-col items-center px-6 pb-20 pt-20 text-center">
        <div className="mb-6 rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-2 text-sm text-blue-300">
          AI-Powered Career Building Platform
        </div>

        <h1 className="max-w-4xl text-5xl font-bold leading-tight tracking-tight sm:text-6xl">
          Build Your Career With
          <span className="block text-blue-400">
            AI-Powered Guidance
          </span>
        </h1>

        <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-400">
          Upload your resume, discover your skill gaps, match your profile
          with target jobs, and get a personalized roadmap to reach your
          career goals.
        </p>

        <div className="mt-10 flex flex-col gap-4 sm:flex-row">
          {/* Analyze My Resume */}
          <Link
            href="/resume"
            className="rounded-lg bg-blue-500 px-7 py-3 font-semibold text-white transition hover:bg-blue-600"
          >
            Analyze My Resume
          </Link>

          {/* Explore Careers */}
          <Link
            href="/resume"
            className="rounded-lg border border-slate-700 px-7 py-3 font-semibold text-slate-200 transition hover:bg-slate-800"
          >
            Explore Careers
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto grid max-w-7xl gap-6 px-6 pb-24 md:grid-cols-3">
        <FeatureCard
          title="Resume Intelligence"
          description="Analyze your resume, check ATS compatibility, and identify areas for improvement."
        />

        <FeatureCard
          title="Skill Gap Analysis"
          description="Compare your current skills with target job requirements and discover what you need to learn."
        />

        <FeatureCard
          title="Personalized Roadmap"
          description="Get a practical career roadmap with learning resources, projects, and interview preparation."
        />
      </section>
    </main>
  );
}

function FeatureCard({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-7 transition hover:border-blue-500/50">
      <h2 className="text-xl font-semibold">{title}</h2>

      <p className="mt-3 leading-7 text-slate-400">
        {description}
      </p>
    </div>
  );
}