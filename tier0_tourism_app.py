import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import st_folium

# --- 1. SETTINGS & ADVANCED UI STYLING ---
st.set_page_config(page_title="Resilience Scorecard Pro", layout="wide")

# Custom CSS για το "Attractive Look"
st.markdown("""
<style>
    /* Main Background & Font */
    .stApp { background-color: #f4f7f9; }
    
    /* Header Style */
    .report-header { 
        background: linear-gradient(90deg, #0e1117 0%, #1c2a48 100%); 
        color: white; padding: 30px; border-radius: 15px; 
        text-align: center; margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border-bottom: 4px solid #00d4ff;
    }

    /* Metric Cards */
    .metric-card {
        background: white; padding: 20px; border-radius: 12px;
        border-top: 5px solid #00d4ff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
    }
    .metric-value { font-size: 28px; font-weight: bold; color: #1c2a48; }
    .metric-label { font-size: 14px; color: #666; text-transform: uppercase; }

    /* Variable Info Cards */
    .var-card {
        background: #ffffff; padding: 15px; border-radius: 10px;
        border-left: 5px solid #1E50B4; margin-bottom: 10px;
        transition: transform 0.2s;
    }
    .var-card:hover { transform: scale(1.02); }

    /* Sidebar Dark Theme */
    [data-testid="stSidebar"] { background-color: #0e1117; color: white; }
    [data-testid="stSidebar"] * { color: white !important; }
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

# --- 3. SIDEBAR (Dark Mode Settings) ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/resilience.png", width=70)
    st.markdown("## SETTINGS")
    st.markdown("---")
    st.markdown("🔍 **SELECT MUNICIPALITIES**")
    selected_cities = st.multiselect("", options=list(mapping.keys()), default=list(mapping.keys()), label_visibility="collapsed")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("⚖️ **ALGORITHMIC MODEL**")
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
    
    def get_status(x):
        if x > upper: return "🟢 High (Safe)"
        if x < lower: return "🔴 Low (Critical)"
        return "🟡 Medium (Stable)"
    
    df["Status"] = df["Score"].apply(get_status)
    df = df.sort_values(by="Score", ascending=False)

    # --- 5. MAIN DASHBOARD ---
    st.markdown("""
        <div class='report-header'>
            <h1>MUNICIPALITY TOURISM RESILIENCE SCORECARD</h1>
            <p style='letter-spacing: 2px; opacity: 0.8;'>DATA-DRIVEN DECISIONS FOR SUSTAINABLE TOURISM</p>
        </div>
    """, unsafe_allow_html=True)

    # 5.1 Metrics Row
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='metric-card'><div class='metric-label'>Mean Resilience (μ)</div><div class='metric-value'>{mu:.1f}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='metric-card'><div class='metric-label'>Standard Deviation (σ)</div><div class='metric-value'>{sigma:.1f}</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-card'><div class='metric-label'>Resilience Threshold</div><div class='metric-value' style='color:#00d4ff;'>{upper:.1f}</div></div>", unsafe_allow_html=True)

    # 5.2 Middle Section: Variable Analysis & Table
    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("📊 Detailed Variable Analysis")
        st.markdown(f"""
            <div class='var-card'><b>ΠΕ1: Composite Index (Economic Base)</b><br>Measures core economic strength.</div>
            <div class='var-card'><b>ΠΕ2: Vulnerability Index (NASA Vibrancy)</b><br>Uses night lights to measure local activity.</div>
            <div class='var-card'><b>ΠΕ3: Policy Alignment (PIAS)</b><br>Checks if ESPA funding matches real needs.</div>
            <div class='var-card'><b>ΠΕ4: Sectoral Network (NACE Rev.2)</b><br>Examines resilience to business shocks.</div>
        """, unsafe_allow_html=True)

    with col_right:
        st.subheader("🏆 Resilience Ranking")
        st.dataframe(df[["Δήμος", "Score", "Status"]], column_config={"Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100)}, use_container_width=True, hide_index=True)

    # 5.3 Comparison & Map
    st.divider()
    st.subheader("📍 Geospatial Resilience Map")
    m = folium.Map(location=[38.2, 24.2], zoom_start=6, tiles="CartoDB positron")
    for _, r in df.iterrows():
        color = "#28A745" if "High" in r["Status"] else "#FD7E14" if "Medium" in r["Status"] else "#DC3545"
        folium.CircleMarker([r["Lat"], r["Lon"]], radius=15, color=color, fill=True, fill_opacity=0.8, popup=f"{r['Δήμος']}: {r['Score']}").add_to(m)
    st_folium(m, width=1100, height=450)

else:
    st.info("⚠️ Please select municipalities from the Sidebar to activate the Scorecard.")
