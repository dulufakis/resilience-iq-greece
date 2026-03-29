import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

# --- 1. CONFIG & SETTINGS ---
st.set_page_config(page_title="ResilienceIQ Consolidated", layout="wide")

CONFIG = {
    "sectoral_imputation": "mean_nace_section",
    "rag_inference": "api",
    "scale_invariance": "Cosine Similarity (PIAS)",
    "audit_trail": "Enabled (Pydantic Model)"
}

st.markdown("""
<style>
    .report-header { background-color: #1E50B4; color: white; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
    .metric-card { background: #ffffff; border-radius: 10px; padding: 12px; border-top: 4px solid #1E50B4; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 8px; }
    .ai-advice { background-color: #f0f2f6; border-left: 5px solid #1E50B4; padding: 15px; border-radius: 5px; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATASET (NUTS II Level) ---
mapping = {
    "Χανιά": {"lat": 35.5138, "lon": 24.0180, "base_dem": 70.1, "list": 677, "pias": 0.88, "vib": 65.0, "sect": 0.72},
    "Ρόδος": {"lat": 36.4341, "lon": 28.2176, "base_dem": 72.0, "list": 850, "pias": 0.82, "vib": 68.0, "sect": 0.65},
    "Κέρκυρα": {"lat": 39.6243, "lon": 19.9217, "base_dem": 62.0, "list": 720, "pias": 0.75, "vib": 58.0, "sect": 0.60},
    "Αθήνα": {"lat": 37.9838, "lon": 23.7275, "base_dem": 92.0, "list": 5000, "pias": 0.91, "vib": 85.0, "sect": 0.88},
    "Σαντορίνη": {"lat": 36.3932, "lon": 25.4615, "base_dem": 88.5, "list": 1100, "pias": 0.79, "vib": 75.0, "sect": 0.55}
}

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("ResilienceIQ Pro")
    menu = st.radio("Πλοήγηση:", ["Επιχειρησιακό Dashboard", "Audit Trail & Compliance"])
    
    if menu == "Επιχειρησιακό Dashboard":
        st.header("🔐 Έλεγχος Πρόσβασης")
        selected_cities = st.multiselect(
            "Επιλέξτε Δήμους (έως 5):",
            options=list(mapping.keys()),
            default=["Χανιά"]
        )

# --- 4. MAIN DASHBOARD ---
if menu == "Επιχειρησιακό Dashboard":
    st.markdown("<div class='report-header'><h2>Consolidated Resilience Dashboard</h2></div>", unsafe_allow_html=True)
    
    if not selected_cities:
        st.warning("⚠️ Παρακαλώ επιλέξτε τουλάχιστον έναν Δήμο από το Sidebar.")
    else:
        # Pipeline Simulation
        results = []
        for name in selected_cities:
            d = mapping[name]
            # Υπολογισμός Resilience Score (CI)
            score = round((d["base_dem"] * 0.3) + (d["pias"] * 50) + (d["vib"] * 0.2), 1)
            color = "#27AE60" if score > 70 else "#E67E22" if score > 55 else "#C0392B"
            results.append({
                "Δήμος": name, "Lat": d["lat"], "Lon": d["lon"], 
                "Score": score, "Color": color, "PIAS": d["pias"], 
                "Dem": d["base_dem"], "Vib": d["vib"], "Sect": d["sect"]
            })
        
        df_res = pd.DataFrame(results)
        focus_city = st.selectbox("Εστίαση & Ανάλυση Μεταβλητών:", selected_cities)
        f_data = df_res[df_res["Δήμος"] == focus_city].iloc[0]

        # --- KPIs ---
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='metric-card'><b>Resilience Score (CI)</b><br><span style='font-size:24px; color:{f_data['Color']};'>{f_data['Score']}</span></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'><b>Policy Alignment (PIAS)</b><br><span style='font-size:24px;'>{f_data['PIAS']:.2f}</span></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-card'><b>Vibrancy (NASA)</b><br><span style='font-size:24px;'>{f_data['Vib']}</span></div>", unsafe_allow_html=True)

        # --- RADAR CHART (COMPARATIVE PROFILE) ---
        st.subheader(f"📊 Συγκριτικό Προφίλ Μεταβλητών: {focus_city}")
        
        categories = ['Οικονομική Ανθεκτικότητα (CI)', 'Ψηφιακή Ζήτηση (Trends)', 
                      'Στρατηγική ΕΣΠΑ (PIAS)', 'Κλαδική Δομή (Sectoral)', 'Vibrancy (NASA)']
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[f_data['Score']/100, f_data['Dem']/100, f_data['PIAS'], f_data['Sect'], f_data['Vib']/100],
            theta=categories, fill='toself', name=focus_city, line_color=f_data['Color']
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=True, height=400)
        st.plotly_chart(fig_radar, use_container_width=True)

        # --- EXPANDER: ANALYSIS OF VARIABLES (The requested section) ---
        with st.expander("🔍 Δείτε τις Μεταβλητές ανά Κατηγορία (Model Features)"):
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                st.markdown("#### ΠΕ1: Σύνθετος Δείκτης (Composite Index)")
                st.write("- **Mr_GVA, Mr_EMP, Mr_GCF:** Μεταβλητές εισοδήματος και εργασίας.")
                st.write("- **Shannon Entropy Weights:** Αυτόματη στάθμιση για αποφυγή υποκειμενικότητας.")
                
                st.markdown("#### ΠΕ2: Δείκτης Ευπάθειας (Vulnerability)")
                st.write("- **NASA Vibrancy Index:** Συνδυασμός νυχτερινού φωτός και κινητικότητας.")
                st.write("- **Lagged CI (t-1):** Για την αποφυγή data leakage στην πρόβλεψη.")
            
            with col_exp2:
                st.markdown("#### ΠΕ3: Policy Alignment (PIAS)")
                st.write("- **Funding Vector:** Το διάνυσμα των επενδύσεων ΕΣΠΑ.")
                st.write("- **Need Vector:** Το διάνυσμα των πραγματικών αναγκών (Inverse Resilience).")
                
                st.markdown("#### ΠΕ4: Sectoral Network")
                st.write("- **NACE Rev.2 Sections:** Κλαδικά δεδομένα με χρήση *Imputation Strategy* για τα κενά (Suppressed Values).")

        # --- MAP & BAR CHART ---
        st.divider()
        col_m, col_g = st.columns([2, 1])
        with col_m:
            st.write("📍 Γεωγραφική Κατανομή")
            m = folium.Map(location=[38.0, 24.0], zoom_start=6, tiles="CartoDB positron")
            for _, r in df_res.iterrows():
                folium.CircleMarker([r["Lat"], r["Lon"]], radius=10, color=r["Color"], fill=True, popup=r["Δήμος"]).add_to(m)
            st_folium(m, width=700, height=350)
        with col_g:
            st.write("📊 Σύγκριση Scores")
            fig_bar = go.Figure(go.Bar(x=df_res["Δήμος"], y=df_res["Score"], marker_color=df_res["Color"]))
            st.plotly_chart(fig_bar, use_container_width=True)

else:
    st.info("🔐 Σελίδα Συμμόρφωσης: Εδώ καταγράφονται τα Audit Logs για τον EU AI Act.")
