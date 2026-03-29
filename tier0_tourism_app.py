import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

# --- 1. SETTINGS & STYLES ---
st.set_page_config(page_title="ResilienceIQ Pro Edition", layout="wide")

st.markdown("""
<style>
    .report-header { background-color: #1E50B4; color: white; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
    .metric-card { background: #ffffff; border-radius: 10px; padding: 12px; border-top: 4px solid #1E50B4; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 8px; }
    .ai-advice { background-color: #f0f2f6; border-left: 5px solid #1E50B4; padding: 15px; border-radius: 5px; font-size: 15px; }
    .summary-box { background-color: #e8f0fe; padding: 15px; border-radius: 10px; border: 1px solid #1E50B4; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATASET ---
mapping = {
    "Χανιά": {"lat": 35.5138, "lon": 24.0180, "base_dem": 70.1, "list": 677},
    "Ρόδος": {"lat": 36.4341, "lon": 28.2176, "base_dem": 72.0, "list": 850},
    "Μύκονος": {"lat": 37.4467, "lon": 25.3289, "base_dem": 85.0, "list": 1200},
    "Σαντορίνη": {"lat": 36.3932, "lon": 25.4615, "base_dem": 88.5, "list": 1100},
    "Κέρκυρα": {"lat": 39.6243, "lon": 19.9217, "base_dem": 62.0, "list": 720},
    "Αθήνα": {"lat": 37.9838, "lon": 23.7275, "base_dem": 92.0, "list": 5000},
    "Θεσσαλονίκη": {"lat": 40.6401, "lon": 22.9444, "base_dem": 58.0, "list": 1500},
    "Ηράκλειο": {"lat": 35.3387, "lon": 25.1442, "base_dem": 60.5, "list": 950},
    "Ναύπλιο": {"lat": 37.5675, "lon": 22.8017, "base_dem": 48.0, "list": 320}
}

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield-with-growth.png", width=60
