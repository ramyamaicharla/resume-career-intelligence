# CAREER BUILDING PLATFORM

## Project Goal
The **CAREER BUILDING PLATFORM** is an AI-powered career guidance platform designed to empower students and job seekers by:
- Assessing their current skills and technical background.
- Identifying concrete skill gaps against target industry roles.
- Prioritizing what skills to learn first.
- Generating personalized, actionable career roadmaps.

> **Core Product Principle**: Directly answer the user's most critical question:  
> **"What should I do next to reach my target career?"**

---

## Target Roles (Initial Focus)
1. **Data Scientist**
2. **Machine Learning Engineer**
3. **GenAI Engineer**

---

## Initial MVP Scope (Phase 1)
A focused, career-specific AI Career Chatbot:
- **Interaction Flow**:
  $$\text{User} \longrightarrow \text{Next.js Frontend} \longrightarrow \text{FastAPI Backend} \longrightarrow \text{OpenAI API} \longrightarrow \text{Career Assistant Response} \longrightarrow \text{Frontend}$$
- **Persona**: Specialized career advisor equipped to evaluate readiness, recommend targeted next steps, and analyze skill transitions for the target roles.
- **Strictly minimal architecture**: No database, no complex multi-agent frameworks, and no premature dependencies.

---

## Planned Technology Stack
- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **Backend**: Python, FastAPI
- **LLM**: OpenAI API
- **Database & Storage**: PostgreSQL *(Future)*
- **AI/Agent Frameworks**: LangChain, LangGraph *(Future)*
- **Retrieval-Augmented Generation (RAG)**: pgvector *(Future)*
- **Observability & Evaluation**: LangSmith *(Future)*
- **Visualization**: React Flow *(Future)*

---

## Development Phases
1. **Phase 1: Minimal Career Chatbot MVP**  
   Establish the core end-to-end communication channel with a specialized career assistant prompt.
2. **Phase 2: Structured Skill Assessment & Gap Analysis**  
   Implement structured user profiling and gap identification for Data Science, MLE, and GenAI roles.
3. **Phase 3: Industry Knowledge Base & RAG Integration**  
   Incorporate pgvector with curated job market benchmarks, courses, and project recommendations.
4. **Phase 4: Personalized Career Roadmap Visualization**  
   Build dynamic, interactive career roadmaps using React Flow.
5. **Phase 5: Agentic Architecture & Observability**  
   Transition to LangGraph-driven multi-agent workflows and evaluate outputs with LangSmith.
