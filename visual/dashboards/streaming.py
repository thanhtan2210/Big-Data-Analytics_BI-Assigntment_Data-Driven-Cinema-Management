import streamlit as st
import pandas as pd
import pymongo
from pymongo import MongoClient
import plotly.express as px
import os
import time

@st.cache_resource
def get_mongo_client():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
    return MongoClient(mongo_uri)

def load_stream_data(db):
    """Load latest metrics from MongoDB live_metrics"""
    try:
        # Get historical windows for charts (last 120 windows = 10 mins at 5s/window)
        cursor = db["live_metrics"].find().sort("window_start", pymongo.DESCENDING).limit(120)
        data = list(cursor)
        df = pd.DataFrame()
        if data:
            df = pd.DataFrame(data).sort_values("window_start", ascending=True)
            # Format window_start to HH:MM:SS string for the X-axis label
            df["time_label"] = pd.to_datetime(df["window_start"]).dt.strftime("%H:%M:%S")
            
        # Get total cumulative ratings across all stream history
        pipeline = [{"$group": {
            "_id": None, 
            "total_lifetime_ratings": {"$sum": "$total_ratings_in_window"},
            "total_lifetime_revenue": {"$sum": "$revenue_in_window"}
        }}]
        agg_result = list(db["live_metrics"].aggregate(pipeline))
        cumulative_ratings = agg_result[0]['total_lifetime_ratings'] if agg_result else 0
        cumulative_revenue = agg_result[0]['total_lifetime_revenue'] if agg_result and 'total_lifetime_revenue' in agg_result[0] and agg_result[0]['total_lifetime_revenue'] else 0
        
        return df, cumulative_ratings, cumulative_revenue
    except Exception as e:
        st.error(f"Error fetching streaming data: {e}")
        return pd.DataFrame(), 0, 0

def render_streaming_dashboard():
    st.markdown("<h1>🎬 Live Cinema Streaming Analytics</h1>", unsafe_allow_html=True)
    st.markdown('<div class="live-badge">🟢 LIVE STREAM</div>', unsafe_allow_html=True)
    
    client = get_mongo_client()
    mongo_db = os.getenv("MONGO_DB", "cinema_dw")
    db = client[mongo_db]
    
    # Layout
    col_metrics, col_chart = st.columns([1, 3])
    
    df, cumulative_ratings, cumulative_revenue = load_stream_data(db)
    
    if not df.empty:
        latest = df.iloc[-1]
        peak_traffic = df['total_ratings_in_window'].max()
        
        with col_metrics:
            st.subheader("Live Overview")
            
            # BI Metric 1: Cumulative Traffic
            st.metric(
                label="Total Streaming Ratings",
                value=f"{int(cumulative_ratings):,}",
                help="Total ratings processed since the stream started."
            )
            
            # BI Metric 3: Cumulative Revenue
            st.metric(
                label="Total Revenue of Trending Movies",
                value=f"${int(cumulative_revenue):,}" if cumulative_revenue else "$0",
                help="Sum of global revenue for all movies that received a rating in the stream."
            )
            
            st.markdown("---")
            st.subheader("Current Window (5s)")
            
            st.metric(
                label="Traffic",
                value=f"{int(latest.get('total_ratings_in_window', 0))}",
                delta="Live"
            )
            
            avg_rtg = latest.get('avg_rating_in_window', 0)
            st.metric(
                label="Avg Rating",
                value=f"{avg_rtg:.2f} ⭐" if pd.notnull(avg_rtg) else "N/A"
            )
            
            # BI Metric 2: Peak Traffic in the viewed window
            st.metric(
                label="Peak Traffic (Last 10m)",
                value=f"{int(peak_traffic)}",
                help="Maximum ratings received in a single 5s window within the last 10 minutes."
            )
            
            current_rev = latest.get('revenue_in_window', 0)
            if pd.notnull(current_rev) and current_rev > 0:
                st.metric(
                    label="Window Revenue",
                    value=f"${int(current_rev):,}",
                    delta="Live"
                )
            
            st.caption(f"Last Updated: {str(latest.get('window_end', '')).split('.')[0]}")
            
        with col_chart:
            st.subheader("📈 Traffic over Time (Realtime — 5s windows)")
            fig = px.area(
                df, 
                x="time_label", 
                y="total_ratings_in_window",
                labels={"time_label": "Time (HH:MM:SS)", "total_ratings_in_window": "Ratings / 5s"},
                color_discrete_sequence=["#58a6ff"]
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#c9d1d9',
                margin=dict(l=0, r=0, t=20, b=0),
                xaxis=dict(showgrid=False, tickangle=-45, nticks=15),
                yaxis=dict(showgrid=True, gridcolor='#30363d')
            )
            st.plotly_chart(fig, width='stretch')
            
            st.subheader("⭐ Average Rating Trend")
            fig2 = px.line(
                df,
                x="time_label",
                y="avg_rating_in_window",
                labels={"time_label": "Time (HH:MM:SS)", "avg_rating_in_window": "Avg Rating"},
                color_discrete_sequence=["#8957e5"],
                markers=True
            )
            fig2.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#c9d1d9',
                margin=dict(l=0, r=0, t=20, b=0),
                xaxis=dict(showgrid=False, tickangle=-45, nticks=15),
                yaxis=dict(showgrid=True, gridcolor='#30363d', range=[0, 5])
            )
            st.plotly_chart(fig2, width='stretch')

            # Revenue chart
            if 'revenue_in_window' in df.columns and df['revenue_in_window'].sum() > 0:
                st.subheader("💰 Window Revenue Trend")
                fig3 = px.bar(
                    df,
                    x="time_label",
                    y="revenue_in_window",
                    labels={"time_label": "Time (HH:MM:SS)", "revenue_in_window": "Revenue ($)"},
                    color_discrete_sequence=["#3fb950"]
                )
                fig3.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#c9d1d9',
                    margin=dict(l=0, r=0, t=20, b=0),
                    xaxis=dict(showgrid=False, tickangle=-45, nticks=15),
                    yaxis=dict(showgrid=True, gridcolor='#30363d')
                )
                st.plotly_chart(fig3, width='stretch')
    else:
        st.info("No streaming data available yet. Start the Kafka Producer and PySpark Streaming Job.")
        
    # Auto-refresh logic (every 1 second for near-realtime feel)
    time.sleep(1)
    st.rerun()
