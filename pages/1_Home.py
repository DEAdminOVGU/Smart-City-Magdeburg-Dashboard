import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime

from utils.live_api import fetch_weather, fetch_elbe_level, fetch_air_quality
from utils.data_loader import load_kiss, load_steuereinnahmen, load_mietspiegel
from utils.constants import LAT, LON

st.title("Smart City Magdeburg — Overview")
st.caption("Live city pulse · Data: DWD, WSV, Sensor.Community, KISS-MD, Landeshauptstadt Magdeburg")

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Landeshauptstadt Magdeburg")
    st.caption(f"Last refreshed: {datetime.now().strftime('%H:%M:%S')}")
    if st.button("🔄 Refresh Live Data"):
        fetch_weather.clear()
        fetch_elbe_level.clear()
        fetch_air_quality.clear()
        st.rerun()

# ── Live KPI cards ────────────────────────────────────────────────────────────
st.subheader("Live City Indicators")

weather = fetch_weather()
elbe = fetch_elbe_level()
pm25 = fetch_air_quality()

c1, c2, c3, c4 = st.columns(4)

with c1:
    if weather:
        temp = weather.get("temperature")
        cond = weather.get("condition", "")
        wind = weather.get("wind_speed")
        st.metric("🌡️ Temperature", f"{temp} °C" if temp is not None else "—", help="Source: Bright Sky / DWD")
        st.caption(f"Condition: {cond} · Wind: {wind} km/h" if wind else cond)
    else:
        st.metric("🌡️ Temperature", "—")
        st.caption("Live data unavailable")

with c2:
    if weather:
        wind = weather.get("wind_speed")
        prec = weather.get("precipitation")
        st.metric("💨 Wind Speed", f"{wind} km/h" if wind is not None else "—", help="Source: Bright Sky / DWD")
        st.caption(f"Precipitation: {prec} mm" if prec is not None else "")
    else:
        st.metric("💨 Wind Speed", "—")
        st.caption("Live data unavailable")

with c3:
    if elbe:
        level = elbe.get("value")
        ts = elbe.get("timestamp", "")[:16].replace("T", " ") if elbe.get("timestamp") else ""
        if level is not None:
            if level < 400:
                colour = "normal"
                label = "Normal"
            elif level < 600:
                colour = "off"
                label = "Elevated"
            else:
                colour = "inverse"
                label = "High"
            st.metric("🌊 Elbe Level", f"{level} cm", delta=label,
                      delta_color=colour, help="Source: PEGELONLINE / WSV · Station Magdeburg-Strombrücke")
            st.caption(f"Measured: {ts}")
        else:
            st.metric("🌊 Elbe Level", "—")
    else:
        st.metric("🌊 Elbe Level", "—")
        st.caption("Live data unavailable")

with c4:
    if pm25 is not None:
        who_limit = 15.0
        delta_val = round(pm25 - who_limit, 1)
        st.metric("💨 PM2.5", f"{pm25} µg/m³",
                  delta=f"{delta_val:+.1f} vs WHO limit",
                  delta_color="inverse" if delta_val > 0 else "normal",
                  help="Source: Sensor.Community · avg of sensors within 10 km")
        st.caption("WHO 24h guideline: 15 µg/m³")
    else:
        st.metric("💨 PM2.5", "No sensors active")
        st.caption("Sensor.Community: no nearby sensors online")

st.divider()

# ── Static city KPIs ──────────────────────────────────────────────────────────
st.subheader("City at a Glance")

try:
    pop_df = load_kiss("bevoelkerung/bevoelkerungsbestand-monatlich.json")
    # var5 = total Hauptwohnsitz; sort by year to get latest
    pop_df_sorted = pop_df.sort_values("Jahr")
    latest_pop = int(pop_df_sorted["var5"].iloc[-1])
except Exception:
    latest_pop = None

try:
    kfz_df = load_kiss("verkehr/kraftfahrzeugbestand-monatlich.json")
    # "Kraftfahrzeugbestand" is the label for var3 (total registered vehicles)
    kfz_df_sorted = kfz_df.sort_values("Jahr")
    latest_kfz = int(kfz_df_sorted["Kraftfahrzeugbestand"].iloc[-1])
except Exception:
    latest_kfz = None

try:
    tax_df = load_steuereinnahmen()
    tax_2024 = tax_df[tax_df["jahr"] == 2024].iloc[0]
    major_cols = ["gewerbesteuer", "gemeindeanteil-an-der-einkommensteuer",
                  "grundsteuer_b", "gemeindeanteil-an-der-umsatzsteuer"]
    total_tax = sum(float(tax_2024.get(c, 0) or 0) for c in major_cols)
except Exception:
    total_tax = None

try:
    rent_df = load_mietspiegel()
    latest_year = rent_df["year"].max()
    avg_rent = rent_df[rent_df["year"] == latest_year]["nettokaltmiete_pro_qm"].mean()
except Exception:
    avg_rent = None

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric("👥 Population", f"{latest_pop:,}".replace(",", ".") if latest_pop else "—",
              help="Hauptwohnsitz · Source: KISS-MD / Einwohnermeldeamt")
with k2:
    st.metric("🚗 Registered Vehicles", f"{latest_kfz:,}".replace(",", ".") if latest_kfz else "—",
              help="Source: KISS-MD / Kraftfahrtbundesamt")
with k3:
    st.metric("🏛️ Tax Revenue (2024)", f"€{total_tax/1e6:.0f} M" if total_tax else "—",
              help="Major taxes: Gewerbesteuer, Einkommensteuer, Grundsteuer B, Umsatzsteuer")
with k4:
    st.metric("🏠 Avg Rent/m²", f"€{avg_rent:.2f}" if avg_rent else "—",
              help=f"Nettokaltmiete · Source: Mietspiegel Magdeburg {latest_year if avg_rent else ''}")

st.divider()

# ── Folium map ─────────────────────────────────────────────────────────────────
st.subheader("City Map")

landmarks = [
    {"name": "Rathaus Magdeburg", "lat": 52.1316, "lon": 11.6371, "desc": "City Hall"},
    {"name": "Magdeburger Dom", "lat": 52.1289, "lon": 11.6401, "desc": "Cathedral (1209)"},
    {"name": "Elbe — Strombrücke", "lat": 52.1253, "lon": 11.6314, "desc": "Elbe water level gauge station"},
    {"name": "Magdeburg Hauptbahnhof", "lat": 52.1306, "lon": 11.6267, "desc": "Main train station"},
    {"name": "Otto-von-Guericke-Universität", "lat": 52.1392, "lon": 11.6467, "desc": "State university, ~14,000 students"},
]

m = folium.Map(location=[LAT, LON], zoom_start=13, tiles="OpenStreetMap")

for lm in landmarks:
    folium.Marker(
        location=[lm["lat"], lm["lon"]],
        popup=folium.Popup(f"<b>{lm['name']}</b><br>{lm['desc']}", max_width=200),
        tooltip=lm["name"],
        icon=folium.Icon(color="darkblue", icon="info-sign"),
    ).add_to(m)

st_folium(m, width="100%", height=420, returned_objects=[])

st.caption("Map data: © OpenStreetMap contributors · Landmarks: manually curated")
