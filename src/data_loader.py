"""
data_loader.py

Reusable loading and validation functions for the Ethiopia Financial Inclusion
unified dataset. Centralizes the loading logic so notebooks/scripts don't
re-implement (and potentially re-break) the same read + validate steps.
"""

from pathlib import Path
from typing import Tuple
import pandas as pd


class DataValidationError(Exception):
    """Raised when a loaded dataset fails a structural or schema check."""


REQUIRED_MAIN_COLUMNS = {
    "record_id", "record_type", "category", "pillar", "indicator",
    "indicator_code", "value_numeric", "observation_date",
    "source_name", "source_type", "confidence",
}

VALID_RECORD_TYPES = {"observation", "event", "target"}


def load_unified_dataset(filepath: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load the main data sheet and the Impact_sheet from the unified xlsx file.

    Parameters
    ----------
    filepath : str
        Path to ethiopia_fi_unified_data.xlsx (or an enriched version of it).

    Returns
    -------
    (main_df, impact_df) : Tuple[pd.DataFrame, pd.DataFrame]

    Raises
    ------
    FileNotFoundError
        If filepath does not exist.
    DataValidationError
        If either sheet is missing, empty, or lacks required columns.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at '{filepath}'. Check the path is correct "
            f"relative to where this script/notebook is running from."
        )

    try:
        main_df = pd.read_excel(path, sheet_name="ethiopia_fi_unified_data")
    except ValueError as e:
        raise DataValidationError(
            f"Could not read sheet 'ethiopia_fi_unified_data' from {filepath}. "
            f"Confirm the sheet name matches exactly. Original error: {e}"
        ) from e

    try:
        impact_df = pd.read_excel(path, sheet_name="Impact_sheet")
    except ValueError as e:
        raise DataValidationError(
            f"Could not read sheet 'Impact_sheet' from {filepath}. "
            f"Original error: {e}"
        ) from e

    if main_df.empty:
        raise DataValidationError("Main data sheet loaded but contains zero rows.")
    if impact_df.empty:
        raise DataValidationError("Impact_sheet loaded but contains zero rows.")

    missing_cols = REQUIRED_MAIN_COLUMNS - set(main_df.columns)
    if missing_cols:
        raise DataValidationError(
            f"Main sheet is missing required columns: {sorted(missing_cols)}. "
            f"This usually means the wrong file or sheet was loaded."
        )

    bad_types = set(main_df["record_type"].dropna().unique()) - VALID_RECORD_TYPES
    if bad_types:
        raise DataValidationError(
            f"Found unexpected record_type value(s): {bad_types}. "
            f"Expected only: {VALID_RECORD_TYPES}"
        )

    main_df["observation_date"] = pd.to_datetime(
        main_df["observation_date"], errors="coerce"
    )
    n_bad_dates = main_df["observation_date"].isna().sum()
    if n_bad_dates > 0:
        print(
            f"Warning: {n_bad_dates} row(s) have an observation_date that could "
            f"not be parsed and were set to NaT. Check these rows before relying "
            f"on temporal analysis."
        )

    return main_df, impact_df


def load_reference_codes(filepath: str) -> pd.DataFrame:
    """
    Load reference_codes.xlsx, the rulebook of valid categorical values.

    Raises
    ------
    FileNotFoundError, DataValidationError
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"reference_codes file not found at '{filepath}'.")

    ref_df = pd.read_excel(path)
    if ref_df.empty:
        raise DataValidationError("reference_codes loaded but contains zero rows.")
    return ref_df


def validate_against_reference(
    main_df: pd.DataFrame, ref_df: pd.DataFrame, field_col: str = "field",
    value_col: str = "code"
) -> pd.DataFrame:
    """
    Cross-check categorical columns in main_df (e.g. 'pillar', 'category',
    'confidence') against the allowed values listed in reference_codes.

    Returns a DataFrame of any violations found (empty if none). This does not
    raise, since some violations may be expected (new data awaiting reference
    update) - the caller decides whether to treat this as fatal.
    """
    violations = []
    if field_col not in ref_df.columns or value_col not in ref_df.columns:
        print(
            f"Warning: reference_codes does not have expected columns "
            f"'{field_col}'/'{value_col}' - skipping validation. "
            f"Available columns: {list(ref_df.columns)}"
        )
        return pd.DataFrame(violations)

    for field in ref_df[field_col].unique():
        if field not in main_df.columns:
            continue
        allowed = set(ref_df.loc[ref_df[field_col] == field, value_col].dropna())
        actual = set(main_df[field].dropna().unique())
        bad = actual - allowed
        for val in bad:
            violations.append({"field": field, "invalid_value": val})

    return pd.DataFrame(violations)