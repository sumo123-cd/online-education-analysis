"""
Pydantic Response Models
========================
Defines the shape of every API response for automatic validation and OpenAPI docs.
"""

from pydantic import BaseModel
from typing import Optional


# ── Courses ───────────────────────────────────────────────────────────────────

class Course(BaseModel):
    course_id: str
    course_name: str
    category: str
    instructor: str
    duration_hours: int
    price_usd: float
    level: str


class CoursesResponse(BaseModel):
    total: int
    courses: list[Course]


# ── KPIs ──────────────────────────────────────────────────────────────────────

class KPIResponse(BaseModel):
    total_enrollments: int
    unique_learners: int
    completed: int
    completion_rate_pct: float
    avg_rating: float
    total_sessions: int
    avg_minutes_per_session: float


# ── Enrollments ───────────────────────────────────────────────────────────────

class EnrollmentPerCourse(BaseModel):
    course_id: str
    course_name: str
    category: str
    total_enrollments: int


class MonthlyTrend(BaseModel):
    month: str
    enrollments: int


class CategoryCount(BaseModel):
    category: str
    count: int


class EnrollmentsResponse(BaseModel):
    per_course: list[EnrollmentPerCourse]
    monthly_trend: list[MonthlyTrend]
    by_category: list[CategoryCount]


# ── Completion Rates ──────────────────────────────────────────────────────────

class StatusDistItem(BaseModel):
    status: str
    count: int


class CompletionPerCourse(BaseModel):
    course_name: str
    Completed: int
    in_progress: int = 0
    Dropped: int = 0
    completion_rate_pct: float

    class Config:
        populate_by_name = True


class ProgressDistItem(BaseModel):
    progress: int
    count: int


class CompletionRatesResponse(BaseModel):
    status_distribution: list[StatusDistItem]
    per_course: list[dict]
    in_progress_progress_distribution: list[ProgressDistItem]


# ── Ratings ───────────────────────────────────────────────────────────────────

class AvgRatingPerCourse(BaseModel):
    course_name: str
    avg_rating: float
    num_reviews: int


class RatingDistItem(BaseModel):
    stars: int
    count: int


class Correlation(BaseModel):
    pearson_r: float
    p_value: float


class Review(BaseModel):
    review_date: str
    course_name: str
    rating: int
    review_text: str


class RatingsResponse(BaseModel):
    avg_per_course: list[AvgRatingPerCourse]
    distribution: list[RatingDistItem]
    correlation: Correlation
    recent_reviews: list[Review]


# ── Activity ──────────────────────────────────────────────────────────────────

class DailyActiveUsers(BaseModel):
    activity_date: str
    active_users: int


class ActivityByType(BaseModel):
    type: str
    sessions: int


class HeatmapCell(BaseModel):
    day_of_week: str
    hour_of_day: int
    sessions: int


class TopLearner(BaseModel):
    learner_id: str
    total_sessions: int
    total_minutes: int


class MinutesByType(BaseModel):
    activity_type: str
    mean: float
    median: float
    min: float
    max: float


class ActivityResponse(BaseModel):
    daily_active_users: list[DailyActiveUsers]
    by_type: list[ActivityByType]
    heatmap: list[HeatmapCell]
    top_learners: list[TopLearner]
    minutes_by_type: list[MinutesByType]
