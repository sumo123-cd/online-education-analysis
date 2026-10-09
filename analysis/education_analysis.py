"""
Online Education Analysis
=========================
Covers: Course Enrollments, Completion Rates, Ratings, Learner Activity
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from scipy import stats
import os

# ── Config ────────────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"figure.dpi": 120, "figure.figsize": (10, 5)})
OUTPUT_DIR = "reports/figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Load Data ─────────────────────────────────────────────────────────────────
courses     = pd.read_csv("data/courses.csv")
enrollments = pd.read_csv("data/enrollments.csv", parse_dates=["enrollment_date", "completion_date"])
activity    = pd.read_csv("data/activity.csv",    parse_dates=["activity_date"])
ratings     = pd.read_csv("data/ratings.csv",     parse_dates=["review_date"])

print("=== Data Loaded ===")
print(f"Courses:     {len(courses)} records")
print(f"Enrollments: {len(enrollments)} records")
print(f"Activity:    {len(activity)} records")
print(f"Ratings:     {len(ratings)} records\n")

# ─────────────────────────────────────────────────────────────────────────────
# 1. COURSE ENROLLMENTS
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 50)
print("1. COURSE ENROLLMENTS")
print("=" * 50)

# Total enrollments per course
enroll_counts = (
    enrollments
    .merge(courses[["course_id", "course_name"]], on="course_id")
    .groupby("course_name")
    .size()
    .reset_index(name="total_enrollments")
    .sort_values("total_enrollments", ascending=False)
)
print("\nTop 5 Enrolled Courses:")
print(enroll_counts.head())

# Monthly enrollment trend
enrollments["month"] = enrollments["enrollment_date"].dt.to_period("M")
monthly_trend = enrollments.groupby("month").size().reset_index(name="enrollments")
monthly_trend["month_dt"] = monthly_trend["month"].dt.to_timestamp()

# Plot 1: Enrollments per course
fig, ax = plt.subplots()
sns.barplot(data=enroll_counts, x="total_enrollments", y="course_name", ax=ax,
            hue="course_name", palette="Blues_r", legend=False)
ax.set_title("Total Enrollments per Course", fontsize=14, fontweight="bold")
ax.set_xlabel("Total Enrollments")
ax.set_ylabel("")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/01_enrollments_per_course.png")
plt.close()
print(f"  [OK] Saved: {OUTPUT_DIR}/01_enrollments_per_course.png")

# Plot 2: Monthly enrollment trend
fig, ax = plt.subplots()
ax.plot(monthly_trend["month_dt"], monthly_trend["enrollments"], marker="o", color="#3b82d4", linewidth=2)
ax.fill_between(monthly_trend["month_dt"], monthly_trend["enrollments"], alpha=0.15, color="#3b82d4")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
plt.xticks(rotation=45)
ax.set_title("Monthly Enrollment Trend", fontsize=14, fontweight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("Enrollments")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/02_monthly_trend.png")
plt.close()
print(f"  [OK] Saved: {OUTPUT_DIR}/02_monthly_trend.png")

# KPIs
total_learners   = enrollments["learner_id"].nunique()
total_enrollments = len(enrollments)
print(f"\nKPIs → Total Unique Learners: {total_learners} | Total Enrollments: {total_enrollments}")

# ─────────────────────────────────────────────────────────────────────────────
# 2. COMPLETION RATES
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 50)
print("2. COMPLETION RATES")
print("=" * 50)

# Overall completion funnel
status_counts = enrollments["completion_status"].value_counts().reset_index()
status_counts.columns = ["status", "count"]
print("\nOverall Status Distribution:")
print(status_counts)

# Completion rate per course
completion_by_course = (
    enrollments
    .merge(courses[["course_id", "course_name"]], on="course_id")
    .groupby(["course_name", "completion_status"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)
if "Completed" not in completion_by_course.columns:
    completion_by_course["Completed"] = 0
total_col = completion_by_course.drop("course_name", axis=1).sum(axis=1)
completion_by_course["completion_rate_%"] = (completion_by_course["Completed"] / total_col * 100).round(1)
completion_by_course = completion_by_course.sort_values("completion_rate_%", ascending=False)
print("\nCompletion Rate per Course:")
print(completion_by_course[["course_name", "completion_rate_%"]])

# Plot 3: Completion status pie
fig, ax = plt.subplots(figsize=(7, 7))
colors = ["#4caf50", "#2196f3", "#f44336"]
ax.pie(status_counts["count"], labels=status_counts["status"], autopct="%1.1f%%",
       colors=colors, startangle=140, textprops={"fontsize": 12})
ax.set_title("Overall Enrollment Status Distribution", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/03_completion_status_pie.png")
plt.close()
print(f"  [OK] Saved: {OUTPUT_DIR}/03_completion_status_pie.png")

# Plot 4: Completion rate per course
fig, ax = plt.subplots()
sns.barplot(data=completion_by_course, x="completion_rate_%", y="course_name",
            ax=ax, hue="course_name", palette="Greens_r", legend=False)
ax.axvline(x=completion_by_course["completion_rate_%"].mean(), color="red",
           linestyle="--", label="Avg")
ax.legend()
ax.set_title("Completion Rate per Course (%)", fontsize=14, fontweight="bold")
ax.set_xlabel("Completion Rate (%)")
ax.set_ylabel("")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/04_completion_rate_per_course.png")
plt.close()
print(f"  [OK] Saved: {OUTPUT_DIR}/04_completion_rate_per_course.png")

# ─────────────────────────────────────────────────────────────────────────────
# 3. RATINGS
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 50)
print("3. RATINGS")
print("=" * 50)

avg_ratings = (
    ratings
    .merge(courses[["course_id", "course_name"]], on="course_id")
    .groupby("course_name")["rating"]
    .agg(["mean", "count"])
    .reset_index()
    .rename(columns={"mean": "avg_rating", "count": "num_reviews"})
    .sort_values("avg_rating", ascending=False)
)
avg_ratings["avg_rating"] = avg_ratings["avg_rating"].round(2)
print("\nAverage Ratings per Course:")
print(avg_ratings)

# Plot 5: Avg rating per course
fig, ax = plt.subplots()
bars = sns.barplot(data=avg_ratings, x="avg_rating", y="course_name",
                   ax=ax, hue="course_name", palette="YlOrRd_r", legend=False)
ax.axvline(x=avg_ratings["avg_rating"].mean(), color="blue",
           linestyle="--", label=f"Overall Avg ({avg_ratings['avg_rating'].mean():.2f})")
ax.set_xlim(0, 5)
ax.legend()
ax.set_title("Average Rating per Course", fontsize=14, fontweight="bold")
ax.set_xlabel("Average Rating (1–5)")
ax.set_ylabel("")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/05_avg_rating_per_course.png")
plt.close()
print(f"  [OK] Saved: {OUTPUT_DIR}/05_avg_rating_per_course.png")

# Plot 6: Rating distribution
fig, ax = plt.subplots(figsize=(7, 5))
rating_dist = ratings["rating"].value_counts().sort_index()
ax.bar(rating_dist.index, rating_dist.values, color="#7c5cd8", edgecolor="white")
ax.set_title("Rating Distribution (1–5 Stars)", fontsize=14, fontweight="bold")
ax.set_xlabel("Rating")
ax.set_ylabel("Number of Reviews")
ax.set_xticks([1, 2, 3, 4, 5])
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/06_rating_distribution.png")
plt.close()
print(f"  [OK] Saved: {OUTPUT_DIR}/06_rating_distribution.png")

# Correlation: rating vs completion rate
corr_df = (
    avg_ratings[["course_name", "avg_rating"]]
    .merge(completion_by_course[["course_name", "completion_rate_%"]], on="course_name")
)
r, p = stats.pearsonr(corr_df["avg_rating"], corr_df["completion_rate_%"])
print(f"\nCorrelation (Rating vs Completion Rate): r={r:.3f}, p={p:.3f}")

# ─────────────────────────────────────────────────────────────────────────────
# 4. LEARNER ACTIVITY
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 50)
print("4. LEARNER ACTIVITY")
print("=" * 50)

# Daily active users
daily_active = activity.groupby("activity_date")["learner_id"].nunique().reset_index()
daily_active.columns = ["date", "active_users"]

# Activity by type
activity_type_counts = activity["activity_type"].value_counts().reset_index()
activity_type_counts.columns = ["activity_type", "count"]
print("\nActivity by Type:")
print(activity_type_counts)

# Heatmap: day of week vs hour
heatmap_data = (
    activity
    .groupby(["day_of_week", "hour_of_day"])
    .size()
    .reset_index(name="count")
    .pivot(index="day_of_week", columns="hour_of_day", values="count")
    .fillna(0)
)
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
heatmap_data = heatmap_data.reindex([d for d in day_order if d in heatmap_data.index])

# Plot 7: Activity heatmap
fig, ax = plt.subplots(figsize=(14, 5))
sns.heatmap(heatmap_data, cmap="YlOrRd", ax=ax, linewidths=0.3, cbar_kws={"label": "Sessions"})
ax.set_title("Learner Activity Heatmap (Day vs Hour)", fontsize=14, fontweight="bold")
ax.set_xlabel("Hour of Day")
ax.set_ylabel("Day of Week")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/07_activity_heatmap.png")
plt.close()
print(f"  [OK] Saved: {OUTPUT_DIR}/07_activity_heatmap.png")

# Plot 8: Daily active users
fig, ax = plt.subplots()
ax.plot(daily_active["date"], daily_active["active_users"], color="#3b82d4", linewidth=1.2, alpha=0.8)
ax.set_title("Daily Active Learners Over Time", fontsize=14, fontweight="bold")
ax.set_xlabel("Date")
ax.set_ylabel("Active Learners")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/08_daily_active_users.png")
plt.close()
print(f"  [OK] Saved: {OUTPUT_DIR}/08_daily_active_users.png")

# Plot 9: Minutes spent per activity type
fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(data=activity, x="activity_type", y="minutes_spent",
            hue="activity_type", palette="pastel", legend=False, ax=ax)
ax.set_title("Time Spent per Activity Type", fontsize=14, fontweight="bold")
ax.set_xlabel("Activity Type")
ax.set_ylabel("Minutes Spent")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/09_time_per_activity_type.png")
plt.close()
print(f"  [OK] Saved: {OUTPUT_DIR}/09_time_per_activity_type.png")

# ─────────────────────────────────────────────────────────────────────────────
# Summary Report
# ─────────────────────────────────────────────────────────────────────────────
os.makedirs("reports", exist_ok=True)
with open("reports/summary.md", "w", encoding="utf-8") as f:
    f.write("# Online Education Analysis — Summary Report\n\n")
    f.write("## Key Metrics\n\n")
    f.write(f"- **Total Unique Learners:** {total_learners}\n")
    f.write(f"- **Total Enrollments:** {total_enrollments}\n")
    f.write(f"- **Overall Completion Rate:** {(status_counts.set_index('status').get('count', pd.Series()).get('Completed', 0) / total_enrollments * 100):.1f}%\n")
    f.write(f"- **Average Course Rating:** {ratings['rating'].mean():.2f} / 5\n")
    f.write(f"- **Total Activity Sessions:** {len(activity)}\n\n")
    f.write("## Course Enrollments\n\n")
    f.write(enroll_counts.to_csv(index=False))
    f.write("\n\n## Completion Rates\n\n")
    f.write(completion_by_course[["course_name", "completion_rate_%"]].to_csv(index=False))
    f.write("\n\n## Ratings\n\n")
    f.write(avg_ratings.to_csv(index=False))
    f.write(f"\n\n**Rating vs Completion Correlation:** r = {r:.3f}, p = {p:.3f}\n")

print("\n[OK] Summary report saved to reports/summary.md")
print("\n[DONE] All analysis complete! Charts saved in reports/figures/")
