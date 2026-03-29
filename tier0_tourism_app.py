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
    st.image("https://img.icons8.com/fluency/96/shield-with-growth.png", width=60)
    st.title("ResilienceIQ Pro")
    menu = st.radio("Μενού Πλοήγησης:", ["Επιχειρησιακό Dashboard", "Εγχειρίδιο & Μεθοδολογία"])
    
    st.divider()
    if menu == "Επιχειρησιακό Dashboard":
        st.header("🔐 Έλεγχος Πρόσβασης")
        selected_cities = st.multiselect(
            "Επιλέξτε έως 5 Δήμους:",
            options=list(mapping.keys()),
            default=["Χανιά", "Ρόδος", "Κέρκυρα", "Αθήνα", "Σαντορίνη"],
            max_selections=5
        )
        st.header("🎮 Προσομοιωτής (What-if)")
        s_demand = st.slider("Μεταβολή Ζήτησης (%)", -100, 50, 0)
        s_mob = st.slider("Μεταβολή Κινητικότητας (%)", -100, 50, 0)

# --- 4. PAGE: DASHBOARD ---
if menu == "Επιχειρησιακό Dashboard":
    st.markdown("<div class='report-header'><h2>Resilience Control Center: Ελλάδα</h2></div>", unsafe_allow_html=True)
    
    if not selected_cities:
        st.error("⚠️ Παρακαλώ επιλέξτε τουλάχιστον έναν Δήμο από το Sidebar.")
    else:
        results = []
        for name in selected_cities:
            data = mapping[name]
            adj_dem = data["base_dem"] * (1 + s_demand/100)
            adj_mob = -3.7 * (1 + s_mob/100)
            vib = np.clip((adj_dem * 0.45 + (55 + adj_mob) * 0.55), 0, 100)
            score = round((adj_dem * 0.35) + (vib * 0.45) + (20 - (data["list"]/1000) * 0.5), 1)
            color = "#27AE60" if score > 55 else "#E67E22" if score > 40 else "#C0392B"
            results.append({"Δήμος": name, "Lat": data["lat"], "Lon": data["lon"], "Score": score, "Color": color, "Vib": vib, "Dem": adj_dem})

        df_res = pd.DataFrame(results)

        # KPIs & FOCUS SELECTION
        focus_city = st.selectbox("Εστίαση & Ερμηνεία Δείκτη για:", selected_cities)
        f_data = df_res[df_res["Δήμος"] == focus_city].iloc[0]

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='metric-card'><b>Resilience Score</b><br><span style='font-size:26px; color:{f_data['Color']};'>{f_data['Score']}</span></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'><b>NASA Vibrancy</b><br><span style='font-size:26px;'>{f_data['Vib']:.1f}</span></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-card'><b>Ζήτηση (Adj)</b><br><span style='font-size:26px;'>{f_data['Dem']:.1f}</span></div>", unsafe_allow_html=True)

        # ΔΥΝΑΜΙΚΗ ΕΡΜΗΝΕΙΑ (Με NASA Vibrancy)
