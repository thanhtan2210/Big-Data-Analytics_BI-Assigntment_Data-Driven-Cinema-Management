import streamlit as st
import pandas as pd
import pymongo
from pymongo import MongoClient
import plotly.express as px
import os

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
    
    total_movies = db.movies.count_documents({})
    total_ratings = db.ratings.count_documents({})
    
    # Fetch top 10 movies
    top_movies_cursor = db.movies.find().sort("ml_rating_count", pymongo.DESCENDING).limit(10)
    top_movies = pd.DataFrame(list(top_movies_cursor))
    
    # Fetch dataset for BI analytics (movies with ratings, limit to 5000 to keep UI extremely fast)
    bi_cursor = db.movies.find(
        {"ml_rating_count": {"$gt": 0}}, 
        {"title": 1, "genres": 1, "ml_avg_rating": 1, "ml_rating_count": 1, "_id": 0}
    ).sort("ml_rating_count", pymongo.DESCENDING).limit(5000)
    
    bi_df = pd.DataFrame(list(bi_cursor))
    
    return total_movies, total_ratings, top_movies, bi_df

def render_batch_dashboard():
    st.markdown("<h1>📊 Batch Analytics Dashboard</h1>", unsafe_allow_html=True)
    st.markdown('<div class="batch-badge">STATIC BATCH DATA</div>', unsafe_allow_html=True)
    st.markdown("Dữ liệu tổng hợp từ hệ thống HDFS thông qua PySpark Batch Processing.")
    with st.spinner("Loading batch analytics..."):
        try:
            total_movies, total_ratings, top_movies_df, bi_df = load_batch_data_cached()
            
            # Calculate global average rating
            global_avg_rating = 0
            if not bi_df.empty:
                global_avg_rating = (bi_df['ml_avg_rating'] * bi_df['ml_rating_count']).sum() / bi_df['ml_rating_count'].sum()
                
        except Exception as e:
            st.error(f"Cannot connect to MongoDB. Is it running? Error: {e}")
            return
            
    # Top Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Movies Processed", f"{total_movies:,}")
    with col2:
        st.metric("Total Ratings Processed", f"{total_ratings:,}")
    with col3:
        st.metric("Global Avg Rating", f"{global_avg_rating:.2f} ⭐" if global_avg_rating else "N/A")
    with col4:
        st.metric("Data Source", "MovieLens + TMDB")
        
    st.markdown("---")
    
    # --- BI Analytics Section ---
    if not bi_df.empty:
        bi_df['title'] = bi_df['title'].fillna('Unknown Title')
        bi_df['ml_rating_count'] = bi_df['ml_rating_count'].fillna(0)
        bi_df['ml_avg_rating'] = bi_df['ml_avg_rating'].fillna(0)
        bi_df['genres'] = bi_df['genres'].fillna('Unknown')
        
        # 1. Top 10 Most Rated Movies
        st.subheader("🏆 Top 10 Most Rated Movies")
        chart_data = top_movies_df.sort_values("ml_rating_count", ascending=True)
        fig_top = px.bar(
            chart_data, 
            x="ml_rating_count", 
            y="title", 
            orientation='h',
            color="ml_avg_rating",
            color_continuous_scale="Viridis",
            labels={"ml_rating_count": "Number of Ratings", "title": "Movie Title", "ml_avg_rating": "Avg Rating"}
        )
        fig_top.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#c9d1d9', margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_top, width='stretch')
        
        st.markdown("---")
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # 2. Genre Distribution (Pie Chart)
            st.subheader("🎭 Movie Genre Distribution")
            
            # Split genres and explode to count each genre individually
            genres_series = bi_df['genres'].str.split('|').explode()
            genre_counts = genres_series.value_counts().reset_index()
            genre_counts.columns = ['Genre', 'Count']
            # Limit to top 10 genres for readability
            top_genres = genre_counts.head(10)
            
            fig_pie = px.pie(
                top_genres,
                values='Count',
                names='Genre',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Plasma
            )
            fig_pie.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#c9d1d9', margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_pie, width='stretch')
            
        with col_chart2:
            # 3. Rating Distribution (Histogram)
            st.subheader("📈 Rating Distribution")
            
            fig_hist = px.histogram(
                bi_df, 
                x="ml_avg_rating", 
                nbins=20,
                color_discrete_sequence=['#58a6ff'],
                labels={"ml_avg_rating": "Average Rating", "count": "Number of Movies"}
            )
            fig_hist.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#c9d1d9', margin=dict(l=0, r=0, t=30, b=0), yaxis_title="Number of Movies")
            st.plotly_chart(fig_hist, width='stretch')
            
        st.markdown("---")
        
        # 4. Engagement vs Quality (Scatter)
        st.subheader("💡 Engagement vs. Quality")
        st.markdown("Does higher engagement (rating counts) correlate with better quality (average rating)?")
        
        fig_scatter = px.scatter(
            bi_df, 
            x="ml_avg_rating", 
            y="ml_rating_count",
            hover_data=["title"],
            color="ml_avg_rating",
            color_continuous_scale="Turbo",
            opacity=0.7,
            labels={"ml_avg_rating": "Average Rating", "ml_rating_count": "Number of Ratings"}
        )
        fig_scatter.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#c9d1d9', margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_scatter, width='stretch')
            
    else:
        st.info("No data found in 'movies' collection. Please run the preprocessing script.")
