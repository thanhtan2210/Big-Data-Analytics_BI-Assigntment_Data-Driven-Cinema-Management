"""
data.py — Real CSV data loaders for Cinema BI Streamlit app.
Reads analytics results from visual/exports/*.csv (Task 3 pipeline output).
All revenue / budget columns are returned in $M (millions USD).
"""
from __future__ import annotations
from pathlib import Path

import pandas as pd
import streamlit as st

# ── Path resolution ───────────────────────────────────────────────────────────
# This file lives at  visual/streamlit_app/data.py
# Exports are at      visual/exports/
_EXPORT_DIR = Path(__file__).parent.parent / "exports"


def _csv(name: str) -> Path:
    return _EXPORT_DIR / name


# Raw USD → millions USD
_M = 1e-6


# ── Dashboard 1 — Revenue & Genre ────────────────────────────────────────────

@st.cache_data
def get_genre_stats() -> pd.DataFrame:
    """Genre-level aggregates. Revenue / budget columns in $M."""
    df = pd.read_csv(_csv("genre_stats.csv"))
    for col in ("total_revenue", "avg_revenue", "avg_budget"):
        df[col] = df[col] * _M
    return df

@st.cache_data
def get_decade_stats() -> pd.DataFrame:
    """Decade × genre breakdown. avg_revenue in $M."""
    df = pd.read_csv(_csv("decade_genre_heatmap.csv"))
    df["avg_revenue"] = df["avg_revenue"] * _M
    return df


@st.cache_data
def get_top_movies(n: int = 20) -> pd.DataFrame:
    """Top-n films by box-office revenue. revenue / budget in $M."""
    df = pd.read_csv(_csv("movies_enriched.csv"))
    df = df[df["revenue"] > 0].nlargest(n, "revenue").copy()
    df["revenue"] = df["revenue"] * _M
    df["budget"] = df["budget"].fillna(0.0) * _M
    df["roi"] = df["roi"].fillna(0.0)
    df["avg_rating"] = df["avg_rating"].fillna(0.0)
    df["rating_count"] = df["rating_count"].fillna(0).astype(int)
    df["year"] = df["year"].apply(
        lambda y: str(int(y)) if pd.notna(y) and y > 0 else "N/A"
    )
    # Drop originals before renaming to avoid duplicate columns
    df = df.drop(columns=["title", "genres"], errors="ignore")
    return (
        df.rename(columns={"title_clean": "title", "genres_array": "genres"})
        [["title", "genres", "year", "revenue", "budget", "roi", "avg_rating", "rating_count"]]
        .reset_index(drop=True)
    )


# ── Dashboard 2 — Audience Engagement ────────────────────────────────────────

@st.cache_data
def get_year_stats() -> pd.DataFrame:
    """Rating activity per calendar year."""
    return pd.read_csv(_csv("year_stats.csv"))


@st.cache_data
def get_rating_dist() -> pd.DataFrame:
    """Distribution of ratings across 10 bins (0.5 → 5.0)."""
    return pd.read_csv(_csv("rating_distribution.csv"))


# ── Dashboard 3 — Customer Segmentation ──────────────────────────────────────

@st.cache_data
def get_user_segment_summary() -> pd.DataFrame:
    """One row per segment: user_count, avg_rating, avg_movies."""
    df = pd.read_csv(_csv("user_segments.csv"))
    return (
        df.groupby("segment", as_index=False)
        .agg(
            user_count=("userId", "count"),
            avg_rating=("avg_rating", "mean"),
            avg_movies=("unique_movies_rated", "mean"),
        )
        .round({"avg_rating": 2, "avg_movies": 1})
    )


@st.cache_data
def get_segment_genre_preference() -> pd.DataFrame:
    """Genre preference ratings per segment."""
    return pd.read_csv(_csv("segment_genre_preference.csv"))


@st.cache_data
def get_tag_stats(top_n: int = 20) -> pd.DataFrame:
    """Top-n most-used user-applied tags."""
    df = pd.read_csv(_csv("tag_stats.csv"))
    return df.nlargest(top_n, "frequency").reset_index(drop=True)


@st.cache_data
def get_segment_recommendations() -> pd.DataFrame:
    """ALS top-N recommendations per segment."""
    df = pd.read_csv(_csv("segment_recommendations.csv"))
    return df.rename(columns={"title_clean": "title", "genres_array": "genres"})


@st.cache_data
def get_user_segments_raw() -> pd.DataFrame:
    """Full user-level segment data (for scatter chart)."""
    return pd.read_csv(_csv("user_segments.csv"))


# ── KPI summary ──────────────────────────────────────────────────────────────

@st.cache_data
def get_kpis() -> dict:
    """Pre-compute all dashboard KPI values from the exported CSVs."""
    gdf = get_genre_stats()          # revenue already in $M
    ydf = get_year_stats()
    tdf = get_tag_stats(1)
    udf = pd.read_csv(_csv("user_segments.csv"), usecols=["userId", "segment", "unique_movies_rated"])
    mdf = pd.read_csv(
        _csv("movies_enriched.csv"),
        usecols=["movieId", "revenue", "budget", "roi"],
    )

    # ── Dashboard 1 ──────────────────────────────────────────────────────────
    # Total revenue: sum from unique movies (avoids genre double-counting)
    total_rev_b = float(
        mdf[mdf["revenue"] > 0]["revenue"].sum() / 1e9   # actual USD → $B
    )
    # Cap per-genre avg_roi at 10× to filter TMDB budget data outliers
    avg_roi = float(gdf["avg_roi"].dropna().clip(upper=10).mean())
    profitable = int(
        ((mdf["revenue"] > 0) & (mdf["budget"] > 0) & (mdf["roi"] > 1)).sum()
    )
    top_rev = gdf.nlargest(1, "total_revenue").iloc[0]

    # ── Dashboard 2 ──────────────────────────────────────────────────────────
    total_ratings = int(ydf["rating_count"].sum())
    avg_rating = float(
        (ydf["avg_rating"] * ydf["rating_count"]).sum() / ydf["rating_count"].sum()
    )
    top_count = gdf.nlargest(1, "rating_count").iloc[0]
    peak = ydf.nlargest(1, "rating_count").iloc[0]
    recent_years = ydf.sort_values("rating_year").tail(3)

    # ── Dashboard 3 ──────────────────────────────────────────────────────────
    total_users = len(udf)
    heavy_n = int((udf["segment"] == "Heavy").sum())
    heavy_pct = heavy_n / total_users * 100 if total_users > 0 else 0.0
    avg_unique_movies = float(udf["unique_movies_rated"].mean()) if total_users > 0 else 0.0
    segment_count = int(udf["segment"].nunique()) if total_users > 0 else 0
    tag_row = tdf.iloc[0] if len(tdf) > 0 else pd.Series({"tag": "N/A", "frequency": 0})
    total_films = len(mdf)

    return {
        # D1
        "total_revenue_b": total_rev_b,
        "avg_roi": avg_roi,
        "profitable_films": profitable,
        "top_genre_rev": str(top_rev["genre"]),
        "top_genre_rev_b": float(top_rev["total_revenue"]) / 1_000,   # $M → $B
        # D2
        "total_ratings": total_ratings,
        "avg_rating": avg_rating,
        "top_genre_count": str(top_count["genre"]),
        "top_genre_count_m": float(top_count["rating_count"]) / 1e6,  # → millions
        "peak_year": int(peak["rating_year"]),
        "peak_count": int(peak["rating_count"]),
        "recent_active_users_3y_sum": int(recent_years["active_users"].sum()),
        "recent_active_year_window": f"{int(recent_years['rating_year'].min())}-{int(recent_years['rating_year'].max())}",
        # D3
        "total_users": total_users,
        "heavy_pct": heavy_pct,
        "heavy_count": heavy_n,
        "avg_unique_movies": avg_unique_movies,
        "segment_count": segment_count,
        "top_tag": str(tag_row["tag"]),
        "top_tag_freq": int(tag_row["frequency"]),
        "total_films": total_films,
    }
