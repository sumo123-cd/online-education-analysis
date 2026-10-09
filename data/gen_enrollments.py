import csv
import random
from datetime import date, timedelta

random.seed(42)

START_DATE = date(2023, 1, 1)
END_DATE = date(2024, 6, 30)
DATE_RANGE = (END_DATE - START_DATE).days

STATUSES = ["Completed", "In Progress", "Dropped"]
WEIGHTS = [0.40, 0.45, 0.15]

def random_date(start, day_range):
    return start + timedelta(days=random.randint(0, day_range))

rows = []
for i in range(1, 301):
    enrollment_id = f"E{i:04d}"
    learner_id = f"L{random.randint(1, 80):03d}"
    course_id = f"C{random.randint(1, 10):03d}"
    enrollment_date = random_date(START_DATE, DATE_RANGE)

    status = random.choices(STATUSES, weights=WEIGHTS, k=1)[0]

    if status == "Completed":
        completion_date = enrollment_date + timedelta(days=random.randint(7, 90))
        progress_percent = 100
    elif status == "In Progress":
        completion_date = ""
        progress_percent = random.randint(10, 99)
    else:  # Dropped
        completion_date = ""
        progress_percent = random.randint(5, 40)

    rows.append([
        enrollment_id,
        learner_id,
        course_id,
        enrollment_date.isoformat(),
        status,
        completion_date.isoformat() if completion_date else "",
        progress_percent,
    ])

output_path = "data/enrollments.csv"
with open(output_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "enrollment_id", "learner_id", "course_id",
        "enrollment_date", "completion_status",
        "completion_date", "progress_percent"
    ])
    writer.writerows(rows)

print(f"Written {len(rows)} rows to {output_path}")
