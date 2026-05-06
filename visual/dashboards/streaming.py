import streamlit as st
import pandas as pd
import pymongo
from pymongo import MongoClient
import plotly.express as px
import os
import time
from datetime import datetime

@st.cache_resource
def get_mongo_client():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
    return MongoClient(mongo_uri)

@st.cache_data(ttl=300)
def load_movies_lookup():
    """Load movie title and genre mapping from MongoDB (cached 5 mins)."""
    client = get_mongo_client()
    mongo_db = os.getenv("MONGO_DB", "cinema_dw")
    db = client[mongo_db]
    cursor = db["movies"].find({}, {"movieId": 1, "title": 1, "genres": 1, "_id": 0})
    df = pd.DataFrame(list(cursor))
    return df if not df.empty else pd.DataFrame(columns=["movieId", "title", "genres"])

def load_stream_data(db):
    """Load per-movie streaming stats for Top-10 BI analytics."""
    try:
        # ── KPI: Cumulative totals from window metrics ──
        kpi_pipeline = [{"$group": {
            "_id": None,
            "total_ratings": {"$sum": "$total_ratings_in_window"},
            "total_revenue":  {"$sum": "$revenue_in_window"}
        }}]
        kpi = list(db["live_metrics"].aggregate(kpi_pipeline))
        cumulative_ratings = kpi[0]["total_ratings"] if kpi else 0
        cumulative_revenue = kpi[0]["total_revenue"] if kpi else 0

        # Latest window for current traffic
        latest_window = db["live_metrics"].find_one(sort=[("window_start", pymongo.DESCENDING)])
        current_traffic = int(latest_window.get("total_ratings_in_window", 0)) if latest_window else 0
        current_avg_rating = latest_window.get("avg_rating_in_window", 0) if latest_window else 0

        # ── Per-movie aggregation from live_movie_stats ──
        movie_pipeline = [
            {"$group": {
                "_id": "$movieId",
                "total_ratings": {"$sum": "$rating_count"},
                "total_rating_sum": {"$sum": "$rating_sum"},
                "movie_revenue":  {"$last": "$movie_revenue"}
            }},
            {"$addFields": {
                "avg_rating": {"$cond": [
                    {"$gt": ["$total_ratings", 0]},
                    {"$divide": ["$total_rating_sum", "$total_ratings"]},
                    0
                ]}
            }},
            {"$match": {"_id": {"$ne": None}}}
        ]
        movie_docs = list(db["live_movie_stats"].aggregate(movie_pipeline))
        movie_df = pd.DataFrame(movie_docs)
        if not movie_df.empty:
            movie_df = movie_df.rename(columns={"_id": "movieId"})

        return cumulative_ratings, cumulative_revenue, current_traffic, current_avg_rating, movie_df
    except Exception as e:
        st.error(f"Error: {e}")
        return 0, 0, 0, 0, pd.DataFrame()

def render_streaming_dashboard():
    st.markdown("<h1>🎬 Live Cinema Intelligence Dashboard</h1>", unsafe_allow_html=True)
    st.markdown('<div class="live-badge">🟢 REAL-TIME</div>', unsafe_allow_html=True)
    st.caption(f"Cập nhật lúc: {datetime.now().strftime('%H:%M:%S')} — Dữ liệu giúp rạp chiếu quyết định chiếu phim nào ngay hôm nay")

    client = get_mongo_client()
    mongo_db = os.getenv("MONGO_DB", "cinema_dw")
    db = client[mongo_db]

    cumulative_ratings, cumulative_revenue, current_traffic, current_avg_rating, movie_df = load_stream_data(db)
    movies_lookup = load_movies_lookup()

    # ── KPI Row using custom HTML to prevent truncation ──
    st.markdown("""
        <style>
        .kpi-container {
            display: flex;
            justify-content: space-between;
            background-color: #161b22;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #30363d;
            margin-bottom: 20px;
        }
        .kpi-box {
            flex: 1;
            text-align: center;
            border-right: 1px solid #30363d;
        }
        .kpi-box:last-child {
            border-right: none;
        }
        .kpi-label {
            color: #8b949e;
            font-size: 0.9rem;
            margin-bottom: 5px;
        }
        .kpi-value {
            color: #ffffff;
            font-size: 1.8rem;
            font-weight: bold;
            word-break: break-all;
        }
        .kpi-delta {
            color: #3fb950;
            font-size: 0.8rem;
            margin-top: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

    html_kpis = f"""
    <div class="kpi-container">
        <div class="kpi-box">
            <div class="kpi-label">📊 Tổng Lượt Đánh Giá</div>
            <div class="kpi-value">{int(cumulative_ratings):,}</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-label">💰 Doanh Thu Tích Lũy</div>
            <div class="kpi-value">${int(cumulative_revenue):,}</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-label">⚡ Traffic Hiện Tại</div>
            <div class="kpi-value">{current_traffic:,}</div>
            <div class="kpi-delta">▲ Live (/5s)</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-label">⭐ Rating TB Hiện Tại</div>
            <div class="kpi-value">{f"{current_avg_rating:.2f}" if current_avg_rating else "—"}</div>
        </div>
    </div>
    """
    st.markdown(html_kpis, unsafe_allow_html=True)

    st.markdown("---")

    if movie_df.empty or movies_lookup.empty:
        st.info("⏳ Đang chờ dữ liệu streaming... Hãy đảm bảo Kafka Producer và PySpark Streaming đang chạy.")
        time.sleep(1)
        st.rerun()
        return

    # Merge với movies lookup để lấy title và genres
    merged = movie_df.merge(movies_lookup, on="movieId", how="left")
    merged["title"] = merged["title"].fillna("Unknown")
    merged["genres"] = merged["genres"].fillna("Unknown")
    merged["movie_revenue"] = merged["movie_revenue"].fillna(0)

    # ── 4 Top-10 Charts in 2×2 grid ──
    col_left, col_right = st.columns(2)

    # ── Chart 1: Top 10 phim doanh thu cao nhất (đang trending) ──
    with col_left:
        st.subheader("💰 Top 10 Phim Có Doanh Thu Cao Nhất")
        st.caption("Trong số các phim đang được đánh giá — giúp rạp ưu tiên chiếu phim blockbuster")
        top_rev = (merged[merged["movie_revenue"] > 0]
                   .sort_values("movie_revenue", ascending=False)
                   .head(10))
        if not top_rev.empty:
            top_rev["revenue_B"] = top_rev["movie_revenue"] / 1e6
            top_rev["short_title"] = top_rev["title"].str[:30]
            fig1 = px.bar(
                top_rev.sort_values("revenue_B"),
                x="revenue_B", y="short_title", orientation="h",
                color="revenue_B",
                color_continuous_scale="Plasma",
                labels={"revenue_B": "Doanh Thu (triệu $)", "short_title": ""},
            )
            fig1.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font_color="#c9d1d9", margin=dict(l=0, r=20, t=10, b=0),
                showlegend=False, coloraxis_showscale=False
            )
            st.plotly_chart(fig1, width="stretch")
        else:
            st.info("Chưa có dữ liệu doanh thu.")

    # ── Chart 2: Top 10 thể loại doanh thu cao nhất ──
    with col_right:
        st.subheader("🎭 Top 10 Thể Loại Có Doanh Thu Cao Nhất")
        st.caption("Thể loại phim nào đang đóng góp doanh thu lớn nhất cho rạp")
        genre_df = merged[merged["movie_revenue"] > 0].copy()
        genre_df = genre_df.assign(genre=genre_df["genres"].str.split("|")).explode("genre")
        genre_df = genre_df[genre_df["genre"] != "Unknown"]
        genre_rev = (genre_df.groupby("genre")["movie_revenue"]
                     .sum().reset_index()
                     .sort_values("movie_revenue", ascending=False)
                     .head(10))
        if not genre_rev.empty:
            genre_rev["revenue_B"] = genre_rev["movie_revenue"] / 1e6
            fig2 = px.bar(
                genre_rev.sort_values("revenue_B"),
                x="revenue_B", y="genre", orientation="h",
                color="revenue_B",
                color_continuous_scale="Viridis",
                labels={"revenue_B": "Tổng Doanh Thu (triệu $)", "genre": ""}
            )
            fig2.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font_color="#c9d1d9", margin=dict(l=0, r=20, t=10, b=0),
                showlegend=False, coloraxis_showscale=False
            )
            st.plotly_chart(fig2, width="stretch")
        else:
            st.info("Chưa có dữ liệu thể loại.")

    st.markdown("---")
    col_left2, col_right2 = st.columns(2)

    # ── Chart 3: Top 10 phim được rating cao nhất ──
    with col_left2:
        st.subheader("⭐ Top 10 Phim Được Rating Cao Nhất")
        st.caption("Phim nào đang được khán giả đánh giá cao nhất ngay lúc này")
        top_rating = (merged[merged["total_ratings"] >= 5]  # Lọc phim có ít nhất 5 rating
                      .sort_values("avg_rating", ascending=False)
                      .head(10))
        if not top_rating.empty:
            top_rating["short_title"] = top_rating["title"].str[:30]
            fig3 = px.bar(
                top_rating.sort_values("avg_rating"),
                x="avg_rating", y="short_title", orientation="h",
                color="avg_rating",
                color_continuous_scale="RdYlGn",
                range_color=[1, 5],
                labels={"avg_rating": "Rating Trung Bình (⭐)", "short_title": ""}
            )
            fig3.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font_color="#c9d1d9", margin=dict(l=0, r=20, t=10, b=0),
                showlegend=False, coloraxis_showscale=False,
                xaxis=dict(range=[0, 5])
            )
            st.plotly_chart(fig3, width="stretch")
        else:
            st.info("Chưa đủ dữ liệu (cần ≥5 ratings/phim).")

    # ── Chart 4: Top 10 thể loại được rating cao nhất ──
    with col_right2:
        st.subheader("🏆 Top 10 Thể Loại Được Rating Cao Nhất")
        st.caption("Thể loại nào đang được khán giả yêu thích — cơ sở để lên lịch chiếu")
        genre_df2 = merged[merged["total_ratings"] > 0].copy()
        genre_df2 = genre_df2.assign(genre=genre_df2["genres"].str.split("|")).explode("genre")
        genre_df2 = genre_df2[genre_df2["genre"] != "Unknown"]
        genre_rating = (genre_df2.groupby("genre")
                        .apply(lambda g: pd.Series({
                            "weighted_sum": (g["avg_rating"] * g["total_ratings"]).sum(),
                            "total_ratings": g["total_ratings"].sum()
                        })).reset_index())
        genre_rating["avg_rating"] = genre_rating["weighted_sum"] / genre_rating["total_ratings"]
        genre_rating = genre_rating[genre_rating["total_ratings"] >= 10].sort_values("avg_rating", ascending=False).head(10)
        if not genre_rating.empty:
            fig4 = px.bar(
                genre_rating.sort_values("avg_rating"),
                x="avg_rating", y="genre", orientation="h",
                color="avg_rating",
                color_continuous_scale="RdYlGn",
                range_color=[1, 5],
                labels={"avg_rating": "Rating Trung Bình (⭐)", "genre": ""}
            )
            fig4.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font_color="#c9d1d9", margin=dict(l=0, r=20, t=10, b=0),
                showlegend=False, coloraxis_showscale=False,
                xaxis=dict(range=[0, 5])
            )
            st.plotly_chart(fig4, width="stretch")
        else:
            st.info("Chưa đủ dữ liệu thể loại.")

    # Auto-refresh every 5 seconds
    time.sleep(5)
    st.rerun()
