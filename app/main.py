import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import auth, tender_sources, tenders

app = FastAPI(
    title="Medical Tender Intelligence & Bid Management System",
    description="MVP foundations: authentication, role-based access control, and tender source management.",
    version="0.1.0-mvp",
)

app.include_router(auth.router)
app.include_router(tender_sources.router)
app.include_router(tenders.router)


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}


# Mount frontend static files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

