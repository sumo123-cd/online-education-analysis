"""
FastAPI Backend — Online Education Analysis
============================================
Run with:  uvicorn backend.main:app --reload --port 8000
Docs at:   http://localhost:8000/docs
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from backend import data_service as ds
from backend.models import (
    CoursesResponse,
    KPIResponse,
    EnrollmentsResponse,
    CompletionRatesResponse,
    RatingsResponse,
    ActivityResponse,
)

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Online Education Analysis API",
    description=(
        "REST API for the Online Education Analysis project.\n\n"
        "Covers **course enrollments**, **completion rates**, **ratings**, and **learner activity**."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Allow the Streamlit dashboard (any origin during dev) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    """Health check — confirms the API is running."""
    return {"status": "ok", "message": "Online Education Analysis API is running."}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


# ── Courses ───────────────────────────────────────────────────────────────────
@app.get(
    "/api/courses",
    response_model=CoursesResponse,
    tags=["Courses"],
    summary="List all courses",
    description="Returns all courses. Optionally filter by **category** and/or **level**.",
)
def list_courses(
    category: Optional[str] = Query(None, description="Filter by category (e.g. 'Data Science')"),
    level: Optional[str] = Query(None, description="Filter by level: Beginner | Intermediate | Advanced"),
):
    try:
        courses = ds.get_courses(category=category, level=level)
        return {"total": len(courses), "courses": courses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── KPIs ──────────────────────────────────────────────────────────────────────
@app.get(
    "/api/kpis",
    response_model=KPIResponse,
    tags=["KPIs"],
    summary="Top-level KPI metrics",
    description=(
        "Returns high-level metrics across all data:\n"
        "total enrollments, unique learners, completion rate, average rating, and activity sessions."
    ),
)
def kpis():
    try:
        return ds.get_kpis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Enrollments ───────────────────────────────────────────────────────────────
@app.get(
    "/api/enrollments",
    response_model=EnrollmentsResponse,
    tags=["Enrollments"],
    summary="Enrollment analytics",
    description=(
        "Returns:\n"
        "- Total enrollments per course\n"
        "- Monthly enrollment trend\n"
        "- Enrollments broken down by category"
    ),
)
def enrollments():
    try:
        return ds.get_enrollments()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Completion Rates ──────────────────────────────────────────────────────────
@app.get(
    "/api/completion-rates",
    response_model=CompletionRatesResponse,
    tags=["Completion Rates"],
    summary="Completion rate analytics",
    description=(
        "Returns:\n"
        "- Overall enrollment status distribution (Completed / In Progress / Dropped)\n"
        "- Completion rate % per course\n"
        "- Progress % distribution for in-progress learners"
    ),
)
def completion_rates():
    try:
        return ds.get_completion_rates()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Ratings ───────────────────────────────────────────────────────────────────
@app.get(
    "/api/ratings",
    response_model=RatingsResponse,
    tags=["Ratings"],
    summary="Course rating analytics",
    description=(
        "Returns:\n"
        "- Average rating per course\n"
        "- 1–5 star distribution\n"
        "- Pearson correlation between rating and completion rate\n"
        "- 10 most recent reviews"
    ),
)
def ratings():
    try:
        return ds.get_ratings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Activity ──────────────────────────────────────────────────────────────────
@app.get(
    "/api/activity",
    response_model=ActivityResponse,
    tags=["Learner Activity"],
    summary="Learner activity analytics",
    description=(
        "Returns:\n"
        "- Daily active learner counts\n"
        "- Session counts by activity type\n"
        "- Heatmap data (day of week × hour of day)\n"
        "- Top 15 most active learners\n"
        "- Average minutes spent per activity type"
    ),
)
def activity():
    try:
        return ds.get_activity()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
