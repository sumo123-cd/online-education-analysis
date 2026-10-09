"""
Online Education Analysis Dashboard
=====================================
Run with: streamlit run dashboard/app.py
Requires the FastAPI backend running at http://localhost:8000
  → uvicorn backend.main:app --reload --port 8000
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

# ── Config ────────────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8080/api"

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Online Education Analysis",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #f7f8fa;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 18px 20px;
        text-align: center;
    }
    .metric-card h2 { color: #3b82d4; margin: 0; font-size: 2rem; }
    .metric-card p  { color: #57606a; margin: 4px 0 0 0; font-size: 0.9rem; }
    .section-title  { font-size: 1.3rem; font-weight: 700; color: #1f2328;
                      border-left: 4px solid #3b82d4; padding-left: 10px; margin: 20px 0 10px; }
    .api-badge { background:#e8f0fe; border:1px solid #3b82d4; color:#1a56db;
                 border-radius:4px; padding:2px 8px; font-size:0.75rem; font-family:monospace; }
</style>
""", unsafe_allow_html=True)

# ── API helpers ────────────────────────────────────────────────────────────────
def fetch(endpoint: str, params: dict = None) -> dict | list:
    """Call the FastAPI backend. Shows a clear error and stops if unreachable."""
    try:
        r = requests.get(f"{API_BASE}{endpoint}", params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error(
            "**Backend not running.**  \n"
            "Open a terminal in the project folder and run:  \n"
            "`python -m uvicorn backend.main:app --reload --port 8080`",
            icon="🔴",
        )
        st.stop()
    except Exception as e:
        st.error(f"API error [{endpoint}]: {e}", icon="⚠️")
        st.stop()


# ── Load sidebar filter options ────────────────────────────────────────────────
courses_raw = fetch("/courses")
if not isinstance(courses_raw, dict) or "courses" not in courses_raw:
    st.error(
        f"Unexpected response from /api/courses: {courses_raw!r}  \n"
        "Make sure the backend is running on port 8000.",
        icon="🔴",
    )
    st.stop()
courses_df = pd.DataFrame(courses_raw["courses"])

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.title("🎓 Filters")
st.sidebar.caption(f"Backend: `{API_BASE}`")
st.sidebar.markdown("---")

all_categories = ["All"] + sorted(courses_df["category"].unique().tolist())
selected_category = st.sidebar.selectbox("Course Category", all_categories)

all_levels = ["All"] + sorted(courses_df["level"].unique().tolist())
selected_level = st.sidebar.selectbox("Course Level", all_levels)

st.sidebar.markdown("---")
st.sidebar.markdown("### API Endpoints")
for ep in ["/courses", "/kpis", "/enrollments", "/completion-rates", "/ratings", "/activity"]:
    st.sidebar.markdown(f'<span class="api-badge">GET {ep}</span>', unsafe_allow_html=True)
st.sidebar.markdown(f"[Open API Docs ↗](http://localhost:8080/docs)")

# ── Fetch all data from API ────────────────────────────────────────────────────
params = {}
if selected_category != "All":
    params["category"] = selected_category
if selected_level != "All":
    params["level"] = selected_level

kpis_data        = fetch("/kpis")
enrollments_data = fetch("/enrollments")
completion_data  = fetch("/completion-rates")
ratings_data     = fetch("/ratings")
activity_data    = fetch("/activity")

# Apply category/level filter to per-course data client-side
filtered_courses = fetch("/courses", params=params if params else None)["courses"]
filtered_course_names = {c["course_name"] for c in filtered_courses}

def filter_by_course(records: list[dict], key="course_name") -> list[dict]:
    if not params:
        return records
    return [r for r in records if r.get(key) in filtered_course_names]

# ── Title ──────────────────────────────────────────────────────────────────────
st.title("🎓 Online Education Analysis Dashboard")
st.markdown(
    "Comprehensive analysis of **course enrollments**, **completion rates**, "
    "**ratings**, and **learner activity** — powered by the FastAPI backend."
)
st.markdown("---")

# ── KPI Row ────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.markdown(f'<div class="metric-card"><h2>{kpis_data["total_enrollments"]}</h2><p>Total Enrollments</p></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="metric-card"><h2>{kpis_data["unique_learners"]}</h2><p>Unique Learners</p></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="metric-card"><h2>{kpis_data["completion_rate_pct"]}%</h2><p>Completion Rate</p></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="metric-card"><h2>{kpis_data["avg_rating"]}⭐</h2><p>Avg Rating</p></div>', unsafe_allow_html=True)
k5.markdown(f'<div class="metric-card"><h2>{kpis_data["total_sessions"]}</h2><p>Activity Sessions</p></div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Enrollments", "✅ Completion Rates", "⭐ Ratings", "📊 Learner Activity"
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — ENROLLMENTS
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-title">Course Enrollments <span class="api-badge">GET /api/enrollments</span></div>', unsafe_allow_html=True)

    per_course_df = pd.DataFrame(filter_by_course(enrollments_data["per_course"]))
    monthly_df    = pd.DataFrame(enrollments_data["monthly_trend"])
    by_cat_df     = pd.DataFrame(enrollments_data["by_category"])

    col1, col2 = st.columns(2)
    with col1:
        if not per_course_df.empty:
            fig = px.bar(
                per_course_df.sort_values("total_enrollments"),
                x="total_enrollments", y="course_name", orientation="h",
                title="Total Enrollments per Course",
                color="total_enrollments", color_continuous_scale="Blues",
                labels={"course_name": "Course", "total_enrollments": "Enrollments"},
            )
            fig.update_layout(coloraxis_showscale=False, height=420)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.line(
            monthly_df, x="month", y="enrollments",
            title="Monthly Enrollment Trend",
            markers=True, color_discrete_sequence=["#3b82d4"],
        )
        fig2.update_layout(height=420, xaxis_title="Month")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">By Category & Level</div>', unsafe_allow_html=True)
    col3, col4 = st.columns(2)

    with col3:
        fig3 = px.pie(
            by_cat_df, values="count", names="category",
            title="Enrollments by Category",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig3.update_layout(height=380)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        level_df = pd.DataFrame(filtered_courses)
        if not level_df.empty:
            level_counts = level_df["level"].value_counts().reset_index()
            level_counts.columns = ["level", "count"]
            fig4 = px.pie(
                level_counts, values="count", names="level",
                title="Courses by Level",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig4.update_layout(height=380)
            st.plotly_chart(fig4, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — COMPLETION RATES
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-title">Completion Rates <span class="api-badge">GET /api/completion-rates</span></div>', unsafe_allow_html=True)

    status_df     = pd.DataFrame(completion_data["status_distribution"])
    per_course_c  = pd.DataFrame(filter_by_course(completion_data["per_course"]))
    progress_df   = pd.DataFrame(completion_data["in_progress_progress_distribution"])

    col1, col2 = st.columns(2)
    with col1:
        color_map = {"Completed": "#4caf50", "In Progress": "#2196f3", "Dropped": "#f44336"}
        fig5 = px.pie(
            status_df, values="count", names="status",
            title="Overall Enrollment Status",
            color="status", color_discrete_map=color_map,
        )
        fig5.update_layout(height=400)
        st.plotly_chart(fig5, use_container_width=True)

    with col2:
        if not per_course_c.empty:
            per_course_c = per_course_c.sort_values("completion_rate_pct", ascending=True)
            avg_comp = per_course_c["completion_rate_pct"].mean()
            fig6 = px.bar(
                per_course_c, x="completion_rate_pct", y="course_name", orientation="h",
                title="Completion Rate per Course (%)",
                color="completion_rate_pct", color_continuous_scale="Greens",
                labels={"course_name": "Course", "completion_rate_pct": "Rate (%)"},
            )
            fig6.add_vline(x=avg_comp, line_dash="dash", line_color="red",
                           annotation_text=f"Avg {avg_comp:.1f}%", annotation_position="top right")
            fig6.update_layout(coloraxis_showscale=False, height=400)
            st.plotly_chart(fig6, use_container_width=True)

    st.markdown('<div class="section-title">Drop-off Analysis</div>', unsafe_allow_html=True)
    col3, col4 = st.columns(2)

    with col3:
        fig7 = px.histogram(
            progress_df, x="progress", y="count",
            title="Progress % Distribution (In-Progress Learners)",
            color_discrete_sequence=["#2196f3"],
            nbins=20,
        )
        fig7.update_layout(height=360, xaxis_title="Progress (%)", yaxis_title="Count")
        st.plotly_chart(fig7, use_container_width=True)

    with col4:
        total_enrolled = status_df["count"].sum()
        in_prog_or_done = status_df.loc[status_df["status"] != "Dropped", "count"].sum()
        completed_count = status_df.loc[status_df["status"] == "Completed", "count"].sum()
        fig8 = go.Figure(go.Funnel(
            y=["Enrolled", "Active (not dropped)", "Completed"],
            x=[total_enrolled, in_prog_or_done, completed_count],
            textinfo="value+percent initial",
            marker={"color": ["#3b82d4", "#4caf50", "#7c5cd8"]},
        ))
        fig8.update_layout(title="Learner Funnel", height=360)
        st.plotly_chart(fig8, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — RATINGS
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-title">Course Ratings <span class="api-badge">GET /api/ratings</span></div>', unsafe_allow_html=True)

    avg_rat_df   = pd.DataFrame(filter_by_course(ratings_data["avg_per_course"]))
    dist_df      = pd.DataFrame(ratings_data["distribution"])
    corr         = ratings_data["correlation"]
    reviews_df   = pd.DataFrame(filter_by_course(ratings_data["recent_reviews"]))

    col1, col2 = st.columns(2)
    with col1:
        if not avg_rat_df.empty:
            avg_rat_df = avg_rat_df.sort_values("avg_rating", ascending=True)
            overall_avg = avg_rat_df["avg_rating"].mean()
            fig9 = px.bar(
                avg_rat_df, x="avg_rating", y="course_name", orientation="h",
                title="Average Rating per Course",
                color="avg_rating", color_continuous_scale="YlOrRd",
                labels={"course_name": "Course", "avg_rating": "Avg Rating"},
            )
            fig9.add_vline(x=overall_avg, line_dash="dash", line_color="blue",
                           annotation_text=f"Avg {overall_avg:.2f}", annotation_position="top right")
            fig9.update_layout(coloraxis_showscale=False, height=420, xaxis_range=[0, 5])
            st.plotly_chart(fig9, use_container_width=True)

    with col2:
        fig10 = px.bar(
            dist_df, x="stars", y="count",
            title="Rating Distribution (1–5 Stars)",
            color="stars", color_continuous_scale="Purples",
            labels={"stars": "Stars", "count": "Reviews"},
        )
        fig10.update_layout(coloraxis_showscale=False, height=420, xaxis=dict(tickvals=[1, 2, 3, 4, 5]))
        st.plotly_chart(fig10, use_container_width=True)

    st.markdown(
        f'<div class="section-title">Rating vs Completion Correlation '
        f'<span class="api-badge">r = {corr["pearson_r"]}  p = {corr["p_value"]}</span></div>',
        unsafe_allow_html=True,
    )

    if not avg_rat_df.empty and not per_course_c.empty:
        corr_plot_df = avg_rat_df.merge(
            per_course_c[["course_name", "completion_rate_pct"]], on="course_name", how="inner"
        )
        if len(corr_plot_df) > 2:
            fig11 = px.scatter(
                corr_plot_df, x="avg_rating", y="completion_rate_pct", text="course_name",
                title=f"Rating vs Completion Rate  (r = {corr['pearson_r']}, p = {corr['p_value']})",
                trendline="ols",
                labels={"avg_rating": "Avg Rating", "completion_rate_pct": "Completion Rate (%)"},
            )
            fig11.update_traces(textposition="top center")
            fig11.update_layout(height=420)
            st.plotly_chart(fig11, use_container_width=True)

    st.markdown('<div class="section-title">Recent Reviews</div>', unsafe_allow_html=True)
    if not reviews_df.empty:
        st.dataframe(
            reviews_df[["review_date", "course_name", "rating", "review_text"]].reset_index(drop=True),
            use_container_width=True,
        )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — LEARNER ACTIVITY
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-title">Learner Activity <span class="api-badge">GET /api/activity</span></div>', unsafe_allow_html=True)

    daily_df    = pd.DataFrame(activity_data["daily_active_users"])
    by_type_df  = pd.DataFrame(activity_data["by_type"])
    heatmap_df  = pd.DataFrame(activity_data["heatmap"])
    top_l_df    = pd.DataFrame(activity_data["top_learners"])
    mins_df     = pd.DataFrame(activity_data["minutes_by_type"])

    col1, col2 = st.columns(2)
    with col1:
        fig12 = px.line(
            daily_df, x="activity_date", y="active_users",
            title="Daily Active Learners Over Time",
            color_discrete_sequence=["#3b82d4"],
        )
        fig12.update_layout(height=400, xaxis_title="Date")
        st.plotly_chart(fig12, use_container_width=True)

    with col2:
        fig13 = px.pie(
            by_type_df, values="sessions", names="type",
            title="Activity Sessions by Type",
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        fig13.update_layout(height=400)
        st.plotly_chart(fig13, use_container_width=True)

    st.markdown('<div class="section-title">Activity Heatmap (Day of Week × Hour)</div>', unsafe_allow_html=True)
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heatmap_pivot = (
        heatmap_df.pivot(index="day_of_week", columns="hour_of_day", values="sessions")
        .fillna(0)
    )
    heatmap_pivot = heatmap_pivot.reindex([d for d in day_order if d in heatmap_pivot.index])
    fig14 = px.imshow(
        heatmap_pivot,
        color_continuous_scale="YlOrRd",
        title="Learner Activity by Day & Hour",
        labels=dict(x="Hour of Day", y="Day of Week", color="Sessions"),
        aspect="auto",
    )
    fig14.update_layout(height=380)
    st.plotly_chart(fig14, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        fig15 = px.bar(
            mins_df, x="activity_type", y="mean",
            title="Avg Minutes Spent per Activity Type",
            color="activity_type",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            labels={"activity_type": "Type", "mean": "Avg Minutes"},
        )
        fig15.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig15, use_container_width=True)

    with col4:
        fig16 = px.bar(
            top_l_df, x="learner_id", y="total_sessions",
            title="Top 15 Most Active Learners",
            color="total_minutes", color_continuous_scale="Blues",
            labels={"learner_id": "Learner", "total_sessions": "Sessions", "total_minutes": "Total Mins"},
        )
        fig16.update_layout(height=400)
        st.plotly_chart(fig16, use_container_width=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#57606a; font-size:0.8rem;'>"
    "Online Education Analysis Dashboard · FastAPI + Streamlit · Data Analytics Course"
    "</div>",
    unsafe_allow_html=True,
)
