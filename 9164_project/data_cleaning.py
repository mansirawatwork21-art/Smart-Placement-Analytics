"""Clean a raw placement DataFrame into a consistent, analysis-ready shape."""

import pandas as pd

REQUIRED_COLUMNS = [
    "student_id", "student_name", "department", "cgpa",
    "skills", "placement_status", "company", "package_lpa",
]


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names, fill gaps, and enforce sane value ranges.

    Raises:
        ValueError: if any required column is missing after normalization.
    """
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))

    # Drop exact duplicate students, keeping the first record seen.
    df["student_id"] = df["student_id"].astype(str).str.strip()
    df = df.drop_duplicates(subset=["student_id"])

    df["student_name"] = df["student_name"].fillna("Unknown").astype(str).str.strip()
    df["department"] = df["department"].fillna("Unknown").astype(str).str.strip()
    df["skills"] = df["skills"].fillna("").astype(str).str.strip(" ,")
    df["company"] = df["company"].fillna("").astype(str).str.strip()

    # Normalize placement status to "Placed" / "Not Placed" regardless of casing.
    status = df["placement_status"].fillna("Not Placed").astype(str).str.strip()
    df["placement_status"] = status.where(
        status.str.lower() != "placed", "Placed"
    )
    df.loc[df["placement_status"].str.lower() != "placed", "placement_status"] = "Not Placed"

    # Numeric columns: coerce bad values to NaN, then fill with a sensible default.
    df["cgpa"] = pd.to_numeric(df["cgpa"], errors="coerce")
    cgpa_fallback = df["cgpa"].median()
    if pd.isna(cgpa_fallback):
        cgpa_fallback = 0.0
    df["cgpa"] = df["cgpa"].fillna(cgpa_fallback).clip(lower=0, upper=10).round(2)

    df["package_lpa"] = pd.to_numeric(df["package_lpa"], errors="coerce").fillna(0).clip(lower=0)

    # Anyone not placed shouldn't carry a leftover company/package value.
    not_placed = df["placement_status"].eq("Not Placed")
    df.loc[not_placed, "company"] = ""
    df.loc[not_placed, "package_lpa"] = 0

    return df.reset_index(drop=True)
