import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import st_folium

# --- 1. CONFIG & SYSTEM CSS (True Layout Styling) ---
st.set_page_config(page_title="Resilience Scorecard Pro", layout="wide")

st.markdown("""
<style>
    /* Φόντο Dashboard & Γραμματοσειρά */
    .stApp { background-color: #0e1117; color: white; font-family: 'Helvetica Neue', sans-serif; }
    
    /* Header Style - Premium Dark Blue */
    .main-header {
        background: linear-gradient(90deg, #1c2a48 0%, #0e1117 100%);
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #00d4ff;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .main-header h1 { color: #ffffff; margin: 0; font-size: 26px; letter-spacing: 2px; }
    .main-header p { color: #00d4ff; font-size: 14px; margin: 5px 0 0 0; opacity: 0.8; }

    /* Content Card Styling - Rounded Boxes */
    .content-card {
        background-color: #161b22;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
    }
    
    /* Stats Box Inside Cards */
    .stat-val { font-size: 36px; font-weight: bold; color: #ffca28; }
    .stat-lbl { font-size: 13px; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; }

    /* Επεξήγηση Μεταβλητών (Styled Text) */
    .var-title { color: #00d4ff; font-weight: bold; font-size: 15px; }
    .var-desc { color: #c9d1d9; font-size: 13px; margin-bottom: 10px; }
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

# --- 3. SIDEBAR (True Dark Settings) ---
with st.sidebar:
    st.markdown("### ⚙️ SETTINGS")
    # Η λίστα των Δήμων όπως ζητήθηκε
    all_cities = list(mapping.keys())
    selected_cities = st.multiselect(
        "Προσθήκη Δήμων στο Δείγμα:",
        options=all_cities,
        default=all_cities
    )
    st.markdown("---")
    st.markdown("📊 **ALGORITHMIC MODEL**")
    st.caption("Shannon Entropy Weighting")
    st.caption("Everitt Empirical Classification")

# --- 4. DATA LOGIC ---
if len(selected_cities) >= 2:
    temp_results = []
    for name in selected_cities:
        d = mapping[name]
        # Σύνθεση Score
        score = round((d["base_dem"] * 0.25) + (d["pias"] * 55) + (d["vib"] * 0.20), 1)
        temp_results.append({
            "Δήμος": name, "Lat": d["lat"], "Lon": d["lon"], 
            "Score": score, "PIAS": d["pias"], "Vibrancy": d["vib"]
        })
    
    df = pd.DataFrame(temp_results)
    mu, sigma = df["Score"].mean(), df["Score"].std()
    upper, lower = mu + (0.5 * sigma), mu - (0.5 * sigma)
    
    df["Επίπεδο"] = df["Score"].apply(lambda x: "🟢 High (Safe)" if x > upper else ("🔴 Low (Critical)" if x < lower else "🟠 Medium (Warning)"))
    df = df.sort_values(by="Score", ascending=False)

    # --- 5. DASHBOARD LAYOUT (2x2 GRID SYSTEM) ---
    
    # 5.1 HEADER
    st.markdown("""
        <div class='main-header'>
            <h1>MUNICIPALITY TOURISM RESILIENCE SCORECARD</h1>
            <p>DATA-DRIVEN DECISIONS FOR SUSTAINABLE TOURISM</p>
        </div>
    """, unsafe_allow_html=True)

    # 5.2 TOP ROW: METRICS & RANKING (3:2 Ratio)
    row1_col1, row1_col2 = st.columns([3, 2])

    with row1_col1:
        st.markdown("<div class='content-card'><b>📊 KEY RESILIENCE METRICS (Overall Sample)</b><br><br>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.markdown(f"<div class='stat-lbl'>Mean Resilience (μ)</div><div class='stat-val'>{mu:.1f}</div>", unsafe_allow_html=True)
        m2.markdown(f"<div class='stat-lbl'>Standard Deviation (σ)</div><div class='stat-val'>{sigma:.1f}</div>", unsafe_allow_html=True)
        m3.markdown(f"<div class='stat-lbl'>Resilience Threshold</div><div class='stat-val' style='color:#00d4ff;'>{upper:.1f}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with row1_col2:
        st.markdown("<div class='content-card'><b>🏆 RESILIENCE RANKING (Full List)</b>", unsafe_allow_html=True)
        # Πίνακας με Progress Bars
        st.dataframe(
            df[["Δήμος", "Score", "Επίπεδο", "PIAS"]], 
            column_config={
                "Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%.1f"),
                "PIAS": st.column_config.NumberColumn("Policy Alignment", format="%.2f")
            },
            use_container_width=True, hide_index=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # 5.3 BOTTOM ROW: VARIABLES & MAP (3:2 Ratio)
    row2_col1, row2_col2 = st.columns([3, 2])

    with row2_col1:
        st.markdown("<div class='content-card'><b>📗 DETAILED VARIABLE ANALYSIS (Work Packages)</b><br><br>", unsafe_allow_html=True)
        
        # Λεπτομερής Επεξήγηση Μεταβλητών με Expanders για εξοικονόμηση χώρου
        with st.expander("🔍 ΠΕ1: Σύνθετος Δείκτης CI (Economic Base)", expanded=False):
            st.markdown("<div class='var-title'>Περιγραφή:</div>", unsafe_allow_html=True)
            st.markdown("<div class='var-desc'>Αναλύει την οικονομική 'υγεία' του Δήμου μέσω του GVA (Ακαθάριστη Προστιθέμενη Αξία) και της απασχόλησης.</div>", unsafe_allow_html=True)
        
        with st.expander("🔍 ΠΕ2: Δείκτης VI (NASA Vibrancy Index)", expanded=False):
            st.markdown("<div class='var-title'>Περιγραφή:</div>", unsafe_allow_html=True)
            st.markdown("<div class='var-desc'>Χρήση δορυφορικών δεδομένων νυχτερινού φωτισμού και κινητικότητας για τη μέτρηση της πραγματικής δραστηριότητας στην πόλη.</div>", unsafe_allow_html=True)
            
        with st.expander("🔍 ΠΕ3: Δείκτης PIAS (Strategic Alignment)", expanded=False):
            st.markdown("<div class='var-title'>Περιγραφή:</div>", unsafe_allow_html=True)
            st.markdown("<div class='var-desc'>Policy-Investment Alignment Score: Ελέγχει την ευθυγράμμιση των επενδύσεων ΕΣΠΑ με τις πραγματικές ανάγκες του Δήμου.</div>", unsafe_allow_html=True)
            
        with st.expander("🔍 ΠΕ4: Sectoral Network (NACE Rev.2)", expanded=False):
            st.markdown("<div class='var-title'>Περιγραφή:</div>", unsafe_allow_html=True)
            st.markdown("<div class='var-desc'>Αναλύει το δίκτυο των τοπικών επιχειρήσεων και μετρά πόσο ευάλωτος είναι ο τουριστικός κλάδος σε σοκ.</div>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

    with row2_col2:
        st.markdown("<div class='content-card'><b>📍 GEOSPATIAL MAP (Global View)</b>", unsafe_allow_html=True)
        # Σκοτεινός Χάρτης για να δένει με το Layout
        m = folium.Map(location=[38.2, 24.2], zoom_start=5, tiles="CartoDB dark_matter")
        for _, r in df.iterrows():
            # Χρώμα Marker βάσει Score
            color = "#28A745" if "High" in r["Επίπεδο"] else "#FD7E14" if "Μεσαίο" in r["Επίπεδο"] else "#DC3545"
            folium.CircleMarker(
                [r["Lat"], r["Lon"]], 
                radius=12, 
                color=color, 
                fill=True, 
                fill_opacity=0.7, 
                popup=f"<b>{r['Δήμος']}</b><br>Score: {r['Score']}"
            ).add_to(m)
        st_folium(m, height=280, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("⚠️ Παρακαλώ επιλέξτε τουλάχιστον 2 Δήμους από τα Settings (Sidebar) για να ξεκινήσει η ανάλυση.")
