# Online Education Analysis

A full-stack data analytics project covering course enrollments, completion rates, ratings, and learner activity.

## Tech Stack
- **Backend:** FastAPI + Pydantic
- **Frontend:** Streamlit + Plotly
- **Analysis:** Pandas, Matplotlib, Seaborn, SciPy

## Project Structure
```
profinal/
├── backend/            # FastAPI REST API (6 endpoints)
├── dashboard/          # Streamlit interactive dashboard
├── analysis/           # Standalone analysis script (9 charts)
├── data/               # CSV datasets
└── reports/            # Generated charts & summary report
```

## Setup

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run the backend (Terminal 1)
```bash
python -m uvicorn backend.main:app --reload --port 8080
```

### Run the dashboard (Terminal 2)
```bash
streamlit run dashboard/app.py
```

### Run standalone analysis
```bash
python -X utf8 analysis/education_analysis.py
```

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /api/kpis` | Top-level KPI metrics |
| `GET /api/courses` | All courses (filter by category/level) |
| `GET /api/enrollments` | Enrollment analytics |
| `GET /api/completion-rates` | Completion rate analytics |
| `GET /api/ratings` | Course rating analytics |
| `GET /api/activity` | Learner activity analytics |

API docs available at: `http://localhost:8080/docs`
