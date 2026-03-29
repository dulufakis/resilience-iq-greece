import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from pytrends.request import TrendReq
import folium
from streamlit_folium import st_folium

# --- 1. SETTINGS & STYLES ---
st.set_page_config(page_title="ResilienceIQ Maps", layout="wide")

st.markdown("""
<style>
    .report-header { background-color: #1E50B4; color: white; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
    .metric-card { background: #ffffff; border-radius: 10px; padding: 12px; border-top: 4px solid #1E50B4; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 8px; }
    .risk-box { padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; color: white; margin-top: 8px; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA & GEOGRAPHY ENGINE ---
# Προσθήκη συντεταγμένων για το χάρτη
mapping = {
    "Χανιά": {"en": "Chania", "lat": 35.5138, "lon": 24.0180},
    "Ρόδος": {"en": "Rhodes", "lat": 36.4341, "lon": 28.2176},
    "Μύκονος": {"en": "Mykonos", "lat": 37.4467, "lon": 25.3289},
    "Σαντορίνη": {"en": "Santorini", "lat": 36.3932, "lon": 25.4615},
    "Κέρκυρα": {"en": "Corfu", "lat": 39.6243, "lon": 19.9217}
}

@st.cache_data(ttl=3600)
def get_live_demand(city_gr):
    city_en = mapping[city_gr]["en"]
    try:
        pytrends = TrendReq(hl='el-GR', tz=120)
        pytrends.build_payload([f"Tourism {city_en}"], cat=67, timeframe='today 12-m', geo='GR')
        df = pytrends.interest_over_time()
        return round(df.iloc[-1, 0], 1) if not df.empty else 62.0
    except:
        return 62.0

# --- 3. SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield-with-growth.png", width=50)
    st.title("ResilienceIQ")
    city_selected = st.selectbox("Επιλέξτε Δήμο:", list(mapping.keys()))
    
    st.header("🎮 Προσομοιωτής Συναρίου")
    s_demand = st.slider("Μεταβολή Ζήτησης (%)", -100, 50, 0)
    s_mob = st.slider("Μεταβολή Κινητικότητας (%)", -100, 50, 0)
    st.divider()
    st.caption("Tier 0 - Geographic Edition")

# --- 4. CALCULATION LOGIC ---
base_demand = get_live_demand(city_selected)
adj_dem = base_demand * (1 + s_demand/100)
adj_mob = -3.7 * (1 + s_mob/100)
vibrancy = np.clip((adj_dem * 0.4 + (50 + adj_mob) * 0.6), 0, 100)
# Χρησιμοποιούμε σταθερά Airbnb listings (677) για το Tier 0
res_score = round((adj_dem * 0.3) + (vibrancy * 0.4) + (677/20 * 0.3), 1)

# Risk Color & Text Logic
if res_score > 50:
    r_color, r_text = "#27AE60", "ΧΑΜΗΛΟΣ ΚΙΝΔΥΝΟΣ" # Green
elif res_score > 35:
    r_color, r_text = "#E67E22", "ΜΕΣΑΙΟΣ ΚΙΝΔΥΝΟΣ" # Orange
else:
    r_color, r_text = "#C0392B", "ΥΨΗΛΟΣ ΚΙΝΔΥΝΟΣ" # Red

# --- 5. MAIN DASHBOARD ---
st.markdown(f"<div class='report-header'><h2>{city_selected}: Γεωγραφική Ανάλυση Ανθεκτικότητας</h2></div>", unsafe_allow_html=True)

# ROW 1: KPIs & RISK METER
c_kpi, c_risk = st.columns([3, 1])

with c_kpi:
    k1, k2, k3 = st.columns(3)
    k1.markdown(f"<div class='metric-card'><b>Resilience Score</b><br><span style='font-size:22px;'>{res_score}</span></div>", unsafe_allow_html=True)
    k2.markdown(f"<div class='metric-card'><b>NASA Vibrancy</b><br><span style='font-size:22px;'>{vibrancy:.1f}</span></div>", unsafe_allow_html=True)
    k3.markdown(f"<div class='metric-card'><b>Ζήτηση (Adj)</b><br><span style='font-size:22px;'>{adj_dem:.1f}</span></div>", unsafe_allow_html=True)

with c_risk:
    st.markdown(f"<div class='risk-box' style='background-color:{r_color};'>{r_text}</div>", unsafe_allow_html=True)

st.divider()

# ROW 2: MAP & RADAR
c_map, c_radar = st.columns([2, 1])

with c_map:
    st.subheader("Γεωγραφικός Χάρτης Κινδύνου")
    # Δημιουργία Χάρτη (Folium)
    m = folium.Map(location=[38.3, 24.5], zoom_start=6, tiles="CartoDB positron")
    
    # Προσθήκη Κυκλικού Δείκτη για τον επιλεγμένο Δήμο
    city_data = mapping[city_selected]
    folium.CircleMarker(
        location=[city_data["lat"], city_data["lon"]],
        radius=15, popup=f"Δήμος {city_selected}<br>Score: {res_score}",
        color=r_color, fill=True, fill_color=r_color, fill_opacity=0.7
    ).add_to(m)
    
    # Εμφάνιση Χάρτη στο Streamlit
    st_folium(m, width=700, height=400)

with c_radar:
    st.subheader("Resilience Profile")
    fig_radar = go.Figure(go.Scatterpolar(
        r=[adj_dem, vibrancy, 50+adj_mob, 677/15, 75],
        theta=['Ζήτηση', 'NASA Vibrancy', 'Κινητικότητα', 'Capacity', 'Υποδομές'],
        fill='toself', name=city_selected, line=dict(color='#1E50B4')
    ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=400, margin=dict(t=20, b=20))
    st.plotly_chart(fig_radar, use_container_width=True)

# ALERT & EXPORT
if r_text == "ΥΨΗΛΟΣ ΚΙΝΔΥΝΟΣ":
    st.error("🚨 ΠΡΟΕΙΔΟΠΟΙΗΣΗ: Το σενάριο δείχνει κρίσιμη αποδυνάμωση της τουριστικής ανθεκτικότητας.")

csv = pd.DataFrame([{"Δήμος": city_selected, "Score": res_score}]).to_csv(index=False).encode('utf-8')
st.download_button("📥 Εξαγωγή Δεδομένων Συναρίου", data=csv, file_name=f"resilience_{city_selected}.csv")
