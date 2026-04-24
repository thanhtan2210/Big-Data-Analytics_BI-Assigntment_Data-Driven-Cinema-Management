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
    get_user_segments_raw,
    get_kpis,
)

_kpis = get_kpis()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cinema BI Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
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
    st.markdown("**Dataset**")
    st.caption("MovieLens 25M + TMDB")
    st.caption(f"{_kpis['total_users']:,} users")
    st.caption(f"{_kpis['total_films']:,} films")
    st.caption(f"{_kpis['total_ratings']:,} ratings")
    st.divider()
    st.success("Real pipeline data loaded", icon="✅")


# ── Dashboard tabs (top-level navigation) ────────────────────────────────────
_tab1, _tab2, _tab3 = st.tabs([
    "📊 Revenue & Genre",
    "👥 Audience Engagement",
    "🎯 Customer Segmentation",
])

# ══════════════════════════════════════════════════════════════════════════════
# Dashboard 1 — Revenue & Genre Intelligence
# ══════════════════════════════════════════════════════════════════════════════
with _tab1:
    st.markdown('<div class="dash-title">Dashboard 1 — Revenue &amp; Genre Intelligence</div>',
                unsafe_allow_html=True)
    st.caption("Genre nào mang lại doanh thu cao nhất? Hỗ trợ quyết định lịch chiếu cuối tuần / ngày lễ.")
    st.divider()

    gdf = get_genre_stats()
    mdf = get_top_movies()
    ddf = get_decade_stats()

    # ── KPIs ──────────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Total Industry Revenue", f"${_kpis['total_revenue_b']:,.0f} B", "TMDB-sourced films")
    with c2: kpi("Avg Genre ROI", f"{_kpis['avg_roi']:.2f}×")
    with c3: kpi("Profitable Films", f"{_kpis['profitable_films']:,}", "revenue > budget")
    with c4: kpi("Highest-Revenue Genre", _kpis['top_genre_rev'], f"${_kpis['top_genre_rev_b']:,.0f} B cumulative")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 1a: Revenue Bar (full width) ─────────────────────────────────────
    st.markdown("##### 1.1 — Total Revenue by Genre")
    revenue_bar_df = gdf.sort_values("total_revenue").copy()
    fig = px.bar(
        revenue_bar_df,
        x="total_revenue", y="genre",
        orientation="h",
        color="total_revenue",
        color_continuous_scale="Reds",
        text=revenue_bar_df["total_revenue"]
            .apply(lambda v: f"${v/1_000:.1f}B"),
        hover_data={"movie_count": ":,.0f", "avg_roi": ":.2f", "total_revenue": ":,.0f"},
        labels={"total_revenue": "Revenue ($M)", "genre": ""},
        template=THEME,
    )
    fig.update_traces(textposition="outside", textfont_size=10)
    fig.update_layout(**CHART_LAYOUT, coloraxis_showscale=False, height=420)
    st.plotly_chart(fig, use_container_width=True)

    # ── Row 1b: Budget vs Revenue Bubble (full width) ─────────────────────────
    st.markdown("##### 1.2 — Budget vs Revenue Bubble (size = popularity)")
    scatter_gdf = gdf[
        (gdf["avg_budget"] > 0) & (gdf["avg_revenue"] > 0) & (gdf["genre"] != "[]")
    ].copy()
    # Normalize rating_count for better bubble sizing
    rating_min, rating_max = scatter_gdf["rating_count"].min(), scatter_gdf["rating_count"].max()
    scatter_gdf["bubble_size"] = 10 + 50 * (scatter_gdf["rating_count"] - rating_min) / (rating_max - rating_min) if rating_max > rating_min else 30
    fig = px.scatter(
        scatter_gdf,
        x="avg_budget", y="avg_revenue",
        size="bubble_size",
        color="genre",
        hover_name="genre",
        text="genre",
        hover_data={
            "avg_roi": ":.2f",
            "avg_budget": ":,.0f",
            "avg_revenue": ":,.0f",
            "rating_count": ":,.0f",
            "movie_count": ":,.0f",
            "bubble_size": False,
        },
        labels={"avg_budget": "Avg Budget ($M)", "avg_revenue": "Avg Revenue ($M)"},
        template=THEME,
        size_max=55,
        log_x=True,
        log_y=True,
    )
    fig.update_traces(textposition="top center", textfont_size=9)
    # Explicit log-axis range padding to spread bubbles
    _x_min = np.log10(scatter_gdf["avg_budget"].min()) - 0.4
    _x_max = np.log10(scatter_gdf["avg_budget"].max()) + 0.4
    _y_min = np.log10(scatter_gdf["avg_revenue"].min()) - 0.4
    _y_max = np.log10(scatter_gdf["avg_revenue"].max()) + 0.4
    fig.update_xaxes(range=[_x_min, _x_max])
    fig.update_yaxes(range=[_y_min, _y_max])
    # break-even line: use actual data range (x0=0 is invisible on log scale)
    x_lo = scatter_gdf["avg_budget"].min() * 0.8
    x_hi = scatter_gdf["avg_budget"].max() * 1.5
    fig.add_shape(type="line", x0=x_lo, y0=x_lo, x1=x_hi, y1=x_hi,
                  line=dict(color="rgba(255,255,255,0.25)", dash="dash", width=1.5))
    fig.add_annotation(x=x_hi * 0.7, y=x_hi * 0.55,
                       text="Break-even", font=dict(color="rgba(255,255,255,0.4)", size=10),
                       showarrow=False)
    fig.update_layout(**CHART_LAYOUT, height=580)
    st.plotly_chart(fig, use_container_width=True)

    # ── Row 2: Line + Treemap ─────────────────────────────────────────────────
    col3, col4 = st.columns([1.3, 1])

    with col3:
        st.markdown("##### 1.3 — Avg Revenue by Decade (Top 5 Genres)")
        top5 = gdf.nlargest(5, "total_revenue")["genre"].tolist()
        line_df = ddf[(ddf["genre"].isin(top5)) & (ddf["avg_revenue"] > 0)].copy()
        line_df["decade"] = pd.to_numeric(line_df["decade"], errors="coerce")
        line_df = line_df.dropna(subset=["decade"]).sort_values("decade")
        if len(line_df) > 0:
            fig = px.line(
                line_df,
                x="decade", y="avg_revenue", color="genre",
                markers=True,
                labels={"avg_revenue": "Avg Revenue ($M)", "decade": "Decade"},
                template=THEME,
            )
            fig.update_traces(line=dict(width=2.5))
            fig.update_layout(**CHART_LAYOUT, height=380)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("⏳ Đang chờ dữ liệu từ Task 3 — `decade_genre_heatmap.csv` chưa có `avg_revenue` hợp lệ. Cột này cần được bổ sung bởi pipeline Task 3.")

    with col4:
        st.markdown("##### 1.4 — Revenue Share Treemap (color = ROI)")
        fig = px.treemap(
            gdf,
            path=["genre"],
            values="total_revenue",
            color="avg_roi",
            color_continuous_scale=["#8B0000", "#FFD700", "#006400"],
            range_color=[1.2, 2.6],
            hover_data={
                "movie_count": ":,.0f",
                "avg_revenue": ":,.0f",
                "avg_budget": ":,.0f",
                "avg_roi": ":.2f",
            },
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
        "roi": "ROI (%)", "avg_rating": "Avg ★", "rating_count": "# Ratings",
    }).copy()
    disp["Revenue ($M)"] = disp["Revenue ($M)"].apply(lambda v: f"${v:,.0f}M")
    disp["Budget ($M)"]  = disp["Budget ($M)"].apply(lambda v: f"${v:,.0f}M")
    disp["ROI (%)"]      = disp["ROI (%)"].apply(lambda v: f"{v * 100:.1f}%")
    disp["Avg ★"]        = disp["Avg ★"].apply(lambda v: f"{v:.2f}")
    disp["# Ratings"]    = disp["# Ratings"].apply(lambda v: f"{v/1_000:.1f}K")
    # Drop Year column if all values are 'N/A' (missing data in source)
    if disp["Year"].nunique() == 1 and disp["Year"].iloc[0] == "N/A":
        st.caption("⚠️ *Year data not available in source (movies_enriched.csv missing year for top revenue films).*")
        disp = disp.drop(columns=["Year"])
    st.dataframe(disp, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# Dashboard 2 — Audience Engagement & Rating Trends
# ══════════════════════════════════════════════════════════════════════════════
with _tab2:
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
    with c1: kpi("Total Ratings", f"{_kpis['total_ratings']:,}")
    with c2: kpi("System Avg Rating", f"{_kpis['avg_rating']:.2f} ★")
    with c3: kpi("Most-Rated Genre", _kpis['top_genre_count'], f"{_kpis['top_genre_count_m']:.1f} M ratings")
    with c4: kpi("Active Users (Recent 3Y*)", f"{_kpis['recent_active_users_3y_sum']:,}", _kpis['recent_active_year_window'])
    st.caption("* Sum of yearly distinct active users in the latest 3-year window from `year_stats.csv`.")

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
            customdata=np.column_stack((gs["rating_count"], gs["avg_rating"] - global_avg)),
            text=gs["avg_rating"].apply(lambda v: f"{v:.2f}"),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Avg rating: %{x:.2f} ★<br># Ratings: %{customdata[0]:,.0f}<br>vs global: %{customdata[1]:+.2f}<extra></extra>",
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
        fig.update_traces(
            textposition="outside",
            textfont_size=10,
            customdata=np.column_stack((rdf["pct"],)),
            hovertemplate="Rating: %{x:.1f}<br># Ratings: %{y:,.0f}<br>Share: %{customdata[0]:.1f}%<extra></extra>",
        )
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
            customdata=np.column_stack((ydf["active_users"], ydf["avg_rating"])),
            hovertemplate="Year: %{x}<br># Ratings: %{y:,.0f}<br>Active users: %{customdata[0]:,.0f}<br>Avg rating: %{customdata[1]:.2f} ★<extra></extra>",
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=ydf["rating_year"], y=ydf["active_users"],
            name="Active Users", mode="lines+markers",
            line=dict(color=GOLD, width=2.5), marker=dict(size=5),
            customdata=np.column_stack((ydf["rating_count"], ydf["avg_rating"])),
            hovertemplate="Year: %{x}<br>Active users: %{y:,.0f}<br># Ratings: %{customdata[0]:,.0f}<br>Avg rating: %{customdata[1]:.2f} ★<extra></extra>",
        ), secondary_y=True)
        fig.update_yaxes(title_text="# Ratings", secondary_y=False)
        fig.update_yaxes(title_text="Active Users", secondary_y=True)
        fig.update_layout(**CHART_LAYOUT, template=THEME, height=380)
        fig.update_layout(legend=dict(x=0.01, y=0.99, bgcolor="rgba(0,0,0,0.3)"))
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown("##### 2.4 — Heatmap: Genre × Decade (Avg Rating)")
        heat_df = ddf[ddf["rating_count"] >= 100].copy()
        if len(heat_df) == 0:
            st.info("⏳ Đang chờ dữ liệu từ Task 3 — `decade_genre_heatmap.csv` chưa có ô nào đạt rating_count ≥ 100. Cần pipeline chạy trên full data.")
        else:
            pivot = heat_df.pivot_table(index="genre", columns="decade", values="avg_rating", aggfunc="mean")
            pivot_count = heat_df.pivot_table(index="genre", columns="decade", values="rating_count", aggfunc="mean")
            pivot = pivot.sort_index().round(2)
            pivot_count = pivot_count.reindex(index=pivot.index, columns=pivot.columns)
            fig = go.Figure(go.Heatmap(
                z=pivot.values,
                x=[str(c) for c in pivot.columns],
                y=pivot.index.tolist(),
                colorscale="RdYlGn",
                zmin=2.5, zmax=4.5,
                customdata=pivot_count.values,
                hovertemplate="Genre: %{y}<br>Decade: %{x}<br>Avg rating: %{z:.2f} ★<br># Ratings: %{customdata:,.0f}<extra></extra>",
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
with _tab3:
    st.markdown('<div class="dash-title">Dashboard 3 — Customer Segmentation &amp; ALS Recommendations</div>',
                unsafe_allow_html=True)
    st.caption("Phân khúc khách hàng & gợi ý phim cá nhân hóa — tối ưu marketing và trải nghiệm.")
    st.divider()

    seg_df  = get_user_segment_summary()
    sgp     = get_segment_genre_preference()
    tag_df  = get_tag_stats()
    rec_df  = get_segment_recommendations()
    has_multiple_segments = _kpis["segment_count"] > 1

    if not has_multiple_segments:
        st.warning(
            "Task 3 export currently contains only the `Heavy` segment. Comparative segment charts remain visible, "
            "but Medium/Light behavior cannot be analyzed until the pipeline output is regenerated.",
            icon="⚠️",
        )

    # ── KPIs ──────────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Total Users", f"{_kpis['total_users']:,}")
    with c2: kpi("VIP (Heavy) Users", f"{_kpis['heavy_pct']:.1f}%", f"{_kpis['heavy_count']:,} active users")
    with c3: kpi("Top User Tag", _kpis['top_tag'], f"{_kpis['top_tag_freq']:,} uses")
    with c4: kpi("Avg Films Rated/User", f"{_kpis['avg_unique_movies']:.1f}")

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
            custom_data=["avg_rating", "avg_movies"],
            template=THEME,
        )
        fig.update_traces(
            textposition="outside",
            textinfo="percent+label",
            textfont_size=13,
            hovertemplate="Segment: %{label}<br>Users: %{value:,.0f}<br>Share: %{percent}<br>Avg rating: %{customdata[0]:.2f} ★<br>Avg unique films rated: %{customdata[1]:.1f}<extra></extra>",
        )
        fig.update_layout(
            paper_bgcolor=PAPER,
            height=380,
            margin=dict(l=10, r=10, t=32, b=10),
            showlegend=True,
            annotations=[dict(
                text=f"{_kpis['total_users'] // 1000}K<br>users",
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
        st.markdown("##### 3.2 — Genre Preference by Segment (Top 10 Genres)")
        sgp10 = sgp[sgp["genre_rank"] <= 10]
        fig = px.bar(
            sgp10,
            x="genre", y="rating_count", color="segment",
            barmode="group",
            color_discrete_map={"Heavy": RED, "Medium": GOLD, "Light": GREY},
            hover_data={"avg_rating": ":.2f", "genre_rank": True},
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
        tag_plot_df = tag_df.sort_values("frequency").copy()
        tag_total = tag_df["frequency"].sum()
        tag_plot_df["pct"] = tag_plot_df["frequency"] / tag_total * 100 if tag_total else 0.0
        fig = px.bar(
            tag_plot_df,
            x="frequency", y="tag",
            orientation="h",
            color="frequency",
            color_continuous_scale="Oranges",
            text=tag_plot_df["frequency"].apply(lambda v: f"{v/1_000:.1f}K"),
            labels={"frequency": "# Uses", "tag": ""},
            template=THEME,
        )
        fig.update_traces(
            textposition="outside",
            textfont_size=9,
            customdata=np.column_stack((tag_plot_df["pct"],)),
            hovertemplate="Tag: %{y}<br># Uses: %{x:,.0f}<br>Share: %{customdata[0]:.2f}%<extra></extra>",
        )
        fig.update_layout(**CHART_LAYOUT, coloraxis_showscale=False, height=510)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown("##### 3.4 — ALS Recommendations per Segment")
        _avail_segs = sorted(rec_df["segment"].unique().tolist()) if len(rec_df) > 0 else ["Heavy"]
        seg_sel = st.selectbox(
            "Segment", _avail_segs, key="seg_sel",
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
    _raw = get_user_segments_raw()
    if "unique_genres_rated" not in _raw.columns:
        st.info("⏳ Đang chờ dữ liệu từ Task 3 — `user_segments.csv` chưa có cột `unique_genres_rated`. Cần bổ sung để hiển thị chart này.")
    else:
        scatter_df = _raw.sample(n=min(2_000, len(_raw)), random_state=42)
        fig = px.scatter(
            scatter_df,
            x="rating_count", y="unique_genres_rated",
            color="segment",
            color_discrete_map={"Heavy": RED, "Medium": GOLD, "Light": GREY},
            opacity=0.55,
            hover_data={"userId": True, "avg_rating": ":.2f"},
            labels={"rating_count": "Total Films Rated", "unique_genres_rated": "Unique Genres Rated"},
            template=THEME,
            log_x=True,
        )
        fig.update_layout(**CHART_LAYOUT, height=380)
        st.plotly_chart(fig, use_container_width=True)
