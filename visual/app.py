import streamlit as st

# --- Page Configuration ---
# Must be the first Streamlit command
st.set_page_config(
    page_title="Cinema Data Analytics",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

import os
from pathlib import Path
from dotenv import load_dotenv

# We import the dashboard modules dynamically based on user selection
# to avoid loading logic prematurely.
from dashboards.batch import render_batch_dashboard
from dashboards.streaming import render_streaming_dashboard

# --- Load Environment ---
project_root = Path(__file__).resolve().parents[1]
load_dotenv(project_root / ".env")

# --- Custom CSS for Premium Design ---
st.markdown("""
<style>
    /* Dark aesthetic background */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Header typography */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #58a6ff;
    }
    
    /* Metric cards styling */
    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, #161b22, #0d1117);
        border: 1px solid #30363d;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s ease-in-out;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(88, 166, 255, 0.2);
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Auto-refresh indicator */
    .live-badge {
        background-color: #238636;
        color: #ffffff;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 1rem;
        animation: pulse 2s infinite;
    }
    
    .batch-badge {
        background-color: #8957e5;
        color: #ffffff;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 1rem;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
st.sidebar.markdown("---")

app_mode = st.sidebar.radio(
    "Select Dashboard",
    ["Batch Analytics", "Real-time Streaming"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Cinema Data Architecture**\n\n"
    "• **Batch**: Static metrics analyzed from HDFS by Spark Batch.\n"
    "• **Streaming**: Real-time traffic tracked via Kafka & PySpark Structured Streaming."
)

# --- Main Routing ---
if app_mode == "Batch Analytics":
    render_batch_dashboard()
elif app_mode == "Real-time Streaming":
    render_streaming_dashboard()
