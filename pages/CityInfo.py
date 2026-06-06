import base64
import os
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta

from utils.data_loader import load_kiss
from utils.constants import MD_TEAL, MD_ORANGE, PLOTLY_TEMPLATE, MONTHS_DE
from utils.ui_helpers import hero_stat, section_header, insight_box, live_card

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
    "Everything you need as a citizen or visitor — city attractions, upcoming events, "
    "tourism statistics, cultural venues, and essential service contacts."
    "</p>",
    unsafe_allow_html=True,
)
st.caption("Sources: KISS-MD / Statistisches Amt Magdeburg · Tourismusverband Sachsen-Anhalt · Landeshauptstadt Magdeburg")

# ── Hero KPI: guest arrivals ──────────────────────────────────────────────────
try:
    df_arr = load_kiss("erholung-sport-und-fremdenverkehr/ankuenfte-der-gaeste-in-magdeburg.json")
    arr_col = next((c for c in df_arr.columns if "ankünfte" in c.lower() and "gesamt" in c.lower()), None)
    if not arr_col:
        arr_col = next((c for c in df_arr.columns if "ankünfte" in c.lower()), None)
    if arr_col:
        df_arr[arr_col] = pd.to_numeric(df_arr[arr_col], errors="coerce")
        by_year = df_arr.groupby("Jahr")[arr_col].sum()
        cy, py = int(by_year.index.max()), int(by_year.index.max()) - 1
        arr_cy = int(by_year[cy])
        arr_py = int(by_year.get(py, arr_cy))
        arr_delta = arr_cy - arr_py
        st.markdown(hero_stat(
            "✈️",
            f"{arr_cy:,}".replace(",", "."),
            f"Guest arrivals in Magdeburg · {cy}",
            f"{'+' if arr_delta >= 0 else ''}{arr_delta:,} vs {py}".replace(",", "."),
            delta_positive=arr_delta >= 0,
            color=CITY_PURPLE,
        ), unsafe_allow_html=True)
except Exception:
    pass

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: TOURISM AT A GLANCE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(section_header("Tourism at a Glance", color=CITY_PURPLE), unsafe_allow_html=True)

t1, t2, t3, t4 = st.columns(4)

with t1:
    try:
        df_a = load_kiss("erholung-sport-und-fremdenverkehr/ankuenfte-der-gaeste-in-magdeburg.json")
        col_a = next((c for c in df_a.columns if "ankünfte" in c.lower() and "gesamt" in c.lower()), None) or \
                next((c for c in df_a.columns if "ankünfte" in c.lower()), None)
        df_a[col_a] = pd.to_numeric(df_a[col_a], errors="coerce")
        cy_val = int(df_a.groupby("Jahr")[col_a].sum().iloc[-1])
        cy_yr  = int(df_a["Jahr"].max())
        st.markdown(live_card("✈️", "Guest Arrivals",
            f"{cy_val:,}".replace(",", "."), f"Total visitors · {cy_yr}",
            status_color=CITY_PURPLE), unsafe_allow_html=True)
    except Exception:
        st.markdown(live_card("✈️", "Guest Arrivals", "—", "data unavailable",
            status_color=CITY_PURPLE), unsafe_allow_html=True)

with t2:
    try:
        df_o = load_kiss("erholung-sport-und-fremdenverkehr/anzahl-der-uebernachtungen-der-gaeste-in-magdeburg.json")
        col_o = next((c for c in df_o.columns if "übernachtungen" in c.lower() and "gesamt" in c.lower()), None) or \
                next((c for c in df_o.columns if "übernachtung" in c.lower()), None)
        df_o[col_o] = pd.to_numeric(df_o[col_o], errors="coerce")
        o_val = int(df_o.groupby("Jahr")[col_o].sum().iloc[-1])
        o_yr  = int(df_o["Jahr"].max())
        st.markdown(live_card("🛏️", "Overnight Stays",
            f"{o_val:,}".replace(",", "."), f"Nights booked · {o_yr}",
            status_color=CITY_PURPLE), unsafe_allow_html=True)
    except Exception:
        st.markdown(live_card("🛏️", "Overnight Stays", "—", "data unavailable",
            status_color=CITY_PURPLE), unsafe_allow_html=True)

with t3:
    try:
        df_d = load_kiss("erholung-sport-und-fremdenverkehr/durchschnittliche-aufenthaltsdauer-der-gaeste-in-magdeburg.json")
        col_d = next((c for c in df_d.columns if "aufenthalt" in c.lower() and "gesamt" in c.lower()), None) or \
                next((c for c in df_d.columns if "aufenthalt" in c.lower()), None)
        df_d[col_d] = pd.to_numeric(df_d[col_d], errors="coerce")
        d_val = round(float(df_d[df_d[col_d].notna()].sort_values("Jahr")[col_d].iloc[-1]), 1)
        d_yr  = int(df_d["Jahr"].max())
        st.markdown(live_card("⏱️", "Avg Stay Duration",
            f"{d_val} nights", f"Per visitor · {d_yr}",
            status_color=CITY_PURPLE), unsafe_allow_html=True)
    except Exception:
        st.markdown(live_card("⏱️", "Avg Stay Duration", "—", "data unavailable",
            status_color=CITY_PURPLE), unsafe_allow_html=True)

with t4:
    try:
        df_p = load_kiss("erholung-sport-und-fremdenverkehr/besucher-der-kommunalen-baeder-und-saunen.json")
        col_p = next((c for c in df_p.columns if "besucher" in c.lower()), None)
        df_p[col_p] = pd.to_numeric(df_p[col_p], errors="coerce")
        p_val = int(df_p.groupby("Jahr")[col_p].sum().iloc[-1])
        p_yr  = int(df_p["Jahr"].max())
        st.markdown(live_card("🏊", "Public Pool Visitors",
            f"{p_val:,}".replace(",", "."), f"Municipal pools & saunas · {p_yr}",
            status_color="#0891B2"), unsafe_allow_html=True)
    except Exception:
        st.markdown(live_card("🏊", "Public Pool Visitors", "—", "data unavailable",
            status_color="#0891B2"), unsafe_allow_html=True)

st.caption("Source: KISS-MD / Tourismusstatistik Sachsen-Anhalt")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: TOURISM TRENDS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(section_header("Tourism Trends", color=CITY_PURPLE), unsafe_allow_html=True)

tr_left, tr_right = st.columns(2)

with tr_left:
    st.caption("Monthly guest arrivals — domestic vs international")
    try:
        df_arr2 = load_kiss("erholung-sport-und-fremdenverkehr/ankuenfte-der-gaeste-in-magdeburg.json")
        inland_col = next((c for c in df_arr2.columns if "inland" in c.lower()), None)
        ausland_col = next((c for c in df_arr2.columns if "ausland" in c.lower()), None)
        if inland_col and ausland_col:
            df_arr2[inland_col]  = pd.to_numeric(df_arr2[inland_col],  errors="coerce")
            df_arr2[ausland_col] = pd.to_numeric(df_arr2[ausland_col], errors="coerce")
            years_avail = sorted(df_arr2["Jahr"].dropna().unique(), reverse=True)
            sel_yr = st.selectbox("Year", years_avail, key="arr_year")
            df_m = df_arr2[df_arr2["Jahr"] == sel_yr].copy()
            df_m["month_num"] = df_m["Monat"].map(MONTHS_DE).fillna(0).astype(int)
            df_m = df_m.sort_values("month_num")
            df_m["month_label"] = df_m["month_num"].apply(
                lambda n: ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][n] if 1 <= n <= 12 else str(n)
            )
            fig_arr = go.Figure()
            fig_arr.add_trace(go.Bar(
                x=df_m["month_label"], y=df_m[inland_col],
                name="Domestic", marker_color=CITY_PURPLE,
                hovertemplate="%{x}: %{y:,}<extra>Domestic</extra>",
            ))
            fig_arr.add_trace(go.Bar(
                x=df_m["month_label"], y=df_m[ausland_col],
                name="International", marker_color=MD_ORANGE,
                hovertemplate="%{x}: %{y:,}<extra>International</extra>",
            ))
            fig_arr.update_layout(
                template=PLOTLY_TEMPLATE, barmode="stack",
                yaxis_title="Arrivals", yaxis=dict(tickformat=",d"),
                legend=dict(orientation="h", y=-0.2),
                margin=dict(l=50, r=10, t=20, b=60), height=300,
            )
            st.plotly_chart(fig_arr, use_container_width=True)
        else:
            st.info("Domestic/international breakdown unavailable.")
    except Exception as e:
        st.info(f"Arrivals data unavailable: {e}")

with tr_right:
    st.caption("Annual overnight stays + avg stay duration trend")
    try:
        df_ov = load_kiss("erholung-sport-und-fremdenverkehr/anzahl-der-uebernachtungen-der-gaeste-in-magdeburg.json")
        df_dur = load_kiss("erholung-sport-und-fremdenverkehr/durchschnittliche-aufenthaltsdauer-der-gaeste-in-magdeburg.json")
        ov_col  = next((c for c in df_ov.columns  if "übernachtung" in c.lower() and "gesamt" in c.lower()), None) or \
                  next((c for c in df_ov.columns  if "übernachtung" in c.lower()), None)
        dur_col = next((c for c in df_dur.columns if "aufenthalt" in c.lower() and "gesamt" in c.lower()), None) or \
                  next((c for c in df_dur.columns if "aufenthalt" in c.lower()), None)

        df_ov[ov_col]   = pd.to_numeric(df_ov[ov_col],   errors="coerce")
        df_dur[dur_col] = pd.to_numeric(df_dur[dur_col], errors="coerce")

        ov_annual  = df_ov.groupby("Jahr")[ov_col].sum().reset_index()
        dur_annual = df_dur.groupby("Jahr")[dur_col].mean().reset_index()

        fig_ov = go.Figure()
        fig_ov.add_trace(go.Bar(
            x=ov_annual["Jahr"], y=ov_annual[ov_col],
            name="Overnight stays", marker_color=CITY_PURPLE, opacity=0.8,
            hovertemplate="%{x}: %{y:,}<extra>Overnight stays</extra>",
        ))
        fig_ov.add_trace(go.Scatter(
            x=dur_annual["Jahr"], y=dur_annual[dur_col],
            mode="lines+markers", name="Avg stay (nights)",
            line=dict(color=MD_ORANGE, width=2),
            yaxis="y2",
            hovertemplate="%{x}: %{y:.1f} nights<extra></extra>",
        ))
        fig_ov.update_layout(
            template=PLOTLY_TEMPLATE,
            yaxis=dict(title="Overnight stays", tickformat=",d"),
            yaxis2=dict(title="Avg nights", overlaying="y", side="right"),
            legend=dict(orientation="h", y=-0.2),
            margin=dict(l=50, r=60, t=20, b=60), height=300,
        )
        st.plotly_chart(fig_ov, use_container_width=True)
    except Exception as e:
        st.info(f"Overnight stays data unavailable: {e}")

st.markdown(insight_box(
    "Summer months (July–August) see peak arrivals. International visitors account for roughly "
    "30–35% of total arrivals, with the share growing steadily. "
    "Average stays are short (1.5–2 nights), typical of a city-break destination — "
    "most visitors come for events, the Dom, and Hundertwasserhaus."
), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: KEY ATTRACTIONS
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
# SECTION 4: MUSEUM & LIBRARY VISITORS
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

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5: UPCOMING EVENTS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(section_header("Upcoming Events in Magdeburg", color=CITY_PURPLE), unsafe_allow_html=True)

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
# SECTION 6: CITY SERVICES & CONTACTS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(section_header("City Services & Contacts", color=CITY_PURPLE), unsafe_allow_html=True)

contacts = [
    {"icon": _FIRE,   "name": "Emergency (Fire / Ambulance)", "number": "112",
     "detail": "European emergency number — free from any phone.", "color": "#C0392B"},
    {"icon": _POLICE, "name": "Police Emergency", "number": "110",
     "detail": "German police emergency number.", "color": "#1565C0"},
    {"icon": "🏥",    "name": "Medical On-Call", "number": "116 117",
     "detail": "Ärztlicher Bereitschaftsdienst — non-emergency medical help.", "color": "#DC2626"},
    {"icon": _BLDG,   "name": "City Hall (Rathaus)", "number": "+49 391 540-0",
     "detail": "General enquiries · Mon–Fri 08:00–18:00", "color": "#007A6E"},
    {"icon": _BUS,    "name": "MVB Public Transport", "number": "+49 391 886-0",
     "detail": "Tram & bus info, journey planner: mvbnet.de", "color": "#6A1B9A"},
    {"icon": "💡", "name": "Stadtwerke Magdeburg", "number": "+49 391 587-0",
     "detail": "Gas, electricity, heating and water services.", "color": "#F59E0B"},
    {"icon": "🔧", "name": "City Maintenance", "number": "+49 391 540-2233",
     "detail": "Report road defects, broken streetlights, and public space issues.", "color": "#78716C"},
    {"icon": "📚", "name": "City Library", "number": "+49 391 540-4506",
     "detail": "Stadtbibliothek Magdeburg · Mon–Sat 10:00–19:00", "color": "#0891B2"},
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
    <span style="display:inline-flex;align-items:center;font-size:1.4rem;line-height:1;">{c["icon"]}</span>
    <span style="font-size:0.78rem;font-weight:700;color:#374151;">{c["name"]}</span>
  </div>
  <div style="font-size:1.15rem;font-weight:900;color:{c['color']};margin-bottom:4px;">{c["number"]}</div>
  <div style="font-size:0.74rem;color:#94a3b8;">{c["detail"]}</div>
</div>
""", unsafe_allow_html=True)
