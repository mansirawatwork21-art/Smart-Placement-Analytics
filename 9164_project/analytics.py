"""Compute summary statistics for a cleaned placement DataFrame."""

import pandas as pd


def calculate_analytics(df: pd.DataFrame) -> dict:
    """Return placement KPIs. Safe to call on an empty DataFrame."""
    total = len(df)
    if total == 0:
        return {
            "total_students": 0,
            "placed_students": 0,
            "not_placed_students": 0,
            "placement_percentage": 0,
            "average_package_lpa": 0,
            "highest_package_lpa": 0,
            "median_package_lpa": 0,
            "company_wise": {},
            "department_wise": {},
        }

    is_placed = df["placement_status"].astype(str).str.lower().eq("placed")
    placed = df[is_placed]
    packages = placed["package_lpa"]

    return {
        "total_students": total,
        "placed_students": int(is_placed.sum()),
        "not_placed_students": int((~is_placed).sum()),
        "placement_percentage": round(is_placed.mean() * 100, 2),
        "average_package_lpa": round(float(packages.mean()), 2) if len(packages) else 0,
        "highest_package_lpa": round(float(packages.max()), 2) if len(packages) else 0,
        "median_package_lpa": round(float(packages.median()), 2) if len(packages) else 0,
        "company_wise": placed["company"].value_counts().to_dict(),
        "department_wise": placed.groupby("department")["student_id"].count().to_dict(),
    }
