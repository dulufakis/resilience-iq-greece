import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import st_folium

# --- 1. SETTINGS & STYLES ---
st.set_page_config(page_title="Tourism Resilience Scorecard", layout="wide")

st.markdown("""
<style>
    .report-header { background-color: #1E50B4; color: white; padding: 25px; border-radius: 12px; margin-bottom: 25px; text-align: center; border-bottom: 5px solid #FFD700; }
    .stat-box { background-color: #ffffff; border-radius: 10px; padding: 15px; border: 2px solid #1E50B4; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    .variable-box { background-color: #f1f3f9; padding: 15px; border-radius: 8px; border-left: 5px solid #1E50B4; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE ---
mapping = {
    "Χανιά": {"lat": 35.5138, "lon": 24.0180, "base_dem": 70.1, "pias": 0.88, "vib": 65.0, "sect": 0.72},
    "Ρόδος": {"lat": 36.4341, "lon": 28.2176, "base_dem": 72.0, "pias": 0.82, "vib": 68.0, "sect": 0.65},
    "Κέρκυρα": {"lat": 39.6243, "lon": 19.9217, "base_dem": 62.0, "pias": 0.75, "vib": 58.0, "sect": 0.60},
    "Αθήνα": {"lat": 37.9838, "lon": 23.7275, "base_dem": 92.0, "pias": 0.91, "vib": 85.0, "sect": 0.88},
    "Σαντορίνη": {"lat": 36.3932, "lon": 25.4615, "base_dem": 88.5, "pias": 0.79, "vib": 75.0, "sect": 0.55},
    "Θεσσαλονίκη": {"lat": 40.6401, "lon": 22.9444, "base_dem": 58.0, "pias": 0.85, "vib": 78.0, "sect": 0.82},
    "Ηράκλειο": {"lat": 35.3387, "lon": 25.1442, "base_dem": 60.5, "pias": 0.80, "vib": 62.0, "sect": 0.70},
    "Μύκονος": {"lat": 37.4467, "lon": 25.3289, "base_dem": 85.0, "pias": 0.72, "vib": 80.0, "sect": 0.50}
}

# --- 3. SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/resilience.png", width=80)
    st.title("DSS Control Panel")
    selected_cities = st.multiselect("Δήμοι προς Benchmarking:", options=list(mapping.keys()), default=list(mapping.keys()))
    st.markdown("---")
    st.caption("Weighting: Shannon Entropy | Clustering: μ ± 0.5σ")

# --- 4. ENGINE ---
if len(selected_cities) >= 2:
    temp_data = []
    for name in selected_cities:
        d = mapping[name]
        score = round((d["base_dem"] * 0.25) + (d["pias"] * 55) + (d["vib"] * 0.20), 1)
        temp_data.append({"Δήμος": name, "Lat": d["lat"], "Lon": d["lon"], "Score": score, "PIAS": d["pias"], "Demand": d["base_dem"], "Vibrancy": d["vib"]})
    
    df = pd.DataFrame(temp_data)
    mu, sigma = df["
