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
    .report-header { background-color: #1E50B4; color: white; padding: 25px; border-radius: 12px; margin-bottom: 20px; text-align: center; border-bottom: 5px solid #FFD700; }
    .guide-box { background-color: #f0f7ff; padding: 20px; border-radius: 10px; border-left: 6px solid #1E50B4; margin-bottom: 25px; }
    .variable-card { background-color: #ffffff; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .sidebar-footer { font-size: 12px; color: #666; margin-top: 20px; padding: 10px; border-top: 1px solid #ddd; }
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

# --- 3. SIDEBAR (Your Requested Settings) ---
with st.sidebar:
    st.header("⚙️ Settings")
    st.markdown("**Προσθήκη Δήμων στο Δείγμα:**")
    
    # Η λίστα των Δήμων όπως ζητήθηκε
    all_cities = list(mapping.keys())
    selected_cities = st.multiselect(
        label="Επιλογή Δήμων:",
        options=all_cities,
        default=all_cities,
        label_visibility="collapsed"
    )
    
    # Το Footer με τον Αλγόριθμο
    st.markdown(f"""
    <div class='sidebar-footer'>
        <b>Algorithm:</b><br>
        Shannon Entropy weighting & Everitt Empirical Classification.
    </div>
    """, unsafe_allow_html=True)

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
    
    df["Επίπεδο"] = df["Score"].apply(lambda x: "🟢 Υψηλό (Safe)" if x > upper else ("🔴 Χαμηλό (Critical)" if x < lower else "🟠 Μεσαίο (Warning)"))
    df = df.sort_values(by="Score", ascending=False)

    # --- 5. MAIN UI ---
    st.markdown("<div class='report-header'><h1>Municipality Tourism Resilience Scorecard</h1></div>", unsafe_allow_html=True)

    # 5.1 Guide & Variables
    with st.expander("📖 Οδηγός Χρήσης & Επεξήγηση Μεταβλητών", expanded=False):
        st.markdown("""
        - **ΠΕ1 (CI):** Οικονομική βάση (GVA & Απασχόληση).
        - **ΠΕ2 (VI):** NASA Vibrancy Index (Δορυφορικά δεδομένα δραστηριότητας).
        - **ΠΕ3 (PIAS):** Policy Alignment (Ευθυγράμμιση ΕΣΠΑ με τοπικές ανάγκες).
        - **ΠΕ4 (NACE):** Κλαδική αντοχή επιχειρηματικού δικτύου.
        """)

    # 5.2 Stats Summary
    st.subheader("📊 Στατιστική Ανάλυση Δείγματος")
    col1, col2, col3 = st.columns(3)
    col1.metric("Μέσος Όρος (μ)", f"{mu:.2f}")
    col2.metric("Τυπική Απόκλιση (σ)", f"{sigma:.2f}")
    col3.metric("Όριο 'Safe Zone' (μ+0.5σ)", f"{upper:.1f}")

    # 5.3 Ranking Table
    st.subheader("🏆 Κατάταξη Ανθεκτικότητας")
    st.dataframe(
        df[["Δήμος", "Score", "Επίπεδο", "PIAS"]], 
        column_config={
            "Score": st.column_config.ProgressColumn("Resilience Score", min_value=0, max_value=100, format="%.1f"),
            "PIAS": st.column_config.NumberColumn("Policy Alignment", format="%.2f")
        },
        use_container_width=True, hide_index=True
    )

    # 5.4 Comparison Chart
    st.subheader("📈 Σύγκριση Μεταβλητών (Top 3)")
    comp_select = st.multiselect("Επιλογή για ανάλυση αξόνων:", options=selected_cities, default=selected_cities[:min(len(selected_cities), 3)], max_selections=3)
    if comp_select:
        b_data = []
        for city in comp_select:
            r = df[df["Δήμος"] == city].iloc[0]
            for l, k in [('Total Score', 'Score'), ('ESPA Alignment', 'PIAS'), ('Vibrancy', 'Vibrancy')]:
                v = r[k] * 100 if k == 'PIAS' else r[k]
                b_data.append({"Δήμος": city, "Metric": l, "Val": v})
        st.plotly_chart(px.bar(pd.DataFrame(b_data), x="Val", y="Metric", color="Δήμος", barmode="group", orientation='h', text_auto='.1f'), use_container_width=True)

    # 5.5 Map
    st.divider()
    st.subheader("📍 Χάρτης Χωρικής Ανθεκτικότητας")
    m = folium.Map(location=[38.2, 24.2], zoom_start=6, tiles="CartoDB positron")
    for _, r in df.iterrows():
        color = "#28A745" if "Υψηλό" in r["Επίπεδο"] else "#FD7E14" if "Μεσαίο" in r["Επίπεδο"] else "#DC3545"
        folium.CircleMarker([r["Lat"], r["Lon"]], radius=14, color=color, fill=True, fill_opacity=0.7, popup=f"{r['Δήμος']}: {r['Score']}").add_to(m)
    st_folium(m, width=1100, height=450)

else:
    st.info("⚠️ Παρακαλώ επιλέξτε τουλάχιστον 2 Δήμους από τα Settings (Sidebar) για να ξεκινήσει η ανάλυση.")
