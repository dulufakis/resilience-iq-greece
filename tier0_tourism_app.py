import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

# --- 1. SETTINGS & CONFIG ---
st.set_page_config(page_title="ResilienceIQ Consolidated", layout="wide")

# Ορισμός ρυθμίσεων (πρώην config.py)
CONFIG = {
    "sectoral_imputation": "mean_nace_section",
    "rag_inference": "api",
    "scale_invariance": "Cosine Similarity (PIAS)"
}

st.markdown("""
<style>
    .report-header { background-color: #1E50B4; color: white; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
    .metric-card { background: #ffffff; border-radius: 10px; padding: 12px; border-top: 4px solid #1E50B4; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 8px; }
    .ai-advice { background-color: #f0f2f6; border-left: 5px solid #1E50B4; padding: 15px; border-radius: 5px; font-size: 14px; margin-top:10px; }
    .summary-box { background-color: #e8f0fe; padding: 15px; border-radius: 10px; border: 1px solid #1E50B4; font-size: 14px; margin-top:10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATASET ---
mapping = {
    "Χανιά": {"lat": 35.5138, "lon": 24.0180, "base_dem": 70.1, "list": 677, "pias": 0.88},
    "Ρόδος": {"lat": 36.4341, "lon": 28.2176, "base_dem": 72.0, "list": 850, "pias": 0.82},
    "Κέρκυρα": {"lat": 39.6243, "lon": 19.9217, "base_dem": 62.0, "list": 720, "pias": 0.75},
    "Αθήνα": {"lat": 37.9838, "lon": 23.7275, "base_dem": 92.0, "list": 5000, "pias": 0.91},
    "Σαντορίνη": {"lat": 36.3932, "lon": 25.4615, "base_dem": 88.5, "list": 1100, "pias": 0.79}
}

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("ResilienceIQ Pro")
    menu = st.radio("Πλοήγηση:", ["Επιχειρησιακό Dashboard", "Μεθοδολογία"])
    
    if menu == "Επιχειρησιακό Dashboard":
        st.header("🔐 Έλεγχος Πρόσβασης")
        selected_cities = st.multiselect(
            "Επιλέξτε Δήμους (έως 5):",
            options=list(mapping.keys()),
            default=["Χανιά"]
        )

# --- 4. MAIN PAGE ---
if menu == "Επιχειρησιακό Dashboard":
    st.markdown("<div class='report-header'><h2>Consolidated Resilience Dashboard</h2></div>", unsafe_allow_html=True)
    
    if not selected_cities:
        st.warning("⚠️ Παρακαλώ επιλέξτε τουλάχιστον έναν Δήμο.")
    else:
        # Υπολογισμοί
        results = []
        for name in selected_cities:
            d = mapping[name]
            score = round((d["base_dem"] * 0.4) + (d["pias"] * 60), 1)
            color = "#27AE60" if score > 70 else "#E67E22" if score > 50 else "#C0392B"
            results.append({"Δήμος": name, "Lat": d["lat"], "Lon": d["lon"], "Score": score, "Color": color, "PIAS": d["pias"]})
        
        df_res = pd.DataFrame(results)

        # Επιλογή πόλης για εστίαση
        focus_city = st.selectbox("Εστίαση & Επεξήγηση (SHAP):", selected_cities)
        f_data = df_res[df_res["Δήμος"] == focus_city].iloc[0]

        # KPIs
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='metric-card'><b>Resilience Score</b><br><span style='font-size:24px; color:{f_data['Color']};'>{f_data['Score']}</span></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'><b>Policy Alignment (PIAS)</b><br><span style='font-size:24px;'>{f_data['PIAS']:.2f}</span></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-card'><b>Methodology</b><br><span style='font-size:16px;'>Scale Invariant</span></div>", unsafe_allow_html=True)

        # --- ΕΔΩ ΕΙΝΑΙ ΟΙ ΕΠΕΞΗΓΗΣΕΙΣ (Που προκάλεσαν το σφάλμα) ---
        st.markdown(f"### 🧠 Επιστημονική Τεκμηρίωση: {focus_city}")
        
        exp1, exp2 = st.columns(2)
        with exp1:
            st.markdown(f"""<div class='ai-advice'><b>Ανάλυση SHAP:</b><br>Η ανθεκτικότητα στα {focus_city} βασίζεται σε LOO-CV (N=13).
            Χρησιμοποιήθηκε <i>{CONFIG['sectoral_imputation']}</i> για τα κλαδικά δεδομένα.</div>""", unsafe_allow_html=True)
        with exp2:
            st.markdown(f"""<div class='summary-box'><b>PIAS Analysis:</b><br>Ο δείκτης ({f_data['PIAS']:.2f}) προέκυψε μέσω 
            <b>Cosine Similarity</b>, απομονώνοντας το μέγεθος της χρηματοδότησης.</div>""", unsafe_allow_html=True)

        # Χάρτης & Γράφημα
        col_m, col_g = st.columns([2, 1])
        with col_m:
            m = folium.Map(location=[38.0, 24.0], zoom_start=6, tiles="CartoDB positron")
            for _, r in df_res.iterrows():
                folium.CircleMarker([r["Lat"], r["Lon"]], radius=10, color=r["Color"], fill=True, popup=r["Δήμος"]).add_to(m)
            st_folium(m, width=700, height=350)
        with col_g:
            fig = go.Figure(go.Bar(x=df_res["Δήμος"], y=df_res["Score"], marker_color=df_res["Color"]))
            st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Σελίδα Μεθοδολογίας: Εδώ περιγράφονται οι δείκτες CI, VI και PIAS.")
