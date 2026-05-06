import streamlit as st
import pandas as pd
import pymongo
from pymongo import MongoClient
import plotly.express as px
import os
import re

@st.cache_resource
def get_mongo_client():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
    return MongoClient(mongo_uri)

@st.cache_data(ttl=3600)
def load_batch_data_cached():
    """Load and aggregate batch data from MongoDB (Cached)"""
    client = get_mongo_client()
    mongo_db = os.getenv("MONGO_DB", "cinema_dw")
    db = client[mongo_db]
    
    # 1. Basic Stats
    total_movies = db.movies.count_documents({})
    total_ratings = db.ratings.count_documents({})
    
    # 2. Fetch movies for BI analytics
    # Limit to 10000 for a good historical overview without killing performance
    bi_cursor = db.movies.find(
        {"ml_rating_count": {"$gt": 0}}, 
        {"title": 1, "genres": 1, "ml_avg_rating": 1, "ml_rating_count": 1, "_id": 0}
    ).sort("ml_rating_count", pymongo.DESCENDING).limit(10000)
    bi_df = pd.DataFrame(list(bi_cursor))
    
    # 3. Fetch revenue data
    rev_cursor = db.revenue.find({}, {"movieId": 1, "revenue": 1, "release_date": 1, "_id": 0})
    rev_df = pd.DataFrame(list(rev_cursor))
    
    return total_movies, total_ratings, bi_df, rev_df

def render_batch_dashboard():
    st.markdown("<h1>📊 Cinema Historical Batch Analytics</h1>", unsafe_allow_html=True)
    st.markdown('<div class="batch-badge">STRATEGIC HISTORICAL DATA</div>', unsafe_allow_html=True)
    st.markdown("Phân tích xu hướng lịch sử giúp định hướng chiến lược dài hạn cho rạp chiếu phim.")
    
    with st.spinner("Đang tính toán dữ liệu lịch sử..."):
        try:
            total_movies, total_ratings, bi_df, rev_df = load_batch_data_cached()
        except Exception as e:
            st.error(f"Cannot connect to MongoDB. Error: {e}")
            return
            
    # Metrics Summary
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tổng phim xử lý", f"{total_movies:,}")
    m2.metric("Tổng lượt đánh giá", f"{total_ratings:,}")
    m3.metric("Nguồn dữ liệu", "HDFS (MovieLens+TMDB)")
    m4.metric("Loại hình", "Batch Processing")

    st.markdown("---")

    if bi_df.empty:
        st.info("Chưa có dữ liệu batch. Hãy chạy script preprocessing.")
        return

    # Data Preparation: Extract Year and Decade
    # From MovieLens titles: "Title (Year)"
    bi_df['year'] = bi_df['title'].str.extract(r'\((\d{4})\)').astype(float)
    bi_df['decade'] = (bi_df['year'] // 10 * 10).fillna(0).astype(int)
    
    # Filter out invalid decades (e.g., 0 or future)
    bi_df = bi_df[(bi_df['decade'] >= 1900) & (bi_df['decade'] <= 2030)]

    # From Revenue release_date: "YYYY-MM-DD"
    if not rev_df.empty:
        rev_df['year'] = pd.to_datetime(rev_df['release_date'], errors='coerce').dt.year
        rev_df['decade'] = (rev_df['year'] // 10 * 10).fillna(0).astype(int)
        rev_df = rev_df[(rev_df['decade'] >= 1900) & (rev_df['decade'] <= 2030)]

    # ── Section 1: Historical Trends (The "Big Picture") ──
    st.header("⏳ Xu hướng qua các Thập kỷ")
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        # Trend: Number of Ratings over Decades
        st.subheader("📈 Lượng quan tâm theo thời gian")
        st.caption("Tổng số lượt đánh giá của các phim theo thập kỷ sản xuất")
        decade_ratings = bi_df.groupby('decade')['ml_rating_count'].sum().reset_index()
        fig_traffic = px.line(decade_ratings, x='decade', y='ml_rating_count', 
                             markers=True, labels={'decade': 'Thập kỷ', 'ml_rating_count': 'Tổng lượt đánh giá'})
        fig_traffic.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#c9d1d9')
        st.plotly_chart(fig_traffic, width='stretch')

    with col_t2:
        # Trend: Quality (Avg Rating) over Decades
        st.subheader("⭐ Chất lượng phim theo thời gian")
        st.caption("Điểm đánh giá trung bình (có trọng số) qua các thập kỷ")
        # Weighted average
        decade_quality = bi_df.groupby('decade').apply(
            lambda x: (x['ml_avg_rating'] * x['ml_rating_count']).sum() / x['ml_rating_count'].sum()
        ).reset_index()
        decade_quality.columns = ['decade', 'avg_rating']
        fig_quality = px.line(decade_quality, x='decade', y='avg_rating', 
                             markers=True, color_discrete_sequence=['#8957e5'],
                             labels={'decade': 'Thập kỷ', 'avg_rating': 'Rating TB'})
        fig_quality.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#c9d1d9', yaxis=dict(range=[0, 5]))
        st.plotly_chart(fig_quality, width='stretch')

    # Trend: Revenue over Decades
    if not rev_df.empty:
        st.subheader("💰 Tổng Doanh Thu mỗi Thập kỷ")
        st.caption("Giúp rạp hiểu được quy mô thị trường của phim các thời đại khác nhau")
        decade_rev = rev_df.groupby('decade')['revenue'].sum().reset_index()
        decade_rev['revenue_B'] = decade_rev['revenue'] / 1e9 # Convert to Billions
        fig_rev = px.bar(decade_rev, x='decade', y='revenue_B', 
                        color='revenue_B', color_continuous_scale='Greens',
                        labels={'decade': 'Thập kỷ', 'revenue_B': 'Tổng doanh thu (tỷ $)'})
        fig_rev.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#c9d1d9')
        st.plotly_chart(fig_rev, width='stretch')

    st.markdown("---")

    # ── Section 2: Genre Evolution ──
    st.header("🎭 Sự thay đổi về Thể loại yêu thích")
    
    # Explode genres by decade
    genre_decade_df = bi_df[['decade', 'genres', 'ml_rating_count']].copy()
    genre_decade_df = genre_decade_df.assign(genre=genre_decade_df['genres'].str.split('|')).explode('genre')
    genre_decade_df = genre_decade_df[genre_decade_df['genre'] != 'Unknown']
    
    # Group to see how genres evolved in popularity (by rating count)
    genre_evo = genre_decade_df.groupby(['decade', 'genre'])['ml_rating_count'].sum().reset_index()
    
    # Filter to top 5 genres overall to keep the chart clean
    top_overall_genres = genre_evo.groupby('genre')['ml_rating_count'].sum().sort_values(ascending=False).head(5).index.tolist()
    genre_evo_filtered = genre_evo[genre_evo['genre'].isin(top_overall_genres)]
    
    st.subheader("🔝 Top 5 Thể loại phổ biến nhất qua các thời kỳ")
    st.caption("Theo dõi sự thay đổi thị hiếu khán giả qua từng thập kỷ")
    fig_evo = px.area(genre_evo_filtered, x='decade', y='ml_rating_count', color='genre',
                      labels={'decade': 'Thập kỷ', 'ml_rating_count': 'Lượt đánh giá', 'genre': 'Thể loại'},
                      color_discrete_sequence=px.colors.qualitative.Safe)
    fig_evo.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#c9d1d9')
    st.plotly_chart(fig_evo, width='stretch')

    st.markdown("---")

    # ── Section 3: Content Insights ──
    st.header("🔍 Đặc điểm nội dung")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Phân bổ Thể loại")
        # Current snapshot genre distribution
        genre_counts = genre_decade_df['genre'].value_counts().reset_index().head(10)
        genre_counts.columns = ['Genre', 'Count']
        fig_pie = px.pie(genre_counts, values='Count', names='Genre', hole=0.4,
                         color_discrete_sequence=px.colors.sequential.Plasma)
        fig_pie.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#c9d1d9')
        st.plotly_chart(fig_pie, width='stretch')

    with c2:
        st.subheader("Phân bổ Điểm đánh giá")
        fig_hist = px.histogram(bi_df, x="ml_avg_rating", nbins=20,
                               color_discrete_sequence=['#58a6ff'],
                               labels={"ml_avg_rating": "Điểm TB", "count": "Số lượng phim"})
        fig_hist.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#c9d1d9', yaxis_title="Số lượng phim")
        st.plotly_chart(fig_hist, width='stretch')
