"""
Data Service
============
Loads all CSVs and exposes computed analytics used by the FastAPI endpoints.
"""

import os
import pandas as pd
import numpy as np
from scipy import stats
from functools import lru_cache

# Resolve the data directory relative to this file (backend/../data/)
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA = os.path.join(_BASE, "data")


@lru_cache(maxsize=1)
def _load():
    """Load all four CSVs once and cache them in-process."""
    courses = pd.read_csv(os.path.join(_DATA, "courses.csv"))
    enrollments = pd.read_csv(
        os.path.join(_DATA, "enrollments.csv"),
        parse_dates=["enrollment_date", "completion_date"],
    )
    activity = pd.read_csv(
        os.path.join(_DATA, "activity.csv"),
        parse_dates=["activity_date"],
    )
    ratings = pd.read_csv(
        os.path.join(_DATA, "ratings.csv"),
        parse_dates=["review_date"],
    )
    return courses, enrollments, activity, ratings


# ── Courses ───────────────────────────────────────────────────────────────────

def get_courses(category: str = None, level: str = None) -> list[dict]:
    courses, _, _, _ = _load()
    df = courses.copy()
    if category:
        df = df[df["category"].str.lower() == category.lower()]
    if level:
        df = df[df["level"].str.lower() == level.lower()]
    return df.to_dict(orient="records")


# ── KPIs ──────────────────────────────────────────────────────────────────────

def get_kpis() -> dict:
    _, enrollments, activity, ratings = _load()
    total_enrollments = len(enrollments)
    unique_learners = int(enrollments["learner_id"].nunique())
    completed = int((enrollments["completion_status"] == "Completed").sum())
    completion_rate = round(completed / total_enrollments * 100, 1) if total_enrollments else 0.0
    avg_rating = round(float(ratings["rating"].mean()), 2)
    total_sessions = len(activity)
    avg_minutes = round(float(activity["minutes_spent"].mean()), 1)
    return {
        "total_enrollments": total_enrollments,
        "unique_learners": unique_learners,
        "completed": completed,
        "completion_rate_pct": completion_rate,
        "avg_rating": avg_rating,
        "total_sessions": total_sessions,
        "avg_minutes_per_session": avg_minutes,
    }


# ── Enrollments ───────────────────────────────────────────────────────────────

def get_enrollments() -> dict:
    courses, enrollments, _, _ = _load()

    # Per-course counts
    per_course = (
        enrollments
        .merge(courses[["course_id", "course_name", "category"]], on="course_id")
        .groupby(["course_id", "course_name", "category"])
        .size()
        .reset_index(name="total_enrollments")
        .sort_values("total_enrollments", ascending=False)
    )

    # Monthly trend
    enrollments = enrollments.copy()
    enrollments["month"] = enrollments["enrollment_date"].dt.to_period("M").dt.to_timestamp()
    monthly = (
        enrollments.groupby("month").size()
        .reset_index(name="enrollments")
    )
    monthly["month"] = monthly["month"].dt.strftime("%Y-%m")

    # By category
    by_category = (
        enrollments
        .merge(courses[["course_id", "category"]], on="course_id")
        .groupby("category").size()
        .reset_index(name="count")
    )

    return {
        "per_course": per_course.to_dict(orient="records"),
        "monthly_trend": monthly.to_dict(orient="records"),
        "by_category": by_category.to_dict(orient="records"),
    }


# ── Completion Rates ──────────────────────────────────────────────────────────

def get_completion_rates() -> dict:
    courses, enrollments, _, _ = _load()

    status_dist = (
        enrollments["completion_status"].value_counts()
        .reset_index()
        .rename(columns={"completion_status": "status", "count": "count"})
    )

    by_course = (
        enrollments
        .merge(courses[["course_id", "course_name"]], on="course_id")
        .groupby(["course_name", "completion_status"])
        .size().unstack(fill_value=0).reset_index()
    )
    for col in ["Completed", "In Progress", "Dropped"]:
        if col not in by_course.columns:
            by_course[col] = 0
    total = by_course[["Completed", "In Progress", "Dropped"]].sum(axis=1)
    by_course["completion_rate_pct"] = (by_course["Completed"] / total * 100).round(1)
    by_course = by_course.sort_values("completion_rate_pct", ascending=False)

    progress_dist = (
        enrollments[enrollments["completion_status"] == "In Progress"]["progress_percent"]
        .dropna().astype(int).value_counts().sort_index()
        .reset_index().rename(columns={"progress_percent": "progress", "count": "count"})
    )

    return {
        "status_distribution": status_dist.to_dict(orient="records"),
        "per_course": by_course[["course_name", "Completed", "In Progress", "Dropped", "completion_rate_pct"]].to_dict(orient="records"),
        "in_progress_progress_distribution": progress_dist.to_dict(orient="records"),
    }


# ── Ratings ───────────────────────────────────────────────────────────────────

def get_ratings() -> dict:
    courses, enrollments, _, ratings = _load()

    avg_per_course = (
        ratings.merge(courses[["course_id", "course_name"]], on="course_id")
        .groupby("course_name")["rating"]
        .agg(avg_rating="mean", num_reviews="count")
        .reset_index()
    )
    avg_per_course["avg_rating"] = avg_per_course["avg_rating"].round(2)
    avg_per_course = avg_per_course.sort_values("avg_rating", ascending=False)

    distribution = (
        ratings["rating"].value_counts().sort_index()
        .reset_index().rename(columns={"rating": "stars", "count": "count"})
    )

    # Correlation with completion rate
    completion_by_course = (
        enrollments
        .merge(courses[["course_id", "course_name"]], on="course_id")
        .groupby(["course_name", "completion_status"])
        .size().unstack(fill_value=0).reset_index()
    )
    for col in ["Completed", "In Progress", "Dropped"]:
        if col not in completion_by_course.columns:
            completion_by_course[col] = 0
    total = completion_by_course[["Completed", "In Progress", "Dropped"]].sum(axis=1)
    completion_by_course["completion_rate_pct"] = (completion_by_course["Completed"] / total * 100).round(1)

    corr_df = avg_per_course.merge(
        completion_by_course[["course_name", "completion_rate_pct"]], on="course_name"
    )
    r, p = stats.pearsonr(corr_df["avg_rating"], corr_df["completion_rate_pct"])

    recent_reviews = (
        ratings.merge(courses[["course_id", "course_name"]], on="course_id")
        [["review_date", "course_name", "rating", "review_text"]]
        .sort_values("review_date", ascending=False)
        .head(10)
    )
    recent_reviews["review_date"] = recent_reviews["review_date"].dt.strftime("%Y-%m-%d")

    return {
        "avg_per_course": avg_per_course.to_dict(orient="records"),
        "distribution": distribution.to_dict(orient="records"),
        "correlation": {"pearson_r": round(r, 3), "p_value": round(p, 3)},
        "recent_reviews": recent_reviews.to_dict(orient="records"),
    }


# ── Learner Activity ──────────────────────────────────────────────────────────

def get_activity() -> dict:
    _, _, activity, _ = _load()

    daily_active = (
        activity.groupby("activity_date")["learner_id"].nunique()
        .reset_index().rename(columns={"learner_id": "active_users"})
    )
    daily_active["activity_date"] = daily_active["activity_date"].dt.strftime("%Y-%m-%d")

    by_type = (
        activity["activity_type"].value_counts()
        .reset_index().rename(columns={"activity_type": "type", "count": "sessions"})
    )

    heatmap = (
        activity.groupby(["day_of_week", "hour_of_day"]).size()
        .reset_index(name="sessions")
    )

    top_learners = (
        activity.groupby("learner_id")
        .agg(total_sessions=("activity_id", "count"), total_minutes=("minutes_spent", "sum"))
        .reset_index()
        .sort_values("total_sessions", ascending=False)
        .head(15)
    )

    minutes_by_type = (
        activity.groupby("activity_type")["minutes_spent"]
        .agg(mean="mean", median="median", min="min", max="max")
        .round(1).reset_index()
    )

    return {
        "daily_active_users": daily_active.to_dict(orient="records"),
        "by_type": by_type.to_dict(orient="records"),
        "heatmap": heatmap.to_dict(orient="records"),
        "top_learners": top_learners.to_dict(orient="records"),
        "minutes_by_type": minutes_by_type.to_dict(orient="records"),
    }
