"""Routes package."""
from app.routes.chat import router as chat_router
from app.routes.resume import router as resume_router

__all__ = ["chat_router", "resume_router"]

