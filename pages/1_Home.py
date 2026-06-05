import streamlit as st
import streamlit.components.v1 as components
import folium
import pandas as pd
from datetime import date, timedelta

from utils.live_api import (
    fetch_weather, fetch_elbe_level, fetch_air_quality,
    fetch_weather_forecast, fetch_city_news,
)
from utils.data_loader import load_kiss
from utils.ui_helpers import section_header, live_card, topic_card

# ── Helpers ───────────────────────────────────────────────────────────────────

COND_ICON = {
    "dry": "☀️", "rain": "🌧️", "snow": "❄️", "sleet": "🌨️",
    "hail": "⛈️", "thunderstorm": "⛈️", "fog": "🌫️",
    "wind": "💨", "cloudy": "⛅", "partly-cloudy": "🌤️",
}

def cond_icon(cond: str) -> str:
    cond = (cond or "dry").lower()
    for key in COND_ICON:
        if key in cond:
            return COND_ICON[key]
    return "🌤️"

def day_label(date_str: str) -> str:
    try:
        d = date.fromisoformat(date_str[:10])
        if d == date.today():
            return "Today"
        if d == date.today() + timedelta(days=1):
            return "Tomorrow"
        return d.strftime("%A")
    except Exception:
        return date_str[:10]

# ── Fetch live data (cached) ──────────────────────────────────────────────────
weather    = fetch_weather()
elbe       = fetch_elbe_level()
pm25       = fetch_air_quality()
forecast   = fetch_weather_forecast()
news_items = fetch_city_news()

temp     = weather.get("temperature")        if weather else None
wind_spd = weather.get("wind_speed")         if weather else None
cond     = weather.get("condition")          if weather else None
humidity = weather.get("relative_humidity")  if weather else None
elbe_val = elbe.get("value")                 if elbe    else None

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:28px 0 6px 0;">
  <div style="font-size:2rem;font-weight:900;color:#1A1A1A;line-height:1.1;">
    Good day, Magdeburg 👋
  </div>
  <div style="font-size:1rem;color:#64748b;margin-top:6px;">
    Your city at a glance — live conditions, news, events, and city services.
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: ACTIVE ALERTS
# ─────────────────────────────────────────────────────────────────────────────
alerts = []
if elbe_val is not None and elbe_val > 400:
    alerts.append(("🚨 Flood Advisory",
                   f"Elbe river is at **{elbe_val:.0f} cm** — above the advisory threshold of 400 cm. "
                   "Avoid the riverside promenades. Monitor PEGELONLINE for updates.", "error"))
elif elbe_val is not None and elbe_val > 300:
    alerts.append(("⚠️ Elbe Watch",
                   f"Elbe is at **{elbe_val:.0f} cm** and rising. No immediate risk — keep an eye on the level.",
                   "warning"))

if pm25 is not None and pm25 > 35:
    alerts.append(("😷 Air Quality Warning",
                   f"PM2.5 is **{pm25:.1f} µg/m³** — above the WHO guideline of 35 µg/m³. "
                   "Sensitive groups should limit outdoor activity.", "warning"))

if wind_spd is not None and wind_spd > 60:
    alerts.append(("💨 Strong Wind Alert",
                   f"Wind speeds of **{wind_spd:.0f} km/h** recorded. "
                   "Cyclists and pedestrians should take care on exposed routes.", "warning"))

if alerts:
    for level_label, msg, alert_type in alerts:
        if alert_type == "error":
            st.error(f"**{level_label}** — {msg}")
        else:
            st.warning(f"**{level_label}** — {msg}")
else:
    st.success("✅ **All Clear** — No active alerts for Magdeburg right now. Conditions are normal.")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 + 3: WEATHER + LIVE PULSE (side by side)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(section_header("Weather & Live Conditions"), unsafe_allow_html=True)

weather_col, pulse_col = st.columns([3, 2], gap="large")

with weather_col:
    temp_str  = f"{temp:.0f}°C"         if temp      is not None else "—"
    wind_str  = f"{wind_spd:.0f} km/h"  if wind_spd  is not None else "—"
    hum_str   = f"{humidity:.0f}%"       if humidity  is not None else "—"
    icon_main = cond_icon(cond)
    cond_str  = (cond or "").replace("-", " ").title() if cond else "—"

    st.markdown(f"""
<div style="background:linear-gradient(135deg,#0f4c75 0%,#1b6ca8 60%,#1e8bc3 100%);
            border-radius:20px;padding:28px 32px;color:#fff;">
  <div style="font-size:0.72rem;font-weight:700;text-transform:uppercase;
              letter-spacing:0.14em;opacity:0.7;margin-bottom:6px;">Magdeburg, today</div>
  <div style="display:flex;align-items:center;gap:16px;">
    <div style="font-size:4rem;line-height:1;">{icon_main}</div>
    <div>
      <div style="font-size:3.2rem;font-weight:900;line-height:1;">{temp_str}</div>
      <div style="font-size:1rem;opacity:0.85;margin-top:4px;">{cond_str}</div>
    </div>
  </div>
  <div style="display:flex;gap:28px;margin-top:20px;font-size:0.88rem;opacity:0.85;">
    <span>💨 Wind &nbsp;<strong>{wind_str}</strong></span>
    <span>💧 Humidity &nbsp;<strong>{hum_str}</strong></span>
  </div>
</div>
""", unsafe_allow_html=True)

    if forecast:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        fc_cols = st.columns(min(len(forecast), 4))
        for i, fc in enumerate(forecast[:4]):
            with fc_cols[i]:
                hi  = f"{fc['temp_max']:.0f}°" if fc.get("temp_max") is not None else "—"
                lo  = f"{fc['temp_min']:.0f}°" if fc.get("temp_min") is not None else "—"
                ico = cond_icon(fc.get("condition"))
                lbl = day_label(fc["date"])
                st.markdown(f"""
<div style="background:#f8fafc;border-radius:12px;padding:12px 8px;text-align:center;">
  <div style="font-size:0.68rem;font-weight:700;color:#64748b;text-transform:uppercase;
              letter-spacing:0.08em;">{lbl}</div>
  <div style="font-size:1.6rem;margin:6px 0;">{ico}</div>
  <div style="font-size:0.9rem;font-weight:800;color:#1A1A1A;">{hi}</div>
  <div style="font-size:0.78rem;color:#94a3b8;">{lo}</div>
</div>
""", unsafe_allow_html=True)

    st.caption("Source: Bright Sky / DWD · Updated every 10 min")

with pulse_col:
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    temp_color = ("#C0392B" if temp is not None and temp < 0
                  else "#E65100" if temp is not None and temp < 5
                  else "#007A6E")
    st.markdown(live_card(
        "🌡️", "Temperature",
        f"{temp:.1f} °C" if temp is not None else "—",
        "Current outdoor temperature",
        status_color=temp_color,
    ), unsafe_allow_html=True)

    wind_color = ("#C0392B" if wind_spd is not None and wind_spd > 60
                  else "#F59E0B" if wind_spd is not None and wind_spd > 40
                  else "#007A6E")
    st.markdown(live_card(
        "💨", "Wind Speed",
        f"{wind_spd:.0f} km/h" if wind_spd is not None else "—",
        "Alert threshold: 60 km/h",
        status_color=wind_color,
    ), unsafe_allow_html=True)

    elbe_color = ("#C0392B" if elbe_val is not None and elbe_val > 400
                  else "#F59E0B" if elbe_val is not None and elbe_val > 300
                  else "#007A6E")
    st.markdown(live_card(
        "🌊", "Elbe Water Level",
        f"{elbe_val:.0f} cm" if elbe_val is not None else "—",
        "Advisory threshold: 400 cm",
        status_color=elbe_color,
    ), unsafe_allow_html=True)

    pm_color = ("#C0392B" if pm25 is not None and pm25 > 35
                else "#F59E0B" if pm25 is not None and pm25 > 25
                else "#007A6E")
    st.markdown(live_card(
        "🫁", "PM2.5 Air Quality",
        f"{pm25:.1f} µg/m³" if pm25 is not None else "—",
        "WHO guideline: 35 µg/m³",
        status_color=pm_color,
    ), unsafe_allow_html=True)

    st.caption("Sources: Bright Sky · PEGELONLINE · Sensor.Community")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: TODAY'S TIPS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(section_header("Today's Recommendations"), unsafe_allow_html=True)

tips = []
if cond and any(k in cond.lower() for k in ["rain", "sleet", "hail"]):
    tips.append("🌧️ Rain expected — take an umbrella or use the MVB tram/bus network to stay dry.")
elif cond and "snow" in cond.lower():
    tips.append("❄️ Snowy conditions — allow extra travel time and check MVB for service disruptions.")
elif cond and "fog" in cond.lower():
    tips.append("🌫️ Foggy morning — drive with low beam headlights and reduce speed on the Elbe bridge.")
elif temp is not None and temp > 25:
    tips.append("☀️ Warm day ahead — the Elbauenpark and Biederitzer Busch are perfect for a walk or picnic.")
elif temp is not None and temp < 0:
    tips.append("🧥 Freezing temperatures — dress in layers and check gritting status before cycling.")
else:
    tips.append("🌤️ Good conditions — explore the Altstadt or cycle along the Elbe cycle path.")

if elbe_val is not None and elbe_val > 300:
    tips.append("🚧 Elbe level is elevated — the riverside promenade near Strombrücke may be partially flooded.")
else:
    tips.append("🚴 The Elbe cycle path is in good condition today — a scenic ride to Schönebeck is possible.")

if pm25 is not None and pm25 > 25:
    tips.append("😷 Air quality is moderate — people with respiratory conditions should limit strenuous outdoor exercise.")
else:
    tips.append("🌿 Air quality is good today — a great day to open windows or exercise outdoors in the parks.")

tips.append("📅 Check the events calendar below for upcoming activities in Magdeburg this month.")

tips_html = "".join(f'<li style="margin-bottom:8px;">{t}</li>' for t in tips)
st.markdown(f"""
<div style="background:#fffbeb;border-left:4px solid #F59E0B;border-radius:0 14px 14px 0;
            padding:18px 24px;margin-bottom:8px;">
  <div style="font-size:0.72rem;font-weight:800;color:#92400E;text-transform:uppercase;
              letter-spacing:0.12em;margin-bottom:10px;">💡 City Tips for Today</div>
  <ul style="margin:0;padding-left:18px;font-size:0.9rem;color:#374151;line-height:1.6;">
    {tips_html}
  </ul>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5: CITY NEWS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(section_header("City News & Updates"), unsafe_allow_html=True)

if news_items:
    news_cols = st.columns(2)
    for i, item in enumerate(news_items[:4]):
        with news_cols[i % 2]:
            link_html = (
                f'<a href="{item["link"]}" target="_blank" rel="noopener" '
                f'style="color:#1565C0;text-decoration:none;font-weight:700;'
                f'font-size:0.88rem;">{item["title"]}</a>'
            ) if item.get("link") else (
                f'<span style="font-weight:700;font-size:0.88rem;color:#1A1A1A;">{item["title"]}</span>'
            )
            summary_html = (
                f'<div style="font-size:0.78rem;color:#64748b;margin-top:4px;">{item["summary"]}</div>'
            ) if item.get("summary") else ""
            date_html = (
                f'<div style="font-size:0.68rem;color:#94a3b8;margin-top:6px;">{item["date"]}</div>'
            ) if item.get("date") else ""
            st.markdown(f"""
<div style="background:#fff;border-radius:12px;padding:16px 18px;
            box-shadow:0 2px 10px rgba(0,0,0,0.06);margin-bottom:10px;
            border-left:3px solid #1565C0;">
  {link_html}
  {summary_html}
  {date_html}
</div>
""", unsafe_allow_html=True)
    st.caption("Source: Landeshauptstadt Magdeburg — City Press Office RSS feed")

else:
    # Data-driven fallback
    fallback_items = []
    try:
        df_e = load_kiss("gesundheit-und-soziales/rettungsdienst-einsaetze.json")
        df_e = df_e.rename(columns={"Rettungsdienst-Einsätze gesamt": "Total"})
        ly = int(df_e["Jahr"].max())
        total = int(df_e[df_e["Jahr"] == ly]["Total"].sum())
        fallback_items.append({
            "icon": "🚑",
            "title": f"Emergency Services: {total:,} Callouts in {ly}".replace(",", "."),
            "body": (f"Magdeburg's rescue services responded to {total:,} emergencies in {ly} — "
                     f"roughly {total // 365:,} per day. Demand has grown steadily since 1991.").replace(",", "."),
        })
    except Exception:
        pass
    try:
        df_s = load_kiss("bildung-und-kultur/anzahl-der-studierenden-im-wintersemester.json")
        df_s = df_s.rename(columns={"var4": "Students"})
        df_s = df_s[df_s["Students"].notna()]
        ly = int(df_s["Jahr"].max())
        total = int(df_s[df_s["Jahr"] == ly]["Students"].sum())
        fallback_items.append({
            "icon": "🎓",
            "title": f"University City: {total:,} Students in {ly}/{ly+1}".replace(",", "."),
            "body": ("Otto-von-Guericke-Universität and Hochschule Magdeburg-Stendal together "
                     "make Magdeburg one of Saxony-Anhalt's most important academic locations."),
        })
    except Exception:
        pass
    try:
        df_bev = load_kiss("bevoelkerung/einwohnerinnen-und-einwohner.json")
        df_bev = df_bev.rename(columns={"var2": "Population"})
        df_bev = df_bev[df_bev["Population"].notna()].sort_values("Jahr")
        ly = int(df_bev["Jahr"].max())
        pop = int(df_bev[df_bev["Jahr"] == ly]["Population"].iloc[-1])
        fallback_items.append({
            "icon": "🏙️",
            "title": f"Magdeburg: {pop:,} Residents ({ly})".replace(",", "."),
            "body": ("Magdeburg is Saxony-Anhalt's capital and largest city, with a growing "
                     "population after years of post-reunification decline."),
        })
    except Exception:
        pass

    fallback_items.append({
        "icon": "📊",
        "title": "Transparency & Open Data",
        "body": ("All data in this dashboard is sourced from Magdeburg's open data portal "
                 "(KISS-MD) and public APIs. Explore the topic pages for detailed breakdowns."),
    })

    news_cols = st.columns(2)
    for i, item in enumerate(fallback_items[:4]):
        with news_cols[i % 2]:
            st.markdown(f"""
<div style="background:#fff;border-radius:12px;padding:16px 18px;
            box-shadow:0 2px 10px rgba(0,0,0,0.06);margin-bottom:10px;
            border-left:3px solid #007A6E;">
  <div style="font-size:1.3rem;margin-bottom:6px;">{item["icon"]}</div>
  <div style="font-weight:700;font-size:0.88rem;color:#1A1A1A;margin-bottom:6px;">{item["title"]}</div>
  <div style="font-size:0.78rem;color:#64748b;line-height:1.5;">{item["body"]}</div>
</div>
""", unsafe_allow_html=True)
    st.caption("Source: KISS-MD / Landeshauptstadt Magdeburg open data (live RSS unavailable)")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6: CITY AT A GLANCE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(section_header("City at a Glance"), unsafe_allow_html=True)
st.caption("Latest headline figures from each topic — click a tile to explore in depth.")

TOPIC_COLORS = {
    "climate":    "#00897B",
    "population": "#1565C0",
    "mobility":   "#6A1B9A",
    "economy":    "#2E7D32",
    "health":     "#C0392B",
}

glance_cols = st.columns(5)

with glance_cols[0]:
    try:
        df_c = load_kiss("klima/jaehrliche-temperaturen-magdeburg.json")
        df_c["var2"] = pd.to_numeric(df_c.get("var2", df_c.iloc[:, 1]), errors="coerce")
        df_c = df_c[df_c["var2"].notna()]
        ly = int(df_c["Jahr"].max()); py = ly - 1
        t_ly = float(df_c[df_c["Jahr"] == ly]["var2"].iloc[0])
        t_py = float(df_c[df_c["Jahr"] == py]["var2"].iloc[0])
        diff = t_ly - t_py
        card_html = topic_card("🌡️", "Climate", f"{t_ly:.1f}", "°C avg",
                               f"{abs(diff):.1f}°C vs {py}", diff >= 0,
                               str(ly), color=TOPIC_COLORS["climate"])
    except Exception:
        card_html = topic_card("🌡️", "Climate", "—", "°C avg", "no data", True,
                               "—", color=TOPIC_COLORS["climate"])
    st.markdown(f'<a href="/climate" style="text-decoration:none;">{card_html}</a>',
                unsafe_allow_html=True)

with glance_cols[1]:
    try:
        df_p = load_kiss("bevoelkerung/einwohnerinnen-und-einwohner.json")
        df_p = df_p.rename(columns={"var2": "Pop"})
        df_p = df_p[df_p["Pop"].notna()].sort_values("Jahr")
        ly = int(df_p["Jahr"].max()); py = ly - 1
        p_ly = int(df_p[df_p["Jahr"] == ly]["Pop"].iloc[-1])
        p_py = int(df_p[df_p["Jahr"] == py]["Pop"].iloc[-1]) if py in df_p["Jahr"].values else p_ly
        diff = p_ly - p_py
        card_html = topic_card("🏘️", "Population", f"{p_ly/1000:.0f}k", "residents",
                               f"{abs(diff):,} vs {py}".replace(",", "."), diff >= 0,
                               str(ly), color=TOPIC_COLORS["population"])
    except Exception:
        card_html = topic_card("🏘️", "Population", "—", "residents", "no data", True,
                               "—", color=TOPIC_COLORS["population"])
    st.markdown(f'<a href="/population" style="text-decoration:none;">{card_html}</a>',
                unsafe_allow_html=True)

with glance_cols[2]:
    try:
        df_m = load_kiss("verkehr/kraftfahrzeuge.json")
        num_cols = [c for c in df_m.columns if pd.to_numeric(df_m[c], errors="coerce").notna().sum() > 5]
        val_col = num_cols[0] if num_cols else df_m.columns[1]
        df_m["_v"] = pd.to_numeric(df_m[val_col], errors="coerce")
        df_m = df_m[df_m["_v"].notna()].sort_values("Jahr")
        ly = int(df_m["Jahr"].max()); py = ly - 1
        v_ly = int(df_m[df_m["Jahr"] == ly]["_v"].iloc[-1])
        v_py = int(df_m[df_m["Jahr"] == py]["_v"].iloc[-1]) if py in df_m["Jahr"].values else v_ly
        diff = v_ly - v_py
        card_html = topic_card("🚌", "Mobility", f"{v_ly/1000:.0f}k", "vehicles",
                               f"{abs(diff):,} vs {py}".replace(",", "."), diff >= 0,
                               str(ly), color=TOPIC_COLORS["mobility"])
    except Exception:
        card_html = topic_card("🚌", "Mobility", "—", "vehicles", "no data", True,
                               "—", color=TOPIC_COLORS["mobility"])
    st.markdown(f'<a href="/mobility" style="text-decoration:none;">{card_html}</a>',
                unsafe_allow_html=True)

with glance_cols[3]:
    try:
        df_eco = load_kiss("wirtschaft/steuereinnahmen.json")
        eco_num = [c for c in df_eco.columns
                   if pd.to_numeric(df_eco[c], errors="coerce").notna().sum() > 5]
        val_col = eco_num[0] if eco_num else df_eco.columns[1]
        df_eco["_t"] = pd.to_numeric(df_eco[val_col], errors="coerce")
        df_eco = df_eco[df_eco["_t"].notna()].sort_values("Jahr")
        ly = int(df_eco["Jahr"].max()); py = ly - 1
        t_ly = float(df_eco[df_eco["Jahr"] == ly]["_t"].iloc[-1])
        t_py = float(df_eco[df_eco["Jahr"] == py]["_t"].iloc[-1]) if py in df_eco["Jahr"].values else t_ly
        diff_pct = (t_ly - t_py) / t_py * 100 if t_py else 0
        card_html = topic_card("💶", "Economy", f"€{t_ly/1e6:.0f}M", "tax revenue",
                               f"{abs(diff_pct):.1f}% vs {py}", diff_pct >= 0,
                               str(ly), color=TOPIC_COLORS["economy"])
    except Exception:
        card_html = topic_card("💶", "Economy", "—", "tax revenue", "no data", True,
                               "—", color=TOPIC_COLORS["economy"])
    st.markdown(f'<a href="/economy" style="text-decoration:none;">{card_html}</a>',
                unsafe_allow_html=True)

with glance_cols[4]:
    try:
        df_h = load_kiss("gesundheit-und-soziales/rettungsdienst-einsaetze.json")
        df_h = df_h.rename(columns={"Rettungsdienst-Einsätze gesamt": "Total"})
        ly = int(df_h["Jahr"].max()); py = ly - 1
        h_ly = int(df_h[df_h["Jahr"] == ly]["Total"].sum())
        h_py = int(df_h[df_h["Jahr"] == py]["Total"].sum())
        diff_pct = (h_ly - h_py) / h_py * 100 if h_py else 0
        card_html = topic_card("🏥", "Health", f"{h_ly/1000:.0f}k", "emergency ops",
                               f"{abs(diff_pct):.1f}% vs {py}", False,
                               str(ly), color=TOPIC_COLORS["health"])
    except Exception:
        card_html = topic_card("🏥", "Health", "—", "emergency ops", "no data", True,
                               "—", color=TOPIC_COLORS["health"])
    st.markdown(f'<a href="/health" style="text-decoration:none;">{card_html}</a>',
                unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7: EVENTS CALENDAR
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(section_header("Upcoming Events in Magdeburg"), unsafe_allow_html=True)

today_date = date.today()

def next_occurrence(month: int, day: int) -> date:
    try:
        candidate = date(today_date.year, month, day)
    except ValueError:
        candidate = date(today_date.year, month, 28)
    if candidate < today_date:
        try:
            candidate = date(today_date.year + 1, month, day)
        except ValueError:
            candidate = date(today_date.year + 1, month, 28)
    return candidate

def next_first_monday() -> date:
    d = today_date.replace(day=1)
    while True:
        first_monday = d + timedelta(days=(7 - d.weekday()) % 7)
        if first_monday >= today_date:
            return first_monday
        d = (d + timedelta(days=32)).replace(day=1)

EVENTS = [
    {"name": "Stadtfest Magdeburg",       "icon": "🎉", "month": 6,    "day": 14,
     "desc": "City festival — music, food, and culture at the Elbe riverside."},
    {"name": "Magdeburg Marathon",         "icon": "🏃", "month": 4,    "day": 20,
     "desc": "Annual city marathon through Magdeburg's historic districts."},
    {"name": "Kulturnacht",                "icon": "🎭", "month": 10,   "day": 12,
     "desc": "One night, dozens of venues — museums, galleries, theatres open until midnight."},
    {"name": "Altstadtfest",              "icon": "🏰", "month": 8,    "day": 23,
     "desc": "Medieval old-town festival at the Dom and Hundertwasserhaus."},
    {"name": "Weihnachtsmarkt",            "icon": "🎄", "month": 11,   "day": 24,
     "desc": "Magdeburg Christmas market at the Cathedral square — one of Germany's oldest."},
    {"name": "City Council Open Session", "icon": "🏛️", "month": None, "day": None,
     "desc": "Stadtrat public meeting — citizens can attend and observe."},
]

upcoming = []
for ev in EVENTS:
    ev_date = next_first_monday() if ev["month"] is None else next_occurrence(ev["month"], ev["day"])
    upcoming.append({**ev, "date": ev_date})

upcoming.sort(key=lambda x: x["date"])
upcoming = upcoming[:4]

ev_cols = st.columns(len(upcoming))
for i, ev in enumerate(upcoming):
    with ev_cols[i]:
        days_away = (ev["date"] - today_date).days
        if days_away == 0:
            badge, badge_color = "Today!", "#C0392B"
        elif days_away <= 7:
            badge, badge_color = f"In {days_away} days", "#E65100"
        elif days_away <= 30:
            badge, badge_color = f"In {days_away} days", "#F59E0B"
        else:
            badge, badge_color = ev["date"].strftime("%d %b %Y"), "#64748b"

        st.markdown(f"""
<div style="background:#fff;border-radius:14px;padding:18px 16px;
            box-shadow:0 2px 12px rgba(0,0,0,0.07);">
  <div style="font-size:1.8rem;margin-bottom:8px;">{ev["icon"]}</div>
  <div style="font-size:0.82rem;font-weight:800;color:#1A1A1A;margin-bottom:6px;
              line-height:1.3;">{ev["name"]}</div>
  <div style="display:inline-block;background:{badge_color}18;color:{badge_color};
              border-radius:8px;padding:2px 10px;font-size:0.72rem;
              font-weight:700;margin-bottom:8px;">{badge}</div>
  <div style="font-size:0.76rem;color:#64748b;line-height:1.5;">{ev["desc"]}</div>
</div>
""", unsafe_allow_html=True)

st.caption("Source: Landeshauptstadt Magdeburg — Events calendar (magdeburg.de/veranstaltungen)")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8: CITY MAP
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(section_header("Explore Magdeburg"), unsafe_allow_html=True)

landmarks = [
    (52.1316, 11.6397, "Dom", "🏛️ Magdeburg Cathedral — 13th century Gothic landmark."),
    (52.1275, 11.6361, "Rathaus", "🏛️ City Hall — administrative centre of Magdeburg."),
    (52.1229, 11.6457, "Hundertwasserhaus", "🏠 Colourful apartment building by Friedensreich Hundertwasser."),
    (52.1361, 11.6272, "Elbauenpark", "🎡 Large riverside park — Stadtfest and outdoor events."),
    (52.1302, 11.6267, "Magdeburg Hbf", "🚂 Main train station — regional and ICE connections."),
    (52.1393, 11.6470, "OVGU Campus", "🎓 Otto-von-Guericke-Universität — largest university."),
    (52.1219, 11.6306, "Elbe Promenade", "🌊 Scenic riverside walk along the Elbe."),
]

m = folium.Map(location=[52.131, 11.640], zoom_start=13, tiles="CartoDB positron")
for lat, lon, name, tooltip in landmarks:
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(f"<b>{name}</b><br><small>{tooltip}</small>", max_width=240),
        tooltip=tooltip,
        icon=folium.Icon(color="blue", icon="info-sign"),
    ).add_to(m)

map_html = m._repr_html_()
components.html(map_html, height=440, scrolling=False)
st.caption("Source: OpenStreetMap / CartoDB · Click markers for details")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 9: CITY CONTACTS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(section_header("City Services & Contacts"), unsafe_allow_html=True)

contacts = [
    {"icon": "🚒", "name": "Emergency (Fire / Ambulance)", "number": "112",
     "detail": "European emergency number — free from any phone.", "color": "#C0392B"},
    {"icon": "👮", "name": "Police Emergency", "number": "110",
     "detail": "German police emergency number.", "color": "#1565C0"},
    {"icon": "🏛️", "name": "City Hall (Rathaus)", "number": "+49 391 540-0",
     "detail": "General enquiries · Mon–Fri 08:00–18:00", "color": "#007A6E"},
    {"icon": "🚌", "name": "MVB Public Transport", "number": "+49 391 886-0",
     "detail": "Tram & bus info, journey planner: mvbnet.de", "color": "#6A1B9A"},
    {"icon": "💡", "name": "Stadtwerke Magdeburg", "number": "+49 391 587-0",
     "detail": "Gas, electricity, heating and water services.", "color": "#F59E0B"},
    {"icon": "ℹ️", "name": "Tourist Information", "number": "+49 391 8380-430",
     "detail": "Am Alten Markt 9 · tourismusmagdeburg.de", "color": "#2E7D32"},
]

contact_cols = st.columns(3)
for i, c in enumerate(contacts):
    with contact_cols[i % 3]:
        st.markdown(f"""
<div style="background:#fff;border-radius:12px;padding:16px 18px;
            box-shadow:0 2px 10px rgba(0,0,0,0.06);margin-bottom:12px;
            border-left:4px solid {c['color']};">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
    <span style="font-size:1.4rem;">{c["icon"]}</span>
    <span style="font-size:0.78rem;font-weight:700;color:#374151;">{c["name"]}</span>
  </div>
  <div style="font-size:1.15rem;font-weight:900;color:{c['color']};margin-bottom:4px;">{c["number"]}</div>
  <div style="font-size:0.74rem;color:#94a3b8;">{c["detail"]}</div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    "<div style='height:20px'></div>"
    "<div style='font-size:0.72rem;color:#94a3b8;text-align:center;padding-bottom:16px;'>"
    "Smart City Magdeburg Dashboard · Data sources: KISS-MD, Bright Sky/DWD, "
    "PEGELONLINE, Sensor.Community, OpenStreetMap"
    "</div>",
    unsafe_allow_html=True,
)
