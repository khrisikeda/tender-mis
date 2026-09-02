import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import auth, tender_sources, tenders, catalogue

app = FastAPI(
    title="Medical Tender Intelligence & Bid Management System",
    description="MVP foundations: authentication, role-based access control, and tender source management.",
    version="0.1.0-mvp",
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tender_sources.router)
app.include_router(tenders.router)
app.include_router(tenders.router, prefix="/api")
app.include_router(catalogue.router)


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}


# Mount frontend static files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

