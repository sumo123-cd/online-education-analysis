import csv
import random
from datetime import date, timedelta

random.seed(42)

START_DATE = date(2023, 1, 1)
END_DATE = date(2024, 6, 30)
DATE_RANGE = (END_DATE - START_DATE).days

ACTIVITY_TYPES = ["Video", "Quiz", "Assignment", "Discussion", "Reading"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Weighted hours: heavier in evenings 18-22
HOURS = list(range(6, 24))
HOUR_WEIGHTS = [
    1, 1, 1, 2, 2, 3,   # 6-11
    3, 3, 2, 2, 2, 2,   # 12-17
    5, 6, 6, 5, 4, 2    # 18-23
]

OUTPUT = "data/activity.csv"

rows = []
for i in range(1, 501):
    activity_id = f"A{i:04d}"
    learner_id = f"L{random.randint(1, 80):03d}"
    course_id = f"C{random.randint(1, 10):03d}"
    activity_date = START_DATE + timedelta(days=random.randint(0, DATE_RANGE))
    day_of_week = DAYS[activity_date.weekday()]
    hour_of_day = random.choices(HOURS, weights=HOUR_WEIGHTS, k=1)[0]
    minutes_spent = random.randint(10, 120)
    activity_type = random.choice(ACTIVITY_TYPES)

    rows.append([
        activity_id,
        learner_id,
        course_id,
        activity_date.isoformat(),
        day_of_week,
        hour_of_day,
        minutes_spent,
        activity_type,
    ])

with open(OUTPUT, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "activity_id", "learner_id", "course_id", "activity_date",
        "day_of_week", "hour_of_day", "minutes_spent", "activity_type"
    ])
    writer.writerows(rows)

print(f"Written {len(rows)} rows to {OUTPUT}")
