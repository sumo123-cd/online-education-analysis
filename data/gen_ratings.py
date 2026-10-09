import csv
import random
from datetime import date, timedelta

random.seed(42)

RATING_WEIGHTS = {1: 5, 2: 8, 3: 20, 4: 37, 5: 30}

REVIEW_TEXTS = {
    1: [
        "Not helpful at all.",
        "Very disappointing course.",
        "Did not meet my expectations.",
        "Waste of time, content is outdated.",
        "Poor quality material and explanations.",
    ],
    2: [
        "Below average, needs a lot of improvement.",
        "Some content was useful but mostly lacking.",
        "Not worth the effort.",
        "Instructor explanations were unclear.",
        "Mediocre course, expected much more.",
    ],
    3: [
        "Decent course, covers the basics.",
        "Average content, nothing special.",
        "Okay for beginners but lacks depth.",
        "Some good points but could be better organized.",
        "Fair course overall.",
    ],
    4: [
        "Good course, learned a lot.",
        "Well structured and easy to follow.",
        "Solid content with practical examples.",
        "Very informative and well presented.",
        "Would recommend to others looking to learn this topic.",
    ],
    5: [
        "Excellent course, highly recommend!",
        "Outstanding content, exceeded my expectations!",
        "Best course I have taken on this subject.",
        "Fantastic instructor and very clear explanations.",
        "Absolutely loved it, worth every minute!",
    ],
}

start_date = date(2023, 1, 1)
end_date = date(2024, 6, 30)
date_range = (end_date - start_date).days

ratings_pool = []
for rating, weight in RATING_WEIGHTS.items():
    ratings_pool.extend([rating] * weight)

rows = []
for i in range(1, 201):
    rating_id = f"R{i:03d}"
    learner_id = f"L{random.randint(1, 80):03d}"
    course_id = f"C{random.randint(1, 10):03d}"
    rating = random.choice(ratings_pool)
    review_date = start_date + timedelta(days=random.randint(0, date_range))
    review_text = random.choice(REVIEW_TEXTS[rating])
    rows.append([rating_id, learner_id, course_id, rating, review_date.strftime("%Y-%m-%d"), review_text])

output_path = "data/ratings.csv"
with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["rating_id", "learner_id", "course_id", "rating", "review_date", "review_text"])
    writer.writerows(rows)

print(f"Written {len(rows)} rows to {output_path}")
