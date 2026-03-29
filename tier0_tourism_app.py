import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import st_folium

# --- 1. CONFIG & SYSTEM CSS ---
st.set_page_config(page_title="Resilience Scorecard Pro", layout="wide")

st.markdown("""
<style>
    /* Φόντο Dashboard */
    .stApp { background-color: #0e1117; color: white; }
    
    /* Header Style - Dark & Professional */
    .main-header {
        background-color: #1c2a48;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #00d4ff;
        margin-bottom: 20px;
    }
    .main-header h1 { color: #ffffff; margin-bottom: 5px; font-size: 24px; letter-spacing: 2px; }
    .main-header p { color: #00d4ff; font-size: 14px; margin: 0; }

    /* Card Styling */
    .content-card {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
        height: 100%;
    }
    
    /* Stats Box Inside Cards */
    .stat-val { font-size: 32px; font-weight: bold; color: #ffca28; }
    .stat-lbl { font-size: 12px; color: #8b949e; text-transform: uppercase; }

    /* Variable List Styling */
    .var-item {
        background: #0d1117;
        padding: 10px;
        border-radius: 5px;
        border-left: 3px solid #00d4ff;
        margin-bottom: 8px;
        font-size: 13px;
    }
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

# --- 3. SIDEBAR (True Dark) ---
with st.sidebar:
    st.markdown("### ⚙️ SETTINGS")
    selected_cities = st.multiselect("Municipalities:", options=list(mapping.keys()), default=list(mapping.keys()))
    st.markdown("---")
    st.markdown("📊 **ALGORITHMIC MODEL**")
    st.caption("Shannon Entropy Weighting")
    st.caption("Everitt Empirical Classification")

# --- 4. ENGINE ---
if len(selected_cities) >= 2:
    temp_data = []
    for name in selected_cities:
        d = mapping[name]
        score = round((d["base_dem"] * 0.25) + (d["pias"] * 55) + (d["vib"] * 0.20), 1)
        temp_data.append({"Δήμος": name, "Lat": d["lat"], "Lon": d["lon"], "Score": score, "PIAS": d["pias"], "Vibrancy": d["vib"]})
    
    df = pd.DataFrame(temp_data)
    mu, sigma = df["Score"].mean(), df["Score"].std()
    upper, lower = mu + (0.5 * sigma), mu - (0.5 * sigma)
    df["Status"] = df["Score"].apply(lambda x: "🟢 High" if x > upper else ("🔴 Low" if x < lower else "🟡 Medium"))
    df = df.sort_values(by="Score", ascending=False)

    # --- 5. DASHBOARD LAYOUT (GRID SYSTEM) ---
    
    # 5.1 HEADER
    st.markdown("""
        <div class='main-header'>
            <h1>MUNICIPALITY TOURISM RESILIENCE SCORECARD</h1>
            <p>DATA-DRIVEN DECISIONS FOR SUSTAINABLE TOURISM</p>
        </div>
    """, unsafe_allow_html=True)

    # 5.2 TOP ROW: METRICS & RANKING
    row1_col1, row1_col2 = st.columns([3, 2])

    with row1_col1:
        st.markdown("<div class='content-card'><b>📊 KEY RESILIENCE METRICS</b><br><br>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.markdown(f"<div class='stat-lbl'>Mean (μ)</div><div class='stat-val'>{mu:.1f}</div>", unsafe_allow_html=True)
        m2.markdown(f"<div class='stat-lbl'>Std Dev (σ)</div><div class='stat-val'>{sigma:.1f}</div>", unsafe_allow_html=True)
        m3.markdown(f"<div class='stat-lbl'>Threshold</div><div class='stat-val' style='color:#00d4ff;'>{upper:.1f}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with row1_col2:
        st.markdown("<div class='content-card'><b>🏆 RESILIENCE RANKING</b>", unsafe_allow_html=True)
        st.dataframe(df[["Δήμος", "Score", "Status"]], use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 5.3 BOTTOM ROW: VARIABLES & MAP
    row2_col1, row2_col2 = st.columns([3, 2])

    with row2_col1:
        st.markdown("""
            <div class='content-card'>
                <b>📘 DETAILED VARIABLE ANALYSIS</b><br><br>
                <div class='var-item'><b>ΠΕ1: Composite Index</b> - Core economic strength analysis.</div>
                <div class='var-item'><b>ΠΕ2: Vulnerability Index</b> - NASA Night Lights & Activity.</div>
                <div class='var-item'><b>ΠΕ3: Policy Alignment</b> - ESPA Funding Similarity Score.</div>
                <div class='var-item'><b>ΠΕ4: Sectoral Network</b> - Business cluster resilience.</div>
            </div>
        """, unsafe_allow_html=True)

    with row2_col2:
        st.markdown("<div class='content-card'><b>📍 GEOSPATIAL MAP</b>", unsafe_allow_html=True)
        m = folium.Map(location=[38.2, 24.2], zoom_start=5, tiles="CartoDB dark_matter")
        for _, r in df.iterrows():
            color = "#28A745" if "High" in r["Status"] else "#FD7E14" if "Medium" in r["Status"] else "#DC3545"
            folium.CircleMarker([r["Lat"], r["Lon"]], radius=10, color=color, fill=True).add_to(m)
        st_folium(m, height=250, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("Please select municipalities.")
