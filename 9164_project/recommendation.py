"""Rule-based matching of a student profile against company offers."""

import pandas as pd


def _skill_set(text) -> set:
    return {s.strip().lower() for s in str(text).split(",") if s.strip()}


def recommend_placements(department: str, cgpa: float, skills: str, offers: pd.DataFrame) -> list[dict]:
    """Return offers the student qualifies for, ranked by skill match then package.

    An offer qualifies when the department matches, the student's CGPA meets the
    minimum, and (when the offer lists required skills) at least one of them is
    present in the student's skill list.
    """
    department = str(department).strip().lower()
    if not department:
        return []

    student_skills = _skill_set(skills)
    results = []

    for _, offer in offers.iterrows():
        if str(offer.department).strip().lower() != department:
            continue
        if cgpa < float(offer.min_cgpa):
            continue

        required = _skill_set(offer.required_skills)
        matched = required & student_skills
        if required and not matched:
            continue

        match_pct = round(len(matched) / len(required) * 100) if required else 100
        results.append({
            "company": offer.company,
            "job_role": offer.job_role,
            "package_lpa": float(offer.package_lpa),
            "matched_skills": ", ".join(sorted(matched)) if matched else "-",
            "skill_match": f"{match_pct}%",
            "_match_pct": match_pct,
        })

    results.sort(key=lambda x: (x["_match_pct"], x["package_lpa"]), reverse=True)
    for r in results:
        del r["_match_pct"]
    return results
