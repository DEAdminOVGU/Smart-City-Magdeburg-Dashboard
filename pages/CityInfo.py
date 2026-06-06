import base64
import os
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta

from utils.data_loader import load_kiss
from utils.constants import MD_TEAL, MD_ORANGE, PLOTLY_TEMPLATE
from utils.ui_helpers import section_header, insight_box, live_card

CITY_PURPLE = "#6D28D9"

# ── Icon helpers ──────────────────────────────────────────────────────────────
def _b64_img(rel_path: str, size: str = "1.6rem") -> str:
    _p = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", rel_path))
    try:
        with open(_p, "rb") as _f:
            _b = base64.b64encode(_f.read()).decode()
        ext  = os.path.splitext(_p)[1].lstrip(".")
        mime = "image/gif" if ext == "gif" else f"image/{ext}"
        return f"<img src='data:{mime};base64,{_b}' style='width:{size};height:{size};object-fit:contain;vertical-align:middle;'>"
    except Exception:
        return ""

_FIRE    = _b64_img("utils/icons/fire-brigade.png")
_POLICE  = _b64_img("utils/icons/policeman.png")
_BUS     = _b64_img("utils/icons/bus.png")
_BLDG    = _b64_img("utils/icons/historic-building.png")
_FACTORY = _b64_img("utils/icons/factory.gif", "2.2rem")

# ── Event helpers (moved from 1_Home.py) ─────────────────────────────────────
_today = date.today()

def next_occurrence(month: int, day: int) -> date:
    try:
        candidate = date(_today.year, month, day)
    except ValueError:
        candidate = date(_today.year, month, 28)
    if candidate < _today:
        try:
            candidate = date(_today.year + 1, month, day)
        except ValueError:
            candidate = date(_today.year + 1, month, 28)
    return candidate

def next_first_monday() -> date:
    d = _today.replace(day=1)
    while True:
        first_monday = d + timedelta(days=(7 - d.weekday()) % 7)
        if first_monday >= _today:
            return first_monday
        d = (d + timedelta(days=32)).replace(day=1)

# ── Page header ───────────────────────────────────────────────────────────────
st.title("City & Culture")
st.markdown(
    "<p style='font-size:0.97rem;color:#64748b;max-width:700px;margin:-6px 0 20px 0;'>"
    "Everything you need as a citizen or visitor — upcoming events, city attractions, "
    "cultural venues, and essential service contacts."
    "</p>",
    unsafe_allow_html=True,
)
st.caption("Sources: KISS-MD / Statistisches Amt Magdeburg · Landeshauptstadt Magdeburg")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: EVENTS CALENDAR
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(section_header("Events Calendar — Magdeburg", color=CITY_PURPLE), unsafe_allow_html=True)

EVENTS = [
    {"name": "Stadtfest Magdeburg",      "icon": "🎉", "month": 6,    "day": 14,
     "desc": "City festival — music, food, and culture at the Elbe riverside."},
    {"name": "Magdeburg Marathon",        "icon": "🏃", "month": 4,    "day": 20,
     "desc": "Annual city marathon through Magdeburg's historic districts."},
    {"name": "Kulturnacht",               "icon": "🎭", "month": 10,   "day": 12,
     "desc": "One night, dozens of venues — museums, galleries, theatres open until midnight."},
    {"name": "Altstadtfest",             "icon": "🏰", "month": 8,    "day": 23,
     "desc": "Medieval old-town festival at the Dom and Hundertwasserhaus."},
    {"name": "Weihnachtsmarkt",           "icon": "🎄", "month": 11,   "day": 24,
     "desc": "Magdeburg Christmas market at the Cathedral square — one of Germany's oldest."},
    {"name": "City Council Open Session", "icon": "🏛️", "month": None, "day": None,
     "desc": "Stadtrat public meeting — citizens can attend and observe."},
]

upcoming = []
for ev in EVENTS:
    ev_date = next_first_monday() if ev["month"] is None else next_occurrence(ev["month"], ev["day"])
    upcoming.append({**ev, "date": ev_date})
upcoming.sort(key=lambda x: x["date"])

ev_cols = st.columns(min(len(upcoming), 4))
for i, ev in enumerate(upcoming[:4]):
    with ev_cols[i]:
        days_away = (ev["date"] - _today).days
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
# SECTION 2: KEY ATTRACTIONS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(section_header("Key Attractions", color=CITY_PURPLE), unsafe_allow_html=True)

ATTRACTIONS = [
    {
        "icon": "🕌",
        "name": "Magdeburger Dom",
        "desc": "Germany's first Gothic cathedral (1209 AD), burial site of Emperor Otto I. "
                "Tallest church in Saxony-Anhalt at 104 m.",
        "badge": "History",
        "badge_color": "#7C3AED",
    },
    {
        "icon": "🟢",
        "name": "Grüne Zitadelle",
        "desc": "Hundertwasser's final major work (2005) — a curved, golden-tipped residential "
                "and cultural complex with rooftop gardens.",
        "badge": "Architecture",
        "badge_color": "#059669",
    },
    {
        "icon": "🏛️",
        "name": "Kunstmuseum Kloster Unser Lieben Frauen",
        "desc": "Magdeburg's oldest surviving building (11th century Romanesque monastery), "
                "now a fine arts museum with sculpture and contemporary exhibitions.",
        "badge": "Art & Museum",
        "badge_color": "#D97706",
    },
    {
        "icon": _FACTORY,
        "name": "Technikmuseum Magdeburg",
        "desc": "Industrial and technical heritage — steam engines, historic vehicles, "
                "and machinery in a former factory building.",
        "badge": "Museum",
        "badge_color": "#64748b",
    },
    {
        "icon": "🌿",
        "name": "Gruson-Gewächshäuser",
        "desc": "Victorian tropical greenhouse complex (1896) with palms, cacti, and "
                "exotic plants from five climate zones. A botanical garden in the city.",
        "badge": "Nature",
        "badge_color": "#16A34A",
    },
    {
        "icon": "🌊",
        "name": "Elbe Promenade & Hubbrücke",
        "desc": "Scenic riverside walk along the Elbe with cycling paths. "
                "The historic Hubbrücke swing bridge and Elbauenpark are nearby.",
        "badge": "Outdoors",
        "badge_color": "#0891B2",
    },
]

attr_row1 = st.columns(3)
attr_row2 = st.columns(3)
rows = [attr_row1, attr_row2]

for idx, attr in enumerate(ATTRACTIONS):
    row_i   = idx // 3
    col_i   = idx % 3
    with rows[row_i][col_i]:
        st.markdown(f"""
<div style="background:#fff;border-radius:14px;padding:20px 18px;
            box-shadow:0 2px 14px rgba(0,0,0,0.07);margin-bottom:16px;
            border-top:4px solid {attr['badge_color']};">
  <div style="font-size:2rem;margin-bottom:10px;">{attr["icon"]}</div>
  <div style="display:inline-block;background:{attr['badge_color']}18;color:{attr['badge_color']};
              border-radius:8px;padding:2px 10px;font-size:0.68rem;
              font-weight:700;margin-bottom:8px;">{attr["badge"]}</div>
  <div style="font-size:0.88rem;font-weight:800;color:#1A1A1A;margin-bottom:6px;
              line-height:1.3;">{attr["name"]}</div>
  <div style="font-size:0.78rem;color:#64748b;line-height:1.55;">{attr["desc"]}</div>
</div>
""", unsafe_allow_html=True)

st.caption("Visitor tips: most attractions are accessible by tram from Magdeburg Hauptbahnhof · tourismusmagdeburg.de")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: CULTURAL VENUES — VISITOR TRENDS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(section_header("Cultural Venues — Visitor Trends", color=CITY_PURPLE), unsafe_allow_html=True)

cult_l, cult_r = st.columns(2)

with cult_l:
    st.caption("City library — annual visitors")
    try:
        df_lib = load_kiss("bildung-und-kultur/monatliche-besuchszahlen-bestaende-und-entleihungen.json")
        lib_col = next((c for c in df_lib.columns if "besucher" in c.lower()), None)
        if lib_col:
            df_lib[lib_col] = pd.to_numeric(df_lib[lib_col], errors="coerce")
            lib_annual = df_lib.groupby("Jahr")[lib_col].sum().reset_index()
            lib_annual = lib_annual[lib_annual[lib_col] > 0]

            fig_lib = go.Figure(go.Bar(
                x=lib_annual["Jahr"], y=lib_annual[lib_col],
                marker_color=CITY_PURPLE, opacity=0.8,
                hovertemplate="%{x}: %{y:,} visitors<extra></extra>",
            ))
            peak_lib = lib_annual.loc[lib_annual[lib_col].idxmax()]
            fig_lib.add_annotation(
                x=peak_lib["Jahr"], y=peak_lib[lib_col],
                text=f"Peak: {int(peak_lib[lib_col]):,}".replace(",", "."),
                showarrow=True, arrowhead=2, ax=30, ay=-30,
            )
            fig_lib.update_layout(
                template=PLOTLY_TEMPLATE,
                yaxis_title="Visitors / year", yaxis=dict(tickformat=",d"),
                margin=dict(l=50, r=10, t=20, b=40), height=280,
            )
            st.plotly_chart(fig_lib, use_container_width=True)
        else:
            st.info("Library visitor column not found.")
    except Exception as e:
        st.info(f"Library data unavailable: {e}")

with cult_r:
    st.caption("Gruson Gewächshäuser (botanical greenhouse) — annual visitors")
    try:
        df_gr = load_kiss("bildung-und-kultur/besuche-gruson-gewaechshaeuser.json")
        gr_col = next((c for c in df_gr.columns if "besucher" in c.lower()), None)
        if gr_col:
            df_gr[gr_col] = pd.to_numeric(df_gr[gr_col], errors="coerce")
            gr_annual = df_gr.groupby("Jahr")[gr_col].sum().reset_index()
            gr_annual = gr_annual[gr_annual[gr_col] > 0]

            fig_gr = go.Figure(go.Bar(
                x=gr_annual["Jahr"], y=gr_annual[gr_col],
                marker_color="#16A34A", opacity=0.8,
                hovertemplate="%{x}: %{y:,} visitors<extra></extra>",
            ))
            fig_gr.update_layout(
                template=PLOTLY_TEMPLATE,
                yaxis_title="Visitors / year", yaxis=dict(tickformat=",d"),
                margin=dict(l=50, r=10, t=20, b=40), height=280,
            )
            st.plotly_chart(fig_gr, use_container_width=True)
        else:
            st.info("Greenhouse visitor column not found.")
    except Exception as e:
        st.info(f"Greenhouse data unavailable: {e}")

st.markdown(insight_box(
    "Library visits peaked before the pandemic and have partially recovered since 2022. "
    "The Gruson Gewächshäuser draw steady year-round visitors — its climate-controlled "
    "tropical environment is especially popular in winter months. "
    "Both venues are free or low-cost, making them key cultural assets for all residents."
), unsafe_allow_html=True)
st.caption("Source: KISS-MD / Stadtbibliothek Magdeburg · Gruson-Gewächshäuser")


