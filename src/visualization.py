"""
visualization.py

Reusable plotting functions. Each takes data + an optional save_path, and
returns the matplotlib Figure (so a notebook can still show/tweak it) rather
than plotting invisibly. Nothing in here re-computes analysis - that logic
lives in eda_analysis.py, kept separate on purpose.
"""

from pathlib import Path
from typing import Optional
import matplotlib.pyplot as plt
import pandas as pd


def plot_overview(df: pd.DataFrame, save_path: Optional[str] = None) -> plt.Figure:
    """Bar charts: records by type, by pillar, and by confidence."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    df["record_type"].value_counts().plot(kind="bar", ax=axes[0], color="steelblue")
    axes[0].set_title("Records by Type")

    pillar_mask = df["record_type"].isin(["observation", "target"])
    df.loc[pillar_mask, "pillar"].value_counts().plot(kind="bar", ax=axes[1], color="seagreen")
    axes[1].set_title("Records by Pillar")

    df["confidence"].value_counts().plot(kind="bar", ax=axes[2], color="darkorange")
    axes[2].set_title("Confidence Distribution")

    plt.tight_layout()
    if save_path:
        _save(fig, save_path)
    return fig


def plot_temporal_coverage(coverage: pd.DataFrame, save_path: Optional[str] = None) -> plt.Figure:
    """Heatmap of the indicator x year coverage matrix from eda_analysis.temporal_coverage()."""
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(coverage, cmap="YlGnBu", aspect="auto")
    ax.set_xticks(range(len(coverage.columns)))
    ax.set_xticklabels(coverage.columns)
    ax.set_yticks(range(len(coverage.index)))
    ax.set_yticklabels(coverage.index)
    ax.set_title("Temporal Coverage: Indicator vs Year (darker = more observations)")
    plt.colorbar(im, ax=ax)
    plt.tight_layout()
    if save_path:
        _save(fig, save_path)
    return fig


def plot_indicator_trend(
    df: pd.DataFrame, indicator_code: str, gender: str = "all",
    title: Optional[str] = None, ylabel: str = "% of adults",
    save_path: Optional[str] = None,
) -> plt.Figure:
    """
    Plot a single indicator's trajectory over time (observation records only).

    Raises
    ------
    ValueError if no matching observation rows are found.
    """
    subset = df[
        (df["record_type"] == "observation")
        & (df["indicator_code"] == indicator_code)
        & (df.get("gender", "all") == gender)
    ].sort_values("observation_date")

    if subset.empty:
        raise ValueError(
            f"No observation rows found for indicator_code='{indicator_code}', "
            f"gender='{gender}'. Check spelling / gender filter."
        )

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(subset["observation_date"], subset["value_numeric"],
            marker="o", markersize=10, linewidth=2, color="navy")
    for _, row in subset.iterrows():
        ax.annotate(f"{row['value_numeric']:.0f}%",
                    (row["observation_date"], row["value_numeric"]),
                    textcoords="offset points", xytext=(0, 10),
                    ha="center", fontweight="bold")

    ax.set_title(title or f"{indicator_code} Trajectory")
    ax.set_ylabel(ylabel)
    plt.tight_layout()
    if save_path:
        _save(fig, save_path)
    return fig


def plot_event_overlay(
    df: pd.DataFrame, indicator_code: str, gender: str = "all",
    save_path: Optional[str] = None,
) -> plt.Figure:
    """Plot an indicator's trend with vertical lines marking cataloged events."""
    trend = df[
        (df["record_type"] == "observation")
        & (df["indicator_code"] == indicator_code)
        & (df.get("gender", "all") == gender)
    ].sort_values("observation_date")

    if trend.empty:
        raise ValueError(f"No observation rows found for indicator_code='{indicator_code}'.")

    events = df[df["record_type"] == "event"].sort_values("observation_date")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(trend["observation_date"], trend["value_numeric"],
            marker="o", linewidth=2, color="navy", label=f"{indicator_code}")

    colors = {"product_launch": "green", "policy": "purple", "market_entry": "orange",
              "infrastructure": "brown", "milestone": "red", "partnership": "teal",
              "pricing": "gray"}

    ylim = ax.get_ylim()
    for _, e in events.iterrows():
        c = colors.get(e["category"], "black")
        ax.axvline(e["observation_date"], color=c, linestyle="--", alpha=0.6)
        ax.text(e["observation_date"], ylim[1] * 0.95, e["indicator"],
                rotation=90, fontsize=7, va="top", ha="right")

    ax.set_title(f"{indicator_code} with Event Timeline Overlay")
    ax.legend()
    plt.tight_layout()
    if save_path:
        _save(fig, save_path)
    return fig


def _save(fig: plt.Figure, save_path: str) -> None:
    """Ensure the parent directory exists, then save the figure."""
    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120)