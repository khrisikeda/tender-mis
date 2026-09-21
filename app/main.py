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


@app.middleware("http")
async def add_no_cache_header(request, call_next):
    response = await call_next(request)
    if request.url.path.endswith((".js", ".css", ".html")) or request.url.path == "/":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

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


import asyncio
import logging

logger = logging.getLogger("main")


async def periodic_30min_sourcing_worker():
    """Automated background worker: scans all monitored sources every 30 minutes."""
    while True:
        await asyncio.sleep(1800)  # 30 minutes = 1800 seconds
        try:
            from app.services.multi_source_crawler import scan_all_monitored_sources
            logger.info("Executing 30-minute automated multi-source scan (Imvaho Nshya + Umucyo)...")
            await scan_all_monitored_sources()
            logger.info("Completed 30-minute automated multi-source scan.")
        except Exception as e:
            logger.warning(f"Periodic sourcing worker error: {e}")


@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(periodic_30min_sourcing_worker())


