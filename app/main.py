from fastapi import FastAPI

from app.routers import auth, tender_sources

app = FastAPI(
    title="Medical Tender Intelligence & Bid Management System",
    description="MVP foundations: authentication, role-based access control, and tender source management.",
    version="0.1.0-mvp",
)

app.include_router(auth.router)
app.include_router(tender_sources.router)


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}
