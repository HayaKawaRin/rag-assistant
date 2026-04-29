from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.tools import router as tools_router
from app.api import chat, documents
from app.core.config import settings
from app.db import models  # noqa: F401
from app.db.database import init_db
from app.api.auth import router as auth_router
import os

app = FastAPI(title=settings.app_name)

init_db()

app.include_router(auth_router)
app.include_router(tools_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(documents.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": f"{settings.app_name} is running"}

import os

@app.get("/debug-version")
def debug_version():
    return {
        "commit_sha": os.getenv("RAILWAY_GIT_COMMIT_SHA"),
        "branch": os.getenv("RAILWAY_GIT_BRANCH"),
        "service_name": os.getenv("RAILWAY_SERVICE_NAME"),
        "rag_version": "RESET_V3",
    }