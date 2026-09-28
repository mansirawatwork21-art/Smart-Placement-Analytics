"""Lightweight smoke tests for the data pipeline (no GUI, no MySQL needed)."""

import pandas as pd

from analytics import calculate_analytics
from data_cleaning import clean_data
from import_data import import_file
from recommendation import recommend_placements

raw = import_file("data/placement_data.xlsx")
df = clean_data(raw)

# The dataset size shouldn't be assumed to be small — just sane relative to input.
assert 0 < len(df) <= len(raw), "cleaning should never invent or lose more rows than it started with"
for col in ["student_id", "student_name", "department", "cgpa", "skills",
            "placement_status", "company", "package_lpa"]:
    assert col in df.columns, f"missing expected column: {col}"

assert df["cgpa"].between(0, 10).all(), "cgpa should be clipped to a 0-10 range"
assert not df["student_id"].duplicated().any(), "duplicate students should be dropped"

stats = calculate_analytics(df)
assert "placement_percentage" in stats
assert stats["total_students"] == len(df)
assert stats["placed_students"] + stats["not_placed_students"] == stats["total_students"]

# calculate_analytics must not blow up on an empty frame.
empty_stats = calculate_analytics(df.iloc[0:0])
assert empty_stats["total_students"] == 0
assert empty_stats["placement_percentage"] == 0

offers = pd.read_csv("data/company_offers.csv")
recs = recommend_placements("B.Sc Computer Science", 8.0, "Python, SQL", offers)
assert isinstance(recs, list)

# An unknown department should yield no matches rather than raising.
assert recommend_placements("Not A Real Department", 9.0, "Python", offers) == []

print("ALL LOCAL TESTS PASSED")
