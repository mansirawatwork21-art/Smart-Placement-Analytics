"""Export a DataFrame to disk in either Excel or CSV format."""

from pathlib import Path

import pandas as pd


def export_data(df: pd.DataFrame, path: str) -> None:
    """Write df to path as .xlsx or .csv, based on the file's extension."""
    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        df.to_csv(path, index=False)
    else:
        df.to_excel(path, index=False)
