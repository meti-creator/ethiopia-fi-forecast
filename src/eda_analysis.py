"""
eda_analysis.py

Reusable analytical functions for the Ethiopia Financial Inclusion dataset.
Each function takes a DataFrame in, returns a DataFrame/dict out, and does not
plot or print by default - keeping analysis logic separate from presentation
so it can be unit-tested and reused across notebooks.
"""

from typing import Optional
import pandas as pd
import numpy as np


def summarize_by(df: pd.DataFrame, group_col: str) -> pd.Series:
    """
    Count records by a categorical column (e.g. 'record_type', 'pillar',
    'source_type', 'confidence').

    Raises
    ------
    ValueError if group_col is not present in df.
    """
    if group_col not in df.columns:
        raise ValueError(
            f"Column '{group_col}' not found in DataFrame. "
            f"Available columns: {list(df.columns)}"
        )
    return df[group_col].value_counts()


def temporal_coverage(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build an indicator x year coverage matrix for observation records.

    Returns
    -------
    DataFrame indexed by indicator_code, columns are years, values are
    counts of observations in that year (0 where none).
    """
    obs = df[df["record_type"] == "observation"].copy()
    if obs.empty:
        raise ValueError("No 'observation' records found - cannot build coverage matrix.")

    obs["observation_date"] = pd.to_datetime(obs["observation_date"], errors="coerce")
    obs["year"] = obs["observation_date"].dt.year

    coverage = obs.pivot_table(
        index="indicator_code", columns="year", values="value_numeric", aggfunc="count"
    ).fillna(0).astype(int)
    return coverage


def sparse_indicators(coverage: pd.DataFrame, max_years: int = 1) -> list:
    """Return indicator_codes present in `max_years` or fewer distinct years."""
    n_years_present = (coverage > 0).sum(axis=1)
    return n_years_present[n_years_present <= max_years].index.tolist()


def compute_growth_rates(
    df: pd.DataFrame, indicator_code: str, gender: str = "all"
) -> pd.DataFrame:
    """
    Compute period-over-period and annualized growth for a single indicator's
    time series (observation records only).

    Parameters
    ----------
    indicator_code : e.g. 'ACC_OWNERSHIP'
    gender : filter to a specific gender slice ('all', 'male', 'female')

    Returns
    -------
    DataFrame with columns: fiscal_year, value_numeric, change_pp,
    years_elapsed, annualized_pp_per_year

    Raises
    ------
    ValueError if fewer than 2 matching observation rows are found (can't
    compute a growth rate from a single point).
    """
    subset = df[
        (df["record_type"] == "observation")
        & (df["indicator_code"] == indicator_code)
        & (df.get("gender", "all") == gender)
    ].sort_values("observation_date")

    if len(subset) < 2:
        raise ValueError(
            f"Only {len(subset)} observation(s) found for indicator_code="
            f"'{indicator_code}', gender='{gender}'. Need at least 2 to "
            f"compute a growth rate. This indicator may only have a single "
            f"snapshot - report it as a limitation rather than forcing a trend."
        )

    result = subset[["fiscal_year", "value_numeric"]].reset_index(drop=True)
    result["change_pp"] = result["value_numeric"].diff()
    result["years_elapsed"] = result["fiscal_year"].diff()
    result["annualized_pp_per_year"] = result["change_pp"] / result["years_elapsed"]
    return result


def correlation_matrix(
    df: pd.DataFrame, min_overlapping_years: int = 3
) -> pd.DataFrame:
    """
    Compute a correlation matrix across indicators that have enough
    overlapping yearly observations to make correlation meaningful.

    Indicators with fewer than `min_overlapping_years` shared data points
    with another indicator are excluded from that pairwise comparison and
    the result is NaN, rather than silently computing a misleading
    correlation from 1-2 points.

    Returns
    -------
    DataFrame (indicator_code x indicator_code) of Pearson correlations,
    with NaN where insufficient overlap exists.
    """
    obs = df[df["record_type"] == "observation"].copy()
    obs["observation_date"] = pd.to_datetime(obs["observation_date"], errors="coerce")
    obs["year"] = obs["observation_date"].dt.year

    # Average multiple readings (e.g. by gender) per indicator/year to get
    # one value per (indicator, year) before pivoting.
    yearly = obs.groupby(["year", "indicator_code"])["value_numeric"].mean().unstack()

    codes = yearly.columns.tolist()
    corr = pd.DataFrame(index=codes, columns=codes, dtype=float)

    for i in codes:
        for j in codes:
            if i == j:
                n_valid = yearly[i].dropna().shape[0]
                corr.loc[i, j] = 1.0 if n_valid >= min_overlapping_years else np.nan
                continue
            paired = yearly[[i, j]].dropna()
            if len(paired) >= min_overlapping_years:
                corr.loc[i, j] = paired[i].corr(paired[j])
            else:
                corr.loc[i, j] = np.nan

    return corr


def registered_vs_active_gap(
    df: pd.DataFrame, registered_code: str, active_code: str
) -> Optional[dict]:
    """
    Compare a 'registered users' indicator against an 'active users' or
    'survey-measured ownership' indicator to quantify the registration-vs-
    actual-use gap.

    Returns None (with a printed warning) if either indicator is missing,
    rather than raising - this comparison is exploratory and a missing
    pairing shouldn't halt a larger analysis run.
    """
    reg = df[(df["record_type"] == "observation") & (df["indicator_code"] == registered_code)]
    act = df[(df["record_type"] == "observation") & (df["indicator_code"] == active_code)]

    if reg.empty or act.empty:
        print(
            f"Warning: could not compute registered-vs-active gap - "
            f"registered_code='{registered_code}' found={not reg.empty}, "
            f"active_code='{active_code}' found={not act.empty}"
        )
        return None

    reg_val = reg.sort_values("observation_date").iloc[-1]["value_numeric"]
    act_val = act.sort_values("observation_date").iloc[-1]["value_numeric"]

    return {
        "registered_indicator": registered_code,
        "registered_value": reg_val,
        "active_indicator": active_code,
        "active_value": act_val,
        "activity_rate_pct": (act_val / reg_val * 100) if reg_val else None,
    }


def events_without_impact_links(main_df: pd.DataFrame, impact_df: pd.DataFrame) -> pd.DataFrame:
    """Return event records that have zero corresponding rows in impact_df."""
    events = main_df[main_df["record_type"] == "event"]
    linked_ids = set(impact_df["parent_id"].dropna().unique())
    return events[~events["record_id"].isin(linked_ids)][
        ["record_id", "indicator", "category", "observation_date"]
    ]