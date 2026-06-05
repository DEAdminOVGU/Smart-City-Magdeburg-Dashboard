import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime

from utils.live_api import fetch_weather, fetch_elbe_level, fetch_air_quality
from utils.data_loader import (
    load_kiss, load_steuereinnahmen, load_mietspiegel, load_klima_monat
)
from utils.ui_helpers import topic_card, live_card
from utils.constants import LAT, LON, MONTHS_DE

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f'<div class="sidebar-footer">Live data as of {datetime.now().strftime("%H:%M")}</div>',
                unsafe_allow_html=True)
    if st.button("🔄 Refresh Live Data", use_container_width=True):
        fetch_weather.clear()
        fetch_elbe_level.clear()
        fetch_air_quality.clear()
        st.rerun()

# ── Hero banner ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:28px;">
  <div style="font-size:0.8rem;font-weight:700;color:#007A6E;text-transform:uppercase;
              letter-spacing:0.12em;margin-bottom:4px;">Smart City Dashboard</div>
  <h1 style="font-size:2.6rem!important;font-weight:900!important;
             color:#1A1A1A!important;line-height:1.1;margin:0 0 8px 0;">
    Magdeburg in Zahlen
  </h1>
  <p style="font-size:1.05rem;color:#666;max-width:620px;margin:0;">
    Live city pulse and historical trends for Magdeburg —
    Saxony-Anhalt's capital on the Elbe.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Live data strip ───────────────────────────────────────────────────────────
st.markdown("#### 🔴 Live Indicators")

weather = fetch_weather()
elbe    = fetch_elbe_level()
pm25    = fetch_air_quality()

c1, c2, c3, c4 = st.columns(4)

with c1:
    if weather and weather.get("temperature") is not None:
        temp  = weather["temperature"]
        cond  = weather.get("condition", "").capitalize()
        color = "#E87722" if temp > 20 else ("#004B87" if temp < 5 else "#007A6E")
        st.markdown(live_card("🌡️", "Temperature", f"{temp} °C", cond, color),
                    unsafe_allow_html=True)
    else:
        st.markdown(live_card("🌡️", "Temperature", "—", "Unavailable", "#ccc"),
                    unsafe_allow_html=True)

with c2:
    if weather and weather.get("wind_speed") is not None:
        wind = weather["wind_speed"]
        prec = weather.get("precipitation", 0) or 0
        color = "#004B87" if wind > 30 else "#007A6E"
        st.markdown(live_card("💨", "Wind Speed", f"{wind} km/h",
                              f"Precipitation: {prec} mm", color),
                    unsafe_allow_html=True)
    else:
        st.markdown(live_card("💨", "Wind Speed", "—", "Unavailable", "#ccc"),
                    unsafe_allow_html=True)

with c3:
    if elbe and elbe.get("value") is not None:
        level = elbe["value"]
        ts    = elbe.get("timestamp", "")[:16].replace("T", " ")
        color = "#C0392B" if level > 600 else ("#E87722" if level > 400 else "#007A6E")
        status = "⚠️ Elevated" if level > 400 else "Normal"
        st.markdown(live_card("🌊", "Elbe Level", f"{level} cm", f"{status} · {ts}", color),
                    unsafe_allow_html=True)
    else:
        st.markdown(live_card("🌊", "Elbe Level", "—", "Unavailable", "#ccc"),
                    unsafe_allow_html=True)

with c4:
    if pm25 is not None:
        color = "#C0392B" if pm25 > 15 else "#007A6E"
        note  = "⚠️ Above WHO limit" if pm25 > 15 else "Within WHO guideline"
        st.markdown(live_card("🫁", "PM2.5", f"{pm25} µg/m³", note, color),
                    unsafe_allow_html=True)
    else:
        st.markdown(live_card("🫁", "PM2.5", "No sensors", "Unavailable", "#ccc"),
                    unsafe_allow_html=True)

st.divider()

# ── Pre-compute topic card values ─────────────────────────────────────────────
cards = {}

# Climate
try:
    df_k = load_klima_monat()
    baseline = df_k[(df_k["year"] >= 1961) & (df_k["year"] <= 1990)]["MO_TT"].mean()
    yearly   = df_k[df_k["MO_TT"].notna()].groupby("year")["MO_TT"].mean()
    completed = yearly[yearly.index < datetime.now().year]
    la  = round(float(completed.iloc[-1]) - baseline, 1)
    pya = round(float(completed.iloc[-2]) - baseline, 1)
    yr  = int(completed.index[-1])
    sign = "+" if la >= 0 else ""
    d_sign = "+" if (la - pya) >= 0 else ""
    cards["climate"] = dict(
        icon="🌡️", title="Climate",
        value=f"{sign}{la}°C", unit="vs 1961–1990 baseline",
        delta=f"{d_sign}{la-pya:.1f}°C vs {yr-1}",
        delta_pos=False,  # warming = concern
        year=str(yr), color="#00897B",
    )
except Exception:
    cards["climate"] = None

# Population
try:
    df_p = load_kiss("bevoelkerung/bevoelkerungsbestand-monatlich.json")
    df_p = df_p.sort_values("Jahr")
    cur_year  = int(df_p["Jahr"].max())
    prev_year = cur_year - 1
    cur_pop   = int(df_p[df_p["Jahr"] == cur_year]["var5"].mean())
    prev_pop  = int(df_p[df_p["Jahr"] == prev_year]["var5"].mean())
    delta_pop = cur_pop - prev_pop
    d_sign    = "+" if delta_pop >= 0 else ""
    cards["population"] = dict(
        icon="👥", title="Population",
        value=f"{cur_pop:,}".replace(",", "."), unit="residents (Hauptwohnsitz)",
        delta=f"{d_sign}{delta_pop:,} vs {prev_year}".replace(",", "."),
        delta_pos=delta_pop >= 0,
        year=str(cur_year), color="#1565C0",
    )
except Exception:
    cards["population"] = None

# Housing / Rent
try:
    df_r     = load_mietspiegel()
    ly       = int(df_r["year"].max())
    py       = ly - 1
    avg_ly   = df_r[df_r["year"] == ly]["nettokaltmiete_pro_qm"].mean()
    avg_py   = df_r[df_r["year"] == py]["nettokaltmiete_pro_qm"].mean()
    diff     = avg_ly - avg_py
    d_sign   = "+" if diff >= 0 else ""
    cards["housing"] = dict(
        icon="🏘️", title="Housing",
        value=f"€{avg_ly:.2f}/m²", unit="avg net cold rent",
        delta=f"{d_sign}€{diff:.2f}/m² vs {py}",
        delta_pos=False,  # rising rent = concern for residents
        year=str(ly), color="#E65100",
    )
except Exception:
    cards["housing"] = None

# Mobility
try:
    df_kfz = load_kiss("verkehr/entwicklung-des-kraftfahrzeugbestandes-in-magdeburg.json")
    df_kfz = df_kfz.sort_values("Jahr")
    df_pop_mob = load_kiss("bevoelkerung/bevoelkerungsbestand-monatlich.json")
    df_pop_mob = df_pop_mob.sort_values("Jahr")
    kfz_ly = int(df_kfz["Jahr"].max())
    kfz_py = kfz_ly - 1
    pkw_ly = float(df_kfz[df_kfz["Jahr"] == kfz_ly]["var4"].values[0])
    pkw_py = float(df_kfz[df_kfz["Jahr"] == kfz_py]["var4"].values[0])
    pop_ly = float(df_pop_mob[df_pop_mob["Jahr"] == kfz_ly]["var5"].mean())
    pop_py = float(df_pop_mob[df_pop_mob["Jahr"] == kfz_py]["var5"].mean())
    cper_ly = round(pkw_ly / pop_ly * 1000)
    cper_py = round(pkw_py / pop_py * 1000)
    diff_c  = cper_ly - cper_py
    d_sign  = "+" if diff_c >= 0 else ""
    cards["mobility"] = dict(
        icon="🚗", title="Mobility",
        value=str(cper_ly), unit="cars per 1,000 residents",
        delta=f"{d_sign}{diff_c} vs {kfz_py}",
        delta_pos=False,  # more cars = less sustainable
        year=str(kfz_ly), color="#6A1B9A",
    )
except Exception:
    cards["mobility"] = None

# Economy / Tax
try:
    df_tax   = load_steuereinnahmen()
    tax_cols = ["gewerbesteuer", "gemeindeanteil-an-der-einkommensteuer",
                "grundsteuer_b", "gemeindeanteil-an-der-umsatzsteuer"]
    t24 = sum(float(df_tax[df_tax["jahr"] == 2024].iloc[0].get(c, 0) or 0) for c in tax_cols)
    t23 = sum(float(df_tax[df_tax["jahr"] == 2023].iloc[0].get(c, 0) or 0) for c in tax_cols)
    pct = (t24 - t23) / t23 * 100
    d_sign = "+" if pct >= 0 else ""
    cards["economy"] = dict(
        icon="💶", title="Economy",
        value=f"€{t24/1e6:.0f}M", unit="tax revenue (2024)",
        delta=f"{d_sign}{pct:.1f}% vs 2023",
        delta_pos=pct >= 0,
        year="2024", color="#2E7D32",
    )
except Exception:
    cards["economy"] = None

# ── Topic card grid ───────────────────────────────────────────────────────────
st.markdown("#### City at a Glance")

row1 = st.columns(3)
row2 = st.columns(3)
card_order = ["climate", "population", "housing", "mobility", "economy"]
cols = [row1[0], row1[1], row1[2], row2[0], row2[1]]

for col, key in zip(cols, card_order):
    c = cards.get(key)
    with col:
        if c:
            st.markdown(topic_card(
                c["icon"], c["title"], c["value"], c["unit"],
                c["delta"], c["delta_pos"], c["year"], c["color"],
            ), unsafe_allow_html=True)
        else:
            st.markdown(topic_card("❓", key.title(), "—", "data unavailable",
                                   "no data", True, "—", "#ccc"),
                        unsafe_allow_html=True)

# Empty 6th cell — point to map
with row2[2]:
    st.markdown("""
<div style="background:#f0f7f6;border-radius:14px;padding:22px 18px;
            box-shadow:0 2px 16px rgba(0,0,0,0.05);
            border-top:4px solid #007A6E;margin-bottom:4px;
            display:flex;flex-direction:column;align-items:center;
            justify-content:center;text-align:center;min-height:160px;">
  <div style="font-size:2.4rem;margin-bottom:8px;">🗺️</div>
  <div style="font-size:0.85rem;font-weight:700;color:#007A6E;">Interactive City Map</div>
  <div style="font-size:0.78rem;color:#999;margin-top:4px;">Scroll down to explore</div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── City Map ───────────────────────────────────────────────────────────────────
st.markdown("#### 🗺️ City Map")

landmarks = [
    {"name": "Rathaus Magdeburg",          "lat": 52.1316, "lon": 11.6371, "desc": "City Hall"},
    {"name": "Magdeburger Dom",             "lat": 52.1289, "lon": 11.6401, "desc": "Cathedral (1209)"},
    {"name": "Elbe — Strombrücke",          "lat": 52.1253, "lon": 11.6314, "desc": "Elbe water level gauge"},
    {"name": "Magdeburg Hauptbahnhof",      "lat": 52.1306, "lon": 11.6267, "desc": "Main train station"},
    {"name": "Otto-von-Guericke-Universität","lat": 52.1392, "lon": 11.6467, "desc": "State university, ~14,000 students"},
]

m = folium.Map(location=[LAT, LON], zoom_start=13, tiles="OpenStreetMap")
for lm in landmarks:
    folium.Marker(
        location=[lm["lat"], lm["lon"]],
        popup=folium.Popup(f"<b>{lm['name']}</b><br>{lm['desc']}", max_width=220),
        tooltip=lm["name"],
        icon=folium.Icon(color="darkblue", icon="info-sign"),
    ).add_to(m)

st_folium(m, width="100%", height=420, returned_objects=[])
st.caption("Map: © OpenStreetMap contributors · Landmarks: manually curated · "
           "Live data: Bright Sky/DWD, PEGELONLINE/WSV, Sensor.Community")
