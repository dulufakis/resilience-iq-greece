import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from pytrends.request import TrendReq

# --- 1. SETTINGS ---
st.set_page_config(page_title="ResilienceIQ - Ελληνικοί Δήμοι", layout="wide")

st.markdown("""
<style>
    .report-header { background-color: #1E50B4; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    .metric-card {
        background: #ffffff; border-radius: 12px; padding: 15px;
        border-top: 5px solid #1E50B4; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .risk-box { padding: 20px; border-radius: 10px; text-align: center; font-weight: bold; color: white; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. API ENGINE & TRANSLATION ---
mapping = {"Χανιά": "Chania", "Ρόδος": "Rhodes", "Μύκονος": "Mykonos", "Σαντορίνη": "Santorini", "Κέρκυρα": "Corfu"}

@st.cache_data(ttl=3600)
def get_live_demand(city_gr):
    city_en = mapping.get(city_gr, city_gr)
    try:
        pytrends = TrendReq(hl='el-GR', tz=120)
        pytrends.build_payload([f"Tourism {city_en}"], cat=67, timeframe='today 12-m', geo='GR')
        df = pytrends.interest_over_time()
        return round(df.iloc[-1, 0], 1) if not df.empty else 62.0
    except:
        return 62.0

# --- 3. SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield-with-growth.png", width=60)
    st.title("ResilienceIQ")
    city_selected = st.selectbox("Επιλέξτε Δήμο:", list(mapping.keys()))
    
    st.header("🎮 Προσομοιωτής Συναρίου")
    s_demand = st.slider("Μεταβολή Ζήτησης (%)", -100, 50, 0)
    s_mob = st.slider("Μεταβολή Κινητικότητας (%)", -100, 50, 0)
    st.divider()
    selected_bench = st.multiselect("Σύγκριση με:", 
                                   ["Ο Δήμος Σας", "Ανταγωνιστικός Δήμος", "Εθνικός Μέσος Όρος"], 
                                   default=["Ο Δήμος Σας", "Εθνικός Μέσος Όρος"])

# --- 4. CALCULATIONS ---
base_demand = get_live_demand(city_selected)
adj_dem = base_demand * (1 + s_demand/100)
adj_mob = -3.7 * (1 + s_mob/100)
vibrancy = np.clip((adj_dem * 0.4 + (50 + adj_mob) * 0.6), 0, 100)
res_score = round((adj_dem * 0.3) + (vibrancy * 0.4) + (677/20 * 0.3), 1)

r_color = "#27AE60" if res_score > 50 else "#E67E22" if res_score > 35 else "#C0392B"
r_text = "ΧΑΜΗΛΟΣ ΚΙΝΔΥΝΟΣ" if res_score > 50 else "ΜΕΣΑΙΟΣ ΚΙΝΔΥΝΟΣ" if res_score > 35 else "ΥΨΗΛΟΣ ΚΙΝΔΥΝΟΣ"

# --- 5. DASHBOARD ---
st.markdown(f"<div class='report-header'><h2>Ανάλυση Ανθεκτικότητας: Δήμος {city_selected}</h2></div>", unsafe_allow_html=True)

c_main, c_risk = st.columns([3, 1])

with c_main:
    k1, k2, k3 = st.columns(3)
    k1.markdown(f"<div class='metric-card'><b>Resilience Score</b><br><span style='font-size:24px;'>{res_score}</span></div>", unsafe_allow_html=True)
    k2.markdown(f"<div class='metric-card'><b>NASA Vibrancy (Νύχτα)</b><br><span style='font-size:24px;'>{vibrancy:.1f}</span></div>", unsafe_allow_html=True)
    k3.markdown(f"<div class='metric-card'><b>Ζήτηση (Προσαρμοσμένη)</b><br><span style='font-size:24px;'>{adj_dem:.1f}</span></div>", unsafe_allow_html=True)
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=[adj_dem, vibrancy, 50+adj_mob, 677/15, 75],
        theta=['Ζήτηση', 'NASA Vibrancy', 'Κινητικότητα', 'Airbnb Capacity', 'Υποδομές'],
        fill='toself', name=city_selected, line=dict(color='#1E50B4')
    ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=400)
    st.plotly_chart(fig_radar, use_container_width=True)

with c_risk:
    st.markdown(f"<div class='risk-box' style='background-color:{r_color};'>{r_text}</div>", unsafe_allow_html=True)
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number", value=res_score,
        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': r_color}},
        domain={'x': [0, 1], 'y': [0, 1]}
    ))
    fig_gauge.update_layout(height=220)
    st.plotly_chart(fig_gauge, use_container_width=True)
    
    csv = pd.DataFrame([{"Δήμος": city_selected, "Score": res_score}]).to_csv(index=False).encode('utf-8')
    st.download_button("📥 Εξαγωγή Συναρίου", data=csv, file_name=f"resilience_{city_selected}.csv")

if r_text == "ΥΨΗΛΟΣ ΚΙΝΔΥΝΟΣ":
    st.error("🚨 ΠΡΟΕΙΔΟΠΟΙΗΣΗ: Το σενάριο δείχνει κρίσιμη αποδυνάμωση της τουριστικής ανθεκτικότητας.")