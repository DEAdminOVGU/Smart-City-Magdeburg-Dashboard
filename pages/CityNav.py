import json
import os
import streamlit as st
import streamlit.components.v1 as components
import folium
from folium.plugins import MarkerCluster, HeatMap
import plotly.graph_objects as go
import pandas as pd

from utils.live_api   import (fetch_weather, fetch_elbe_level,
                               load_mvb_stops, fetch_departures,
                               fetch_service_disruptions)
from utils.overpass   import fetch_parking, fetch_charging, fetch_transit_stops, fetch_restaurants
from utils.ui_helpers import section_header, live_card
from utils.i18n import t
from utils.constants  import PLOTLY_TEMPLATE

NAV_ORANGE = "#D4481C"
NAV_AMBER  = "#E8650B"

# ── Page header ───────────────────────────────────────────────────────────────
st.title(t("navi.title"))
st.markdown(
    f"<p style='font-size:0.97rem;color:#64748b;max-width:680px;margin:-6px 0 20px 0;'>"
    f"{t('navi.subtitle')}"
    f"</p>",
    unsafe_allow_html=True,
)

# ── Live data ─────────────────────────────────────────────────────────────────
weather  = fetch_weather()
elbe     = fetch_elbe_level()

temp     = weather.get("temperature")   if weather else None
wind_spd = weather.get("wind_speed")    if weather else None
cond     = weather.get("condition", "") if weather else ""
precip   = weather.get("precipitation") if weather else None
elbe_val = elbe.get("value")            if elbe    else None

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: TRAFFIC ALERTS
# ─────────────────────────────────────────────────────────────────────────────
alerts = []

if temp is not None and temp < 0:
    alerts.append(("🧊 Black Ice Risk",
                   f"Temperature is {temp:.0f}°C — black ice possible on bridges and shaded roads. "
                   "Reduce speed and allow extra braking distance.", "warning"))
elif temp is not None and temp < 3 and precip is not None and precip > 0:
    alerts.append(("⚠️ Slippery Roads",
                   f"Near-freezing temperatures ({temp:.0f}°C) with precipitation. "
                   "Roads may be slippery — drive carefully.", "warning"))

if cond and "fog" in cond.lower():
    alerts.append(("🌫️ Reduced Visibility",
                   "Fog reported — use low beam headlights and increase following distance. "
                   "Check MVB for tram and bus delays.", "warning"))

if wind_spd is not None and wind_spd > 60:
    alerts.append(("💨 Strong Wind",
                   f"Wind gusts of {wind_spd:.0f} km/h. Take extra care on the Elbe bridges "
                   "and avoid cycling on exposed routes.", "warning"))

if elbe_val is not None and elbe_val > 400:
    alerts.append(("🌊 Riverside Roads Affected",
                   f"Elbe at {elbe_val:.0f} cm — low-lying riverside roads near Strombrücke "
                   "may be impassable. Check before travelling.", "error"))

if cond and any(k in cond.lower() for k in ["rain", "hail", "sleet"]):
    alerts.append(("🌧️ Wet Road Conditions",
                   "Rain or precipitation active — stopping distances are longer. "
                   "Cyclists should use lights and avoid puddles near drains.", "info"))

for d in fetch_service_disruptions():
    affects_str = f" (affects: {d['affects']})" if d["affects"] else ""
    alerts.append((f"🚌 {d['head']}", f"{d['text']}{affects_str}", "warning"))

if alerts:
    for label, msg, kind in alerts:
        if kind == "error":
            st.error(f"**{label}** — {msg}")
        elif kind == "warning":
            st.warning(f"**{label}** — {msg}")
        else:
            st.info(f"**{label}** — {msg}")
else:
    st.success("✅ **Traffic conditions normal** — no active weather or road alerts for Magdeburg.")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: FETCH MAP DATA
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(section_header(t("navi.sec.map"), color=NAV_ORANGE), unsafe_allow_html=True)
st.caption(t("navi.map.cap") + " Use the layer control (top-right) to toggle layers on/off.")

with st.spinner("Loading map data from OpenStreetMap…"):
    parking_pts     = fetch_parking()
    charging_pts    = fetch_charging()
    transit_pts     = fetch_transit_stops()
    restaurant_pts  = fetch_restaurants()

# Load accident GeoJSON
accident_pts = []
_acc_path = os.path.join(os.path.dirname(__file__), "..", "data", "Unfaelle", "Magdeburg_Unfallatlas.geojson")
try:
    with open(os.path.normpath(_acc_path), encoding="utf-8") as f:
        _acc_geojson = json.load(f)
    for feat in _acc_geojson.get("features", []):
        props = feat.get("properties", {})
        lat = props.get("lat") or props.get("LAT") or props.get("YLAT")
        lon = props.get("lon") or props.get("LON") or props.get("XLON")
        if lat and lon:
            try:
                accident_pts.append({
                    "lat": float(lat), "lon": float(lon),
                    "year": int(props.get("UJAHR", 0)),
                    "category": int(props.get("UKATEGORIE", 0)),
                    "rad": int(props.get("IstRad", 0)),
                    "pkw": int(props.get("IstPKW", 0)),
                    "fuss": int(props.get("IstFuss", 0)),
                    "krad": int(props.get("IstKrad", 0)),
                })
            except (TypeError, ValueError):
                pass
except Exception:
    pass

# Load district boundaries
_stadtteile_path = os.path.join(os.path.dirname(__file__), "..", "data", "Stadtteile", "Stadtteile.geojson")
stadtteile_geojson = None
try:
    with open(os.path.normpath(_stadtteile_path), encoding="utf-8") as f:
        stadtteile_geojson = json.load(f)
except Exception:
    pass

# ─────────────────────────────────────────────────────────────────────────────
# BUILD FOLIUM MAP
# ─────────────────────────────────────────────────────────────────────────────
m = folium.Map(location=[52.131, 11.640], zoom_start=12, tiles="CartoDB positron")

# Layer 1: District boundaries
if stadtteile_geojson:
    fg_districts = folium.FeatureGroup(name="🏘️ Districts", show=True)
    folium.GeoJson(
        stadtteile_geojson,
        style_function=lambda f: {
            "fillColor": "transparent",
            "color": "#007A6E",
            "weight": 1.5,
            "fillOpacity": 0,
        },
        tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=["District:"]),
    ).add_to(fg_districts)
    fg_districts.add_to(m)

# Layer 2: Transit stops
fg_transit = folium.FeatureGroup(name="🚌 Transit Stops", show=False)
transit_cluster = MarkerCluster(
    options={"maxClusterRadius": 40, "disableClusteringAtZoom": 15}
)
for s in transit_pts:
    color = "#009E3D" if s["type"] == "bus" else "#0057A8"
    icon_char = "🚌" if s["type"] == "bus" else "🚃"
    ref_str = f" ({s['ref']})" if s.get("ref") else ""
    folium.CircleMarker(
        location=[s["lat"], s["lon"]],
        radius=5,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.8,
        popup=folium.Popup(
            f"<b>{icon_char} {s['name']}{ref_str}</b><br>Type: {s['type'].title()} stop",
            max_width=200,
        ),
        tooltip=s["name"],
    ).add_to(transit_cluster)
transit_cluster.add_to(fg_transit)
fg_transit.add_to(m)

# Layer 3: Parking
fg_parking = folium.FeatureGroup(name="🅿️ Parking", show=False)
parking_cluster = MarkerCluster(
    options={"maxClusterRadius": 50, "disableClusteringAtZoom": 15}
)
for p in parking_pts:
    cap_str = f"<br>Capacity: {p['capacity']}" if p.get("capacity") else ""
    typ_str = f"<br>Type: {p['type'].replace('_',' ').title()}" if p.get("type") else ""
    folium.CircleMarker(
        location=[p["lat"], p["lon"]],
        radius=6,
        color="#1565C0",
        fill=True,
        fill_color="#1565C0",
        fill_opacity=0.7,
        popup=folium.Popup(
            f"<b>🅿️ {p['name']}</b>{cap_str}{typ_str}",
            max_width=220,
        ),
        tooltip=f"🅿️ {p['name']}",
    ).add_to(parking_cluster)
parking_cluster.add_to(fg_parking)
fg_parking.add_to(m)

# Layer 4: EV Charging
fg_charging = folium.FeatureGroup(name="⚡ EV Charging", show=False)
for c in charging_pts:
    op_str  = f"<br>Operator: {c['operator']}" if c.get("operator") else ""
    soc_str = f"<br>Sockets: {c['sockets']}"   if c.get("sockets")  else ""
    fee_str = f"<br>Fee: {c['fee']}"            if c.get("fee")      else ""
    folium.Marker(
        location=[c["lat"], c["lon"]],
        popup=folium.Popup(
            f"<b>⚡ {c['name']}</b>{op_str}{soc_str}{fee_str}",
            max_width=220,
        ),
        tooltip=f"⚡ {c['name']}",
        icon=folium.DivIcon(
            html=(
                '<div style="background:#F59E0B;border:2px solid #92400E;'
                'border-radius:50%;width:22px;height:22px;display:flex;'
                'align-items:center;justify-content:center;'
                'font-size:13px;font-weight:900;color:#fff;">⚡</div>'
            ),
            icon_size=(22, 22),
            icon_anchor=(11, 11),
        ),
    ).add_to(fg_charging)
fg_charging.add_to(m)

# Layer 5: Restaurants & Cafés
fg_food = folium.FeatureGroup(name="🍽️ Restaurants & Cafés", show=False)
food_cluster = MarkerCluster(options={"maxClusterRadius": 45, "disableClusteringAtZoom": 15})
for r in restaurant_pts:
    cuisine_str = f"<br>Cuisine: {r['cuisine']}" if r.get("cuisine") else ""
    folium.CircleMarker(
        location=[r["lat"], r["lon"]],
        radius=5,
        color="#E65100",
        fill=True,
        fill_color="#E65100",
        fill_opacity=0.8,
        popup=folium.Popup(
            f"<b>🍽️ {r['name'] or 'Restaurant'}</b>{cuisine_str}",
            max_width=200,
        ),
        tooltip=r["name"] or r.get("amenity", "restaurant").title(),
    ).add_to(food_cluster)
food_cluster.add_to(fg_food)
fg_food.add_to(m)

# Layer 6: Accident hotspots (clustered red markers)
if accident_pts:
    fg_accidents = folium.FeatureGroup(name="🚨 Accident Hotspots", show=False)
    acc_cluster = MarkerCluster(
        options={"maxClusterRadius": 35, "disableClusteringAtZoom": 15}
    )
    cat_label = {1: "Fatal", 2: "Serious injury", 3: "Minor injury"}
    for a in accident_pts:
        cat = cat_label.get(a["category"], "Accident")
        involved = []
        if a["rad"]:  involved.append("cyclist")
        if a["pkw"]:  involved.append("car")
        if a["fuss"]: involved.append("pedestrian")
        if a["krad"]: involved.append("motorcycle")
        inv_str = ", ".join(involved) if involved else "vehicle"
        folium.CircleMarker(
            location=[a["lat"], a["lon"]],
            radius=4,
            color="#C0392B",
            fill=True,
            fill_color="#C0392B",
            fill_opacity=0.75,
            popup=folium.Popup(
                f"<b>🚨 {cat}</b><br>Year: {a['year']}<br>Involved: {inv_str}",
                max_width=200,
            ),
            tooltip=f"Accident {a['year']} — {cat}",
        ).add_to(acc_cluster)
    acc_cluster.add_to(fg_accidents)
    fg_accidents.add_to(m)

    # Layer 6: Accident heatmap
    fg_heatmap = folium.FeatureGroup(name="🔥 Accident Heatmap", show=False)
    heat_data = [[a["lat"], a["lon"]] for a in accident_pts]
    HeatMap(
        heat_data,
        min_opacity=0.3,
        radius=14,
        blur=10,
        gradient={"0.4": "#ffd700", "0.65": "#ff8c00", "1": "#c0392b"},
    ).add_to(fg_heatmap)
    fg_heatmap.add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

components.html(m._repr_html_(), height=560, scrolling=False)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: STATS STRIP
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(section_header(t("navi.sec.infra"), color=NAV_ORANGE), unsafe_allow_html=True)

stat_cols = st.columns(4)

with stat_cols[0]:
    st.markdown(live_card(
        "🅿️", t("navi.card.parking"),
        str(len(parking_pts)) if parking_pts else "—",
        t("navi.card.parking.sub"),
        status_color="#1565C0",
    ), unsafe_allow_html=True)

with stat_cols[1]:
    st.markdown(live_card(
        "⚡", t("navi.card.charging"),
        str(len(charging_pts)) if charging_pts else "—",
        t("navi.card.charging.sub"),
        status_color="#F59E0B",
    ), unsafe_allow_html=True)

with stat_cols[2]:
    bus_count  = sum(1 for s in transit_pts if s["type"] == "bus")
    tram_count = sum(1 for s in transit_pts if s["type"] == "tram")
    st.markdown(live_card(
        "🚌", t("navi.card.transit"),
        str(len(transit_pts)) if transit_pts else "—",
        f"{bus_count} bus · {tram_count} tram",
        status_color="#009E3D",
    ), unsafe_allow_html=True)

with stat_cols[3]:
    if accident_pts:
        max_year = max(a["year"] for a in accident_pts)
        yr_count = sum(1 for a in accident_pts if a["year"] == max_year)
        st.markdown(live_card(
            "🚨", t("navi.card.accidents"),
            f"{yr_count:,}".replace(",", "."),
            f"Traffic incidents in {max_year}",
            status_color="#C0392B",
        ), unsafe_allow_html=True)
    else:
        st.markdown(live_card(
            "🚨", t("navi.card.accidents"), "—",
            "Unfallatlas data unavailable",
            status_color="#C0392B",
        ), unsafe_allow_html=True)

st.caption("Sources: OpenStreetMap / Overpass API (parking, charging, transit) · Unfallatlas (accidents)")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: LIVE DEPARTURES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(section_header(t("navi.sec.depart"), color=NAV_ORANGE), unsafe_allow_html=True)

mvb_stops = load_mvb_stops()
if mvb_stops:
    sel_col, hint_col = st.columns([4, 1])
    with sel_col:
        sel_idx = st.selectbox(
            "stop",
            options=range(len(mvb_stops)),
            format_func=lambda i: mvb_stops[i]["name"],
            index=None,
            placeholder="Choose a stop…",
            label_visibility="collapsed",
        )
    with hint_col:
        st.caption("🔄 updates every 60 s")

    if sel_idx is not None:
        selected_stop = mvb_stops[sel_idx]
        with st.spinner(f"Fetching departures from {selected_stop['name']}…"):
            deps = fetch_departures(selected_stop["ext_id"])

        if deps:
            rows_html = ""
            for d in deps:
                delay_min = d["delay_min"]
                cancelled = d["cancelled"]
                if cancelled:
                    row_bg    = "background:#FFF1F2;"
                    name_sty  = "text-decoration:line-through;color:#999;"
                    delay_html = '<span style="color:#C0392B;font-weight:700;">Cancelled</span>'
                else:
                    row_bg   = ""
                    name_sty = ""
                    if delay_min is None or delay_min <= 0:
                        delay_html = '<span style="color:#2E7D32;font-weight:700;">On time</span>'
                    elif delay_min <= 5:
                        delay_html = f'<span style="color:#E8650B;font-weight:700;">+{delay_min} min</span>'
                    else:
                        delay_html = f'<span style="color:#C0392B;font-weight:700;">+{delay_min} min</span>'

                rt_cell  = d["rt_time"] if d["rt_time"] and d["rt_time"] != d["time"] else "—"
                plat_cell = d["platform"] if d["platform"] else "—"
                rows_html += f"""
<tr style="{row_bg}border-bottom:1px solid #f1f5f9;">
  <td style="padding:8px 12px;font-weight:700;color:{NAV_ORANGE};white-space:nowrap;{name_sty}">{d['line']}</td>
  <td style="padding:8px 12px;color:#374151;max-width:220px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{d['direction']}</td>
  <td style="padding:8px 12px;font-family:monospace;color:#374151;">{d['time']}</td>
  <td style="padding:8px 12px;font-family:monospace;color:#374151;">{rt_cell}</td>
  <td style="padding:8px 12px;">{delay_html}</td>
  <td style="padding:8px 12px;color:#94a3b8;text-align:center;">{plat_cell}</td>
</tr>"""

            st.markdown(f"""
<div style="background:#fff;border-radius:12px;overflow:hidden;
            box-shadow:0 2px 12px rgba(0,0,0,0.06);margin-bottom:8px;">
  <table style="width:100%;border-collapse:collapse;font-size:0.88rem;">
    <thead>
      <tr style="background:#f8fafc;border-bottom:2px solid #e2e8f0;">
        <th style="padding:10px 12px;text-align:left;font-size:0.68rem;text-transform:uppercase;
                   letter-spacing:0.1em;color:#64748b;font-weight:800;">Line</th>
        <th style="padding:10px 12px;text-align:left;font-size:0.68rem;text-transform:uppercase;
                   letter-spacing:0.1em;color:#64748b;font-weight:800;">Direction</th>
        <th style="padding:10px 12px;text-align:left;font-size:0.68rem;text-transform:uppercase;
                   letter-spacing:0.1em;color:#64748b;font-weight:800;">Scheduled</th>
        <th style="padding:10px 12px;text-align:left;font-size:0.68rem;text-transform:uppercase;
                   letter-spacing:0.1em;color:#64748b;font-weight:800;">Real-time</th>
        <th style="padding:10px 12px;text-align:left;font-size:0.68rem;text-transform:uppercase;
                   letter-spacing:0.1em;color:#64748b;font-weight:800;">Delay</th>
        <th style="padding:10px 12px;text-align:center;font-size:0.68rem;text-transform:uppercase;
                   letter-spacing:0.1em;color:#64748b;font-weight:800;">Track</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>
""", unsafe_allow_html=True)
            st.caption(
                f"Departures from {selected_stop['name']} · "
                "Real-time data via NASA HAFAS REST API · refreshes every 60 s"
            )
        else:
            st.info(
                "No departure data available for this stop. "
                "The stop may not have live departures or the HAFAS service is currently unavailable."
            )
    else:
        st.markdown(
            '<div style="color:#94a3b8;font-size:0.88rem;padding:12px 0;">'
            'Select a stop above to view live departures.</div>',
            unsafe_allow_html=True,
        )
else:
    st.info("Stop list unavailable — could not load MVB GTFS data.")
