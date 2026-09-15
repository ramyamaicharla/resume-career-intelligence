from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import router as chat_router
from app.routes.resume import router as resume_router
from app.routes.learning_resources import router as learning_resources_router
from app.routes.project_recommendation import router as project_recommendation_router
from app.routes.interview_prep import router as interview_prep_router


app = FastAPI(
    title="Career Building Platform API",
    description="Backend API for the Career Building Platform",
    version="0.1.0",
)

# Enable CORS for local development (Next.js default port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(chat_router)
app.include_router(resume_router)
app.include_router(learning_resources_router)
app.include_router(project_recommendation_router)
app.include_router(interview_prep_router)


@app.get("/")
def read_root():
    return {
        "message": "Career Building Platform backend is running",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }

