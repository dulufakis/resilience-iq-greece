import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import st_folium

# --- 1. SETTINGS & STYLES ---
st.set_page_config(page_title="ResilienceIQ Modern", layout="wide")

st.markdown("""
<style>
    .report-header { background-color: #1E50B4; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center; }
    .metric-card { background: #ffffff; border-radius: 10px; padding: 15px; border-top: 5px solid #1E50B4; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE (Πλήρης Λίστα Δήμων) ---
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

# --- 3. CALCULATIONS (Για όλους τους Δήμους) ---
results = []
for name, d in mapping.items():
    score = round((d["base_dem"] * 0.25) + (d["pias"] * 55) + (d["vib"] * 0.20), 1)
    status = "Safe" if score > 72 else "Warning" if score > 58 else "Critical"
    results.append({
        "Δήμος": name, "Lat": d["lat"], "Lon": d["lon"], 
        "Resilience Score": score, "Κατάσταση": status,
        "PIAS": d["pias"], "Demand": d["base_dem"], "Vibrancy": d["vib"], "Sectoral": d["sect"]
    })
df_all = pd.DataFrame(results).sort_values(by="Resilience Score", ascending=False)

# --- 4. SIDEBAR (Επιλογή για Σύγκριση) ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield-with-growth.png", width=60)
    st.title("ResilienceIQ Pro")
    st.markdown("### 📊 Ανάλυση & Σύγκριση")
    # Περιορισμός επιλογής σε ακριβώς έως 3 Δήμους
    comparison_cities = st.multiselect(
        "Επιλέξτε έως 3 Δήμους για λεπτομερή σύγκριση:",
        options=list(mapping.keys()),
        default=["Χανιά", "Αθήνα"],
        max_selections=3
    )
    st.divider()
    st.info(f"Εμφανίζονται {len(mapping)} Δήμοι στο Dashboard.")

# --- 5. MAIN PAGE ---
st.markdown("<div class='report-header'><h2>Resilience Control Center v5.2</h2></div>", unsafe_allow_html=True)

# --- SECTION A: COMPARATIVE BARS (Μόνο για τους 3 επιλεγμένους) ---
if comparison_cities:
    st.subheader(f"🔄 Σύγκριση Μεταβλητών: {', '.join(comparison_cities)}")
    plot_data = []
    labels = {
        'Resilience Score': 'Συνολικό Score', 
        'Demand': 'Ψηφιακή Ζήτηση', 
        'PIAS': 'Στρατηγική ΕΣΠΑ', 
        'Sectoral': 'Κλαδική Συνοχή', 
        'Vibrancy': 'Vibrancy (NASA)'
    }
    for city in comparison_cities:
        c = df_all[df_all["Δήμος"] == city].iloc[0]
        for key, lab in labels.items():
            val = c[key] * 100 if key in ['PIAS', 'Sectoral'] else c[key]
            plot_data.append({"Δήμος": city, "Μεταβλητή": lab, "Value": val})
    
    fig = px.bar(
        pd.DataFrame(plot_data), 
        x="Value", y="Μεταβλητή", 
        color="Δήμος", barmode="group", 
        orientation='h', text_auto='.1f', 
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    fig.update_layout(xaxis_title="Score (0-100)", yaxis_title="", height=400, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("💡 Επιλέξτε Δήμους από το Sidebar για να ενεργοποιηθεί η συγκριτική ανάλυση.")

# --- SECTION B: RANKING TABLE (Όλοι οι Δήμοι) ---
st.subheader("🏆 Κατάταξη & Επιδόσεις (Πλήρης Λίστα)")
st.dataframe(
    df_all[["Δήμος", "Resilience Score", "Κατάσταση", "PIAS"]],
    column_config={
        "Resilience Score": st.column_config.ProgressColumn("Score", format="%.1f", min_value=0, max_value=100),
        "PIAS": st.column_config.NumberColumn("Alignment", format="%.2f"),
        "Κατάσταση": st.column_config.TextColumn("Status")
    },
    use_container_width=True, hide_index=True
)

# --- SECTION C: GEOSPATIAL MAP (Όλοι οι Δήμοι) ---
st.divider()
st.subheader("📍 Γεωγραφική Διασπορά (Global View)")
m = folium.Map(location=[38.0, 24.0], zoom_start=6, tiles="CartoDB positron")
for _, r in df_all.iterrows():
    # Χρωματική σήμανση βάσει score
    color = "#27AE60" if r["Resilience Score"] > 72 else "#E67E22" if r["Resilience Score"] > 58 else "#C0392B"
    # Αν ο δήμος είναι επιλεγμένος για σύγκριση, κάνουμε το marker πιο έντονο
    radius = 16 if r["Δήμος"] in comparison_cities else 10
    
    folium.CircleMarker(
        [r["Lat"], r["Lon"]], 
        radius=radius, 
        color=color, 
        fill=True, 
        fill_opacity=0.7 if r["Δήμος"] in comparison_cities else 0.4,
        popup=f"<b>{r['Δήμος']}</b><br>Score: {r['Resilience Score']}"
    ).add_to(m)
st_folium(m, width=1100, height=450)
