"""
Cinema BI Dashboard — Streamlit Prototype
Visualises three BI dashboards with mock data before Power BI production.
Run: streamlit run streamlit_app/app.py
"""
import sys
import os

# allow `from data import *` when the working-directory is the project root
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from data import (
    get_genre_stats,
    get_decade_stats,
    get_top_movies,
    get_year_stats,
    get_rating_dist,
    get_user_segment_summary,
    get_segment_genre_preference,
    get_tag_stats,
    get_segment_recommendations,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cinema BI Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global style ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* main background */
.stApp { background-color: #0a0e1a; }

/* sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #12122a 0%, #0e0f1e 100%);
    border-right: 1px solid #252b4a;
}

/* KPI card */
.kpi-card {
    background: linear-gradient(135deg, #1e2140 0%, #252b4a 100%);
    border: 1px solid #3a4080;
    border-radius: 12px;
    padding: 20px 16px;
    text-align: center;
    margin-bottom: 4px;
}
.kpi-label  { font-size: 12px; color: #8899bb; letter-spacing: .5px; margin-bottom: 6px; }
.kpi-value  { font-size: 26px; font-weight: 700; color: #e8ecff; line-height: 1.1; }
.kpi-delta  { font-size: 11px; color: #4caf6e; margin-top: 6px; }

/* section title gradient */
.dash-title {
    background: linear-gradient(90deg, #e50914 0%, #ff6b35 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 2px;
}

/* hide default radio label */
div[data-testid="stRadio"] > label { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Plotly theme constants ─────────────────────────────────────────────────────
THEME  = "plotly_dark"
BG     = "#0f1022"
PAPER  = "#0a0e1a"
RED    = "#e50914"
GOLD   = "#f5c518"
GREY   = "#6c757d"

CHART_LAYOUT = dict(
    paper_bgcolor=PAPER,
    plot_bgcolor=BG,
    margin=dict(l=8, r=8, t=32, b=8),
    font=dict(family="Inter, sans-serif", size=12),
    legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0),
)


def kpi(label: str, value: str, delta: str = "") -> None:
    delta_html = f'<div class="kpi-delta">▲ {delta}</div>' if delta else ""
    st.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'{delta_html}</div>',
        unsafe_allow_html=True,
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎬 Cinema BI")
    st.markdown("*Data-Driven Cinema Management*")
    st.divider()

    page = st.radio(
        "nav",
        ["📊 Revenue & Genre", "👥 Audience Engagement", "🎯 Customer Segmentation"],
    )

    st.divider()
    st.markdown("**Dataset**")
    st.caption("MovieLens 25M + TMDB")
    st.caption("162,541 users")
    st.caption("62,423 films")
    st.caption("25,000,095 ratings")
    st.divider()
    st.info("⚠️ Mock data — prototype only", icon="ℹ️")


# ══════════════════════════════════════════════════════════════════════════════
# Dashboard 1 — Revenue & Genre Intelligence
# ══════════════════════════════════════════════════════════════════════════════
if "Revenue" in page:
    st.markdown('<div class="dash-title">Dashboard 1 — Revenue &amp; Genre Intelligence</div>',
                unsafe_allow_html=True)
    st.caption("Genre nào mang lại doanh thu cao nhất? Hỗ trợ quyết định lịch chiếu cuối tuần / ngày lễ.")
    st.divider()

    gdf = get_genre_stats()
    mdf = get_top_movies()
    ddf = get_decade_stats()

    # ── KPIs ──────────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Total Industry Revenue", "$549 B", "TMDB-sourced films")
    with c2: kpi("Avg Genre ROI", "2.08×")
    with c3: kpi("Profitable Films", "8,240", "revenue > budget")
    with c4: kpi("Highest-Revenue Genre", "Action", "$84.2 B cumulative")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 1: Bar + Bubble ───────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### 1.1 — Total Revenue by Genre")
        fig = px.bar(
            gdf.sort_values("total_revenue"),
            x="total_revenue", y="genre",
            orientation="h",
            color="total_revenue",
            color_continuous_scale="Reds",
            text=gdf.sort_values("total_revenue")["total_revenue"]
                .apply(lambda v: f"${v/1_000:.1f}B"),
            labels={"total_revenue": "Revenue ($M)", "genre": ""},
            template=THEME,
        )
        fig.update_traces(textposition="outside", textfont_size=10)
        fig.update_layout(**CHART_LAYOUT, coloraxis_showscale=False, height=500)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("##### 1.2 — Budget vs Revenue Bubble (size = popularity)")
        fig = px.scatter(
            gdf,
            x="avg_budget", y="avg_revenue",
            size="rating_count",
            color="genre",
            hover_name="genre",
            hover_data={"avg_roi": ":.2f", "avg_budget": ":,.0f", "avg_revenue": ":,.0f"},
            labels={"avg_budget": "Avg Budget ($M)", "avg_revenue": "Avg Revenue ($M)"},
            template=THEME,
            size_max=55,
        )
        # break-even line (revenue = budget)
        axis_max = max(gdf["avg_revenue"].max(), gdf["avg_budget"].max()) * 1.15
        fig.add_shape(type="line", x0=0, y0=0, x1=axis_max, y1=axis_max,
                      line=dict(color="rgba(255,255,255,0.25)", dash="dash", width=1.5))
        fig.add_annotation(x=axis_max * 0.85, y=axis_max * 0.82,
                           text="Break-even", font=dict(color="rgba(255,255,255,0.4)", size=10),
                           showarrow=False)
        fig.update_layout(**CHART_LAYOUT, height=500)
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 2: Line + Treemap ─────────────────────────────────────────────────
    col3, col4 = st.columns([1.3, 1])

    with col3:
        st.markdown("##### 1.3 — Avg Revenue by Decade (Top 5 Genres)")
        top5 = gdf.nlargest(5, "total_revenue")["genre"].tolist()
        fig = px.line(
            ddf[ddf["genre"].isin(top5)],
            x="decade", y="avg_revenue", color="genre",
            markers=True,
            labels={"avg_revenue": "Avg Revenue ($M)", "decade": "Decade"},
            template=THEME,
        )
        fig.update_traces(line=dict(width=2.5))
        fig.update_layout(**CHART_LAYOUT, height=380)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown("##### 1.4 — Revenue Share Treemap (color = ROI)")
        fig = px.treemap(
            gdf,
            path=["genre"],
            values="total_revenue",
            color="avg_roi",
            color_continuous_scale=["#8B0000", "#FFD700", "#006400"],
            range_color=[1.2, 2.6],
            hover_data={"avg_revenue": ":,.0f", "avg_roi": ":.2f"},
            labels={"total_revenue": "Revenue ($M)", "avg_roi": "Avg ROI"},
            template=THEME,
        )
        fig.update_layout(paper_bgcolor=PAPER, height=380,
                          margin=dict(l=0, r=0, t=32, b=0))
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 3: Top-20 Table ───────────────────────────────────────────────────
    st.markdown("##### 1.5 — Top 20 Movies by Revenue")
    disp = mdf.rename(columns={
        "title": "Film", "genres": "Genre", "year": "Year",
        "revenue": "Revenue ($M)", "budget": "Budget ($M)",
        "roi": "ROI (×)", "avg_rating": "Avg ★", "rating_count": "# Ratings",
    }).copy()
    disp["Revenue ($M)"] = disp["Revenue ($M)"].apply(lambda v: f"${v:,.0f}M")
    disp["Budget ($M)"]  = disp["Budget ($M)"].apply(lambda v: f"${v:,.0f}M")
    disp["ROI (×)"]      = disp["ROI (×)"].apply(lambda v: f"{v:.2f}×")
    disp["Avg ★"]        = disp["Avg ★"].apply(lambda v: f"{v:.2f}")
    disp["# Ratings"]    = disp["# Ratings"].apply(lambda v: f"{v/1_000:.1f}K")
    st.dataframe(disp, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# Dashboard 2 — Audience Engagement & Rating Trends
# ══════════════════════════════════════════════════════════════════════════════
elif "Audience" in page:
    st.markdown('<div class="dash-title">Dashboard 2 — Audience Engagement &amp; Rating Trends</div>',
                unsafe_allow_html=True)
    st.caption("Xu hướng đánh giá và sức hút theo thể loại — hỗ trợ điều chỉnh danh mục phim.")
    st.divider()

    gdf = get_genre_stats()
    ydf = get_year_stats()
    ddf = get_decade_stats()
    rdf = get_rating_dist()

    # ── KPIs ──────────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Total Ratings", "25,000,095")
    with c2: kpi("System Avg Rating", "3.53 ★")
    with c3: kpi("Most-Rated Genre", "Drama", "6.2 M ratings")
    with c4: kpi("Peak Activity Year", "2007", "2.35 M ratings")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 1: Avg-rating bar + Histogram ────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### 2.1 — Avg Rating by Genre (vs Global Avg)")
        global_avg = gdf["avg_rating"].mean()
        gs = gdf.sort_values("avg_rating", ascending=True)
        colors = ["#e63946" if v < global_avg else "#2a9d8f" for v in gs["avg_rating"]]
        fig = go.Figure(go.Bar(
            x=gs["avg_rating"], y=gs["genre"],
            orientation="h",
            marker_color=colors,
            text=gs["avg_rating"].apply(lambda v: f"{v:.2f}"),
            textposition="outside",
        ))
        fig.add_vline(
            x=global_avg, line_dash="dash",
            line_color="rgba(255,255,255,0.45)", line_width=1.5,
            annotation_text=f"Global avg {global_avg:.2f}",
            annotation_font_color="rgba(255,255,255,0.6)",
        )
        fig.update_layout(**CHART_LAYOUT, template=THEME, height=500,
                          xaxis=dict(range=[2.8, 4.3]), yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("##### 2.2 — Rating Distribution")
        total_ratings = rdf["frequency"].sum()
        rdf = rdf.copy()
        rdf["pct"] = (rdf["frequency"] / total_ratings * 100).round(1)
        fig = px.bar(
            rdf, x="rating", y="frequency",
            color="frequency",
            color_continuous_scale="Blues",
            text=rdf["pct"].apply(lambda v: f"{v}%"),
            labels={"rating": "Rating", "frequency": "# Ratings"},
            template=THEME,
        )
        fig.update_traces(textposition="outside", textfont_size=10)
        fig.update_xaxes(
            tickvals=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
            ticktext=["0.5", "1.0", "1.5", "2.0", "2.5", "3.0", "3.5", "4.0", "4.5", "5.0"],
        )
        fig.update_layout(**CHART_LAYOUT, coloraxis_showscale=False, height=500)
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 2: Dual-axis line + Heatmap ──────────────────────────────────────
    col3, col4 = st.columns([1.3, 1])

    with col3:
        st.markdown("##### 2.3 — Rating Activity Over Time (Dual Axis)")
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            x=ydf["rating_year"], y=ydf["rating_count"],
            name="# Ratings", marker_color=RED, opacity=0.7,
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=ydf["rating_year"], y=ydf["active_users"],
            name="Active Users", mode="lines+markers",
            line=dict(color=GOLD, width=2.5), marker=dict(size=5),
        ), secondary_y=True)
        fig.update_yaxes(title_text="# Ratings", secondary_y=False)
        fig.update_yaxes(title_text="Active Users", secondary_y=True)
        fig.update_layout(**CHART_LAYOUT, template=THEME, height=380)
        fig.update_layout(legend=dict(x=0.01, y=0.99, bgcolor="rgba(0,0,0,0.3)"))
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown("##### 2.4 — Heatmap: Genre × Decade (Avg Rating)")
        genre_subset = ["Action", "Adventure", "Animation", "Comedy", "Drama",
                        "Horror", "Romance", "Sci-Fi", "Thriller"]
        pivot = (
            ddf[ddf["genre"].isin(genre_subset)]
            .pivot_table(index="genre", columns="decade", values="avg_rating", aggfunc="mean")
            .round(2)
        )
        fig = go.Figure(go.Heatmap(
            z=pivot.values,
            x=[str(c) for c in pivot.columns],
            y=pivot.index.tolist(),
            colorscale="RdYlGn",
            zmin=2.5, zmax=4.5,
            text=pivot.values.round(2),
            texttemplate="%{text}",
            textfont=dict(size=10),
            colorbar=dict(title="★"),
        ))
        fig.update_layout(**CHART_LAYOUT, template=THEME,
                          xaxis_title="Decade", yaxis_title="", height=380)
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 3: Popularity vs Quality combo ───────────────────────────────────
    st.markdown("##### 2.5 — Popularity vs Quality per Genre")
    gc = gdf.sort_values("rating_count", ascending=False)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=gc["genre"], y=gc["rating_count"],
        name="# Ratings (Popularity)", marker_color=RED, opacity=0.72,
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=gc["genre"], y=gc["avg_rating"],
        name="Avg Rating (Quality)", mode="lines+markers",
        line=dict(color=GOLD, width=2.5), marker=dict(size=8),
    ), secondary_y=True)
    fig.update_yaxes(title_text="# Ratings", secondary_y=False)
    fig.update_yaxes(title_text="Avg Rating ★", range=[2.5, 4.5], secondary_y=True)
    fig.update_layout(**CHART_LAYOUT, template=THEME, height=380)
    fig.update_layout(legend=dict(x=0.01, y=0.99, bgcolor="rgba(0,0,0,0.3)"))
    st.plotly_chart(fig, use_container_width=True)

    # Quadrant classification table
    med_count  = gdf["rating_count"].median()
    med_rating = gdf["avg_rating"].median()

    def _quadrant(row):
        high_pop = row["rating_count"] >= med_count
        high_rat = row["avg_rating"]   >= med_rating
        if high_pop and high_rat:   return "🏆 Blockbuster — schedule prominently"
        if high_pop:                return "⚠️ Popular but mediocre — promo carefully"
        if high_rat:                return "💎 Hidden gem — target cinephiles"
        return                             "❌ Niche — limited screenings only"

    gdf["Strategy"] = gdf.apply(_quadrant, axis=1)
    st.dataframe(
        gdf[["genre", "Strategy", "avg_rating", "rating_count"]]
        .sort_values("Strategy")
        .rename(columns={"genre": "Genre", "avg_rating": "Avg ★", "rating_count": "# Ratings"}),
        use_container_width=True,
        hide_index=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# Dashboard 3 — Customer Segmentation & Recommendations
# ══════════════════════════════════════════════════════════════════════════════
else:
    st.markdown('<div class="dash-title">Dashboard 3 — Customer Segmentation &amp; ALS Recommendations</div>',
                unsafe_allow_html=True)
    st.caption("Phân khúc khách hàng & gợi ý phim cá nhân hóa — tối ưu marketing và trải nghiệm.")
    st.divider()

    seg_df  = get_user_segment_summary()
    sgp     = get_segment_genre_preference()
    tag_df  = get_tag_stats()
    rec_df  = get_segment_recommendations()

    # ── KPIs ──────────────────────────────────────────────────────────────────
    heavy_pct = 14_820 / 162_541 * 100
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Total Users", "162,541")
    with c2: kpi("VIP (Heavy) Users", f"{heavy_pct:.1f}%", "14,820 active users")
    with c3: kpi("Top User Tag", "atmospheric", "28,420 uses")
    with c4: kpi("Avg Genre Diversity", "8.3 genres/user")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 1: Donut + Grouped bar ────────────────────────────────────────────
    col1, col2 = st.columns([1, 1.6])

    with col1:
        st.markdown("##### 3.1 — User Segment Distribution")
        fig = px.pie(
            seg_df,
            names="segment", values="user_count",
            hole=0.55,
            color="segment",
            color_discrete_map={"Heavy": RED, "Medium": GOLD, "Light": GREY},
            template=THEME,
        )
        fig.update_traces(
            textposition="outside",
            textinfo="percent+label",
            textfont_size=13,
        )
        fig.update_layout(
            paper_bgcolor=PAPER,
            height=380,
            margin=dict(l=10, r=10, t=32, b=10),
            showlegend=True,
            annotations=[dict(
                text="162K<br>users",
                x=0.5, y=0.5,
                font=dict(size=15, color="white"),
                showarrow=False,
            )],
        )
        st.plotly_chart(fig, use_container_width=True)

        # compact summary table
        st.dataframe(
            seg_df.rename(columns={
                "segment": "Segment", "user_count": "# Users",
                "avg_rating": "Avg ★", "avg_movies": "Avg Films",
            }),
            use_container_width=True,
            hide_index=True,
        )

    with col2:
        st.markdown("##### 3.2 — Genre Preference by Segment (Top 8 Genres)")
        sgp8 = sgp[sgp["genre_rank"] <= 8]
        fig = px.bar(
            sgp8,
            x="genre", y="rating_count", color="segment",
            barmode="group",
            color_discrete_map={"Heavy": RED, "Medium": GOLD, "Light": GREY},
            labels={"rating_count": "# Ratings", "genre": ""},
            template=THEME,
        )
        fig.update_layout(**CHART_LAYOUT, height=480, xaxis_tickangle=-30)
        fig.update_layout(legend=dict(x=0.78, y=0.99, bgcolor="rgba(0,0,0,0.3)"))
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 2: Tag bar + Recommendations ─────────────────────────────────────
    col3, col4 = st.columns([1, 1.5])

    with col3:
        st.markdown("##### 3.3 — Top 20 User-Applied Tags")
        fig = px.bar(
            tag_df.sort_values("frequency"),
            x="frequency", y="tag",
            orientation="h",
            color="frequency",
            color_continuous_scale="Oranges",
            text=tag_df.sort_values("frequency")["frequency"].apply(lambda v: f"{v/1_000:.1f}K"),
            labels={"frequency": "# Uses", "tag": ""},
            template=THEME,
        )
        fig.update_traces(textposition="outside", textfont_size=9)
        fig.update_layout(**CHART_LAYOUT, coloraxis_showscale=False, height=510)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown("##### 3.4 — ALS Recommendations per Segment")
        seg_sel = st.selectbox(
            "Segment", ["Heavy", "Medium", "Light"], key="seg_sel",
            label_visibility="collapsed",
        )
        seg_label_map = {"Heavy": "VIP (≥200 ratings)", "Medium": "50–199 ratings", "Light": "20–49 ratings"}
        st.caption(f"Showing top-10 ALS recommendations for **{seg_sel}** users ({seg_label_map[seg_sel]})")

        disp_rec = rec_df[rec_df["segment"] == seg_sel].copy()
        disp_rec["avg_predicted_rating"] = disp_rec["avg_predicted_rating"].apply(
            lambda v: f"{v:.2f} ★"
        )
        disp_rec["recommended_to_users"] = disp_rec["recommended_to_users"].apply(
            lambda v: f"{v:,}"
        )
        st.dataframe(
            disp_rec[["rank", "title", "genres", "avg_predicted_rating", "recommended_to_users"]]
            .rename(columns={
                "rank": "#", "title": "Film", "genres": "Genre",
                "avg_predicted_rating": "Predicted ★",
                "recommended_to_users": "Users Matched",
            }),
            use_container_width=True,
            hide_index=True,
            height=430,
        )

    # ── Row 3: User activity scatter ──────────────────────────────────────────
    st.markdown("##### 3.5 — User Activity vs Genre Diversity")
    st.caption("Synthetic sample (n=2 000). X-axis log-scaled.")

    rng_s = np.random.default_rng(99)
    heavy_n, med_n, light_n = 200, 700, 1_100
    scatter_df = pd.DataFrame({
        "segment": ["Heavy"] * heavy_n + ["Medium"] * med_n + ["Light"] * light_n,
        "rating_count": np.concatenate([
            rng_s.integers(200,  1200, heavy_n),
            rng_s.integers(50,   199,  med_n),
            rng_s.integers(20,   49,   light_n),
        ]),
        "unique_genres": np.concatenate([
            rng_s.integers(10, 18, heavy_n),
            rng_s.integers(6,  15, med_n),
            rng_s.integers(3,  10, light_n),
        ]),
        "avg_rating": np.concatenate([
            np.clip(rng_s.normal(3.85, 0.30, heavy_n), 1, 5),
            np.clip(rng_s.normal(3.70, 0.35, med_n),   1, 5),
            np.clip(rng_s.normal(3.60, 0.40, light_n), 1, 5),
        ]).round(2),
    })
    fig = px.scatter(
        scatter_df,
        x="rating_count", y="unique_genres",
        color="segment",
        color_discrete_map={"Heavy": RED, "Medium": GOLD, "Light": GREY},
        opacity=0.55,
        hover_data={"avg_rating": True},
        labels={"rating_count": "Total Films Rated", "unique_genres": "Unique Genres Explored"},
        template=THEME,
        log_x=True,
    )
    fig.update_layout(**CHART_LAYOUT, height=380)
    st.plotly_chart(fig, use_container_width=True)
