"""Load placement records from a CSV or Excel file into a DataFrame."""

from pathlib import Path

import pandas as pd

SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def import_file(path: str) -> pd.DataFrame:
    """Read a CSV or Excel file and return it as a DataFrame.

    Raises:
        ValueError: if the file type is unsupported or the file is empty.
        FileNotFoundError: if the path does not exist.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = p.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError("Select a CSV or Excel file (.csv, .xlsx, .xls).")

    df = pd.read_csv(p) if suffix == ".csv" else pd.read_excel(p)

    if df.empty:
        raise ValueError("The selected file has no rows.")

    return df
