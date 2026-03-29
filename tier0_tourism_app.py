import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

# --- 1. CONFIG & STYLES ---
st.set_page_config(page_title="ResilienceIQ Consolidated Pro", layout="wide")

st.markdown("""
<style>
    .report-header { background-color: #1E50B4; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center; }
    .metric-card { background: #ffffff; border-radius: 10px; padding: 15px; border-top: 5px solid #1E50B4; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .stTable { background-color: white; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE (Expanded) ---
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

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield-with-growth.png", width=60)
    st.title("ResilienceIQ Pro")
    st.markdown("### 🔐 Έλεγχος Πρόσβασης")
    selected_cities = st.multiselect(
        "Επιλέξτε Δήμους για ανάλυση (απεριόριστοι):",
        options=list(mapping.keys()),
        default=["Χανιά", "Ρόδος", "Αθήνα", "Σαντορίνη"]
    )
    st.divider()
    st.info(f"📊 Σύνολο προς επεξεργασία: {len(selected_cities)} Δήμοι")

# --- 4. MAIN DASHBOARD ---
if not selected_cities:
    st.warning("⚠️ Παρακαλώ επιλέξτε τουλάχιστον έναν Δήμο από το Sidebar για να ξεκινήσει το Pipeline.")
else:
    # --- PIPELINE CALCULATIONS ---
    results = []
    for name in selected_cities:
        d = mapping[name]
        # Weighted Resilience Score Calculation
        score = round((d["base_dem"] * 0.25) + (d["pias"] * 55) + (d["vib"] * 0.20), 1)
        # Empirical Classification Logic (3 Levels)
        status = "Υψηλή (Safe)" if score > 72 else "Μεσαία (Warning)" if score > 58 else "Χαμηλή (Critical)"
        color = "#27AE60" if status == "Υψηλή (Safe)" else "#E67E22" if status == "Μεσαία (Warning)" else "#C0392B"
        
        results.append({
            "Δήμος": name, "Lat": d["lat"], "Lon": d["lon"], 
            "Resilience Score": score, "Κατάσταση": status, "Color": color,
            "PIAS": d["pias"], "Demand": d["base_dem"], "Vibrancy": d["vib"], "Sectoral": d["sect"]
        })
    
    # Δημιουργία DataFrame και Ταξινόμηση (Ranking)
    df_res = pd.DataFrame(results).sort_values(by="Resilience Score", ascending=False)

    st.markdown("<div class='report-header'><h2>Consolidated Resilience Dashboard v4.0</h2></div>", unsafe_allow_html=True)

    # --- SECTION A: COMPARATIVE RADAR (Triple Mode) ---
    st.subheader("📊 Συγκριτικό Προφίλ (Έως 3 Δήμοι)")
    comp_selection = st.multiselect(
        "Επιλέξτε Δήμους για σύγκριση στο Radar Chart:",
        options=selected_cities,
        default=selected_cities[:min(len(selected_cities), 3)],
        max_selections=3
    )

    if comp_selection:
        categories = ['Ανθεκτικότητα', 'Ζήτηση', 'ΕΣΠΑ (PIAS)', 'Κλαδική Δομή', 'Vibrancy (NASA)']
        fig_radar = go.Figure()
        for city in comp_selection:
            c_data = df_res[df_res["Δήμος"] == city].iloc[0]
            fig_radar.add_trace(go.Scatterpolar(
                r=[c_data['Resilience Score']/100, c_data['Demand']/100, c_data['PIAS'], c_data['Sectoral'], c_data['Vibrancy']/100],
                theta=categories, fill='toself', name=city
            ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), height=450)
        st.plotly_chart(fig_radar, use_container_width=True)

    # --- SECTION B: RANKING TABLE ---
    st.subheader("🏆 Πίνακας Κατάταξης & Scorecards")
    # Εμφάνιση πίνακα με styling
    st.dataframe(
        df_res[["Δήμος", "Resilience Score", "Κατάσταση", "PIAS"]].style.background_gradient(subset=['Resilience Score'], cmap='RdYlGn'),
        use_container_width=True, hide_index=True
    )

    # --- SECTION C: METHODOLOGY EXPANDER ---
    with st.expander("🔍 Ανάλυση Μεταβλητών ανά ΠΕ (Model Features)"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### ΠΕ1 & ΠΕ2: CI & VI")
            st.write("- **Mr_GVA, Mr_EMP:** Οικονομική βάση.")
            st.write("- **NASA VIIRS:** Φυσική δραστηριότητα.")
        with col2:
            st.markdown("#### ΠΕ3 & ΠΕ4: PIAS & SECTORAL")
            st.write("- **Cosine Similarity:** Ευθυγράμμιση ΕΣΠΑ.")
            st.write("- **NACE Imputation:** Κάλυψη κενών ΕΛΣΤΑΤ.")

    # --- SECTION D: GEOSPATIAL MAP ---
    st.divider()
    st.subheader("📍 Γεωγραφική Διασπορά Κινδύνου")
    m = folium.Map(location=[38.2, 24.2], zoom_start=6, tiles="CartoDB positron")
    for _, r in df_res.iterrows():
        folium.CircleMarker(
            location=[r["Lat"], r["Lon"]], radius=12,
            color=r["Color"], fill=True, fill_color=r["Color"],
            popup=f"<b>{r['Δήμος']}</b><br>Score: {r['Resilience Score']}<br>Status: {r['Κατάσταση']}"
        ).add_to(m)
    st_folium(m, width=1100, height=500)
