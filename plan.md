  ---
  Smart City Magdeburg Dashboard
  
  A hackathon project (24-hour pitch prototype) to build a smart city dashboard for Magdeburg, Germany. The repo is in early stage — only data
  and docs so far, no frontend/backend code yet.

  Structure

  data/
  ├── kiss-md/           322 static JSON datasets from Magdeburg's municipal statistics portal
  ├── live-sources/      Docs for runtime APIs (weather, river, air quality, transit)
  ├── mietspiegel-2024/  Rent index data 2012–2026 by district
  ├── sensor-data/       DWD climate station data (daily from 1881, monthly from 1834)
  └── steuereinnahmen/   Tax revenue data 2010–2025 + tax rate history

  Available Data (KISS-MD — 322 datasets across 13 categories)

  ┌──────────────────────────────────────────────┬──────────┐
  │                   Category                   │ Datasets │
  ├──────────────────────────────────────────────┼──────────┤
  │ Wirtschaft (economy)                         │ 58       │
  ├──────────────────────────────────────────────┼──────────┤
  │ Energie & Umwelt (energy/environment)        │ 45       │
  ├──────────────────────────────────────────────┼──────────┤
  │ Bevoelkerung (population)                    │ 38       │
  ├──────────────────────────────────────────────┼──────────┤
  │ Bautätigkeit & Wohnen (construction/housing) │ 37       │
  ├──────────────────────────────────────────────┼──────────┤
  │ Verkehr (transport)                          │ 31       │
  ├──────────────────────────────────────────────┼──────────┤
  │ Oeffentliche Ordnung (public order)          │ 34       │
  ├──────────────────────────────────────────────┼──────────┤
  │ Bautätigkeit & Wohnen (construction/housing) │ 37       │
  ├──────────────────────────────────────────────┼──────────┤
  │ Verkehr (transport)                          │ 31       │
  ├──────────────────────────────────────────────┼──────────┤
  │ Oeffentliche Ordnung (public order)          │ 34       │
  ├──────────────────────────────────────────────┼──────────┤
  │ Bildung & Kultur (education/culture)         │ 28       │
  ├──────────────────────────────────────────────┼──────────┤
  │ Arbeitsmarkt (labor market)                  │ 23       │
  ├──────────────────────────────────────────────┼──────────┤
  │ ... + 5 more                                 │          │
  └──────────────────────────────────────────────┴──────────┘

  Live APIs (browser-callable)

  - Bright Sky/DWD — current weather
  - PEGELONLINE/WSV — Elbe river water level
  - Sensor.Community — air quality / PM10/PM2.5
  - OSM tiles + LVermGeo — map layers
  - GovData CKAN — open dataset catalogue
  - Sensor.Community — air quality / PM10/PM2.5
  - OSM tiles + LVermGeo — map layers
  - GovData CKAN — open dataset catalogue

  LLM Integration

  A docs_README.md describes a Watsonx/Granite 4 Small LLM backend accessible via ${SERVER_URL}/api/llm/chat — likely provided by hackathon
  organizers for AI-powered features.

  What's Missing

  No frontend or backend code exists yet — this is a blank canvas with rich data. The reference projects (Regensburg, Münster, Saarbrücken
  dashboards) suggest a web-based interactive dashboard with maps, charts, and live indicators.

✻ Baked for 49s

❯ /plan                                                                                                                                         
  ⎿  Enabled plan mode

❯ Create a practical implementation plan for a Smart City Magdeburg Dashboard hackathon project                                                 

⏺ I'll start by exploring the codebase more deeply in parallel to understand the data and examples before designing.

⏺ Explore(Explore KISS-MD example code and key datasets)
   ├ Explore KISS-MD example code and key datasets · 5 tool uses · 8.6k tokens

⏺ 2 Explore agents finished (ctrl+o to expand)
   ├ Explore KISS-MD example code and key datasets · 11 tool uses · 23.7k tokens
   │ ⎿  Done
   └ Explore sensor data, tax data, and rent data schemas · 24 tool uses · 18.0k tokens
     ⎿  Done

⏺ Good — I have a thorough picture of the data. Let me ask a few key questions before writing the plan.
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Planning: /Users/kumar/.claude/plans/create-a-practical-implementation-radiant-bunny.md
⏺ User answered Claude's questions:
  ⎿  · What tech stack should the dashboard use? → Python (Streamlit or Dash)
     · Which topic areas should the dashboard prioritize? (Choose up to 3) → Climate & Environment, Population & Housing, Mobility & Transport, 
     Economy & Financenclude the LLM AI chat feature (using the hackathon-provided Watsonx/Granite 4 backend)?
     · Should the dashboard include the LLM AI chat feature (using the hackathon-provided Watsonx/Granite 4 backend)? → No — charts and maps 
  1  only
   
⏺ Now I have everything I need. Let me design the implementation and write the plan.

⏺ Plan(Design Streamlit dashboard architecture)
  ⎿  Read(README.md)
         ls /Users/kumar/Desktop/Projects.nosync/Personal…)
     Running…
         import json…)urces/DATENQUELLEN.md)
     Running…
  ⎿  · What tech stack should the dashboard use? → Python (Streamlit or Dash)
     · Which topic areas should the dashboard prioritize? (Choose up to 3) → Climate & Environment, Population & Housing, Mobility & Transport,
     Economy & Finance
     · Should the dashboard include the LLM AI chat feature (using the hackathon-provided Watsonx/Granite 4 backend)? → No — charts and maps
     only

⏺ Now I have everything I need. Let me design the implementation and write the plan.

⏺ Plan(Design Streamlit dashboard architecture)
  ⎿  Done (64 tool uses · 71.0k tokens · 6m 47s)
  (ctrl+o to expand)

⏺ Excellent plan. Now writing the final plan file.

⏺ Updated plan
  ⎿  /plan to preview

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 Ready to code?

 Here is Claude's plan:
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
 Smart City Magdeburg Dashboard — Implementation Plan

 Context

 A 24-hour hackathon prototype that demonstrates added value for the city of Magdeburg. The repo ships 322 static JSON datasets (KISS-MD), DWD
 climate data back to 1834, rental market data, and tax revenue data. Three live APIs are available (weather, Elbe river level, air quality).
 The goal is a multi-page Streamlit dashboard covering all four topic areas: Climate & Environment, Population & Housing, Mobility & Transport,
 and Economy & Finance — with live data on the home page.

 ---
 File Structure

 smart-city-magdeburg/        # repo root
 ├── app.py                   # entry point — st.set_page_config + st.navigation()
 ├── requirements.txt
 ├── .streamlit/config.toml
 ├── pages/
 │   ├── 1_Home.py            # live KPI cards + Folium map
 │   ├── 2_Climate.py
 │   ├── 3_Population_Housing.py
 │   ├── 4_Mobility.py
 │   └── 5_Economy.py
 └── utils/
     ├── constants.py         # DATA_ROOT, MONTHS_DE, brand colours
     ├── data_loader.py       # @st.cache_data JSON readers
     ├── live_api.py          # BrightSky, Pegelonline, Sensor.Community
     └── chart_helpers.py     # Plotly wrappers (line, bar, heatmap)

 Data files are read-only from their existing paths under data/ — no copies or symlinks.

 ---
 Page Breakdown

 Page 1 — Home / Overview (pages/1_Home.py)

 Live KPI cards (4 columns):
 - Temperature + condition → api.brightsky.dev/current_weather?lat=52.1205&lon=11.6276
 - Wind speed km/h → same BrightSky response
 - Elbe river level (cm, colour-coded: green <400, amber 400–600, red >600) →
 pegelonline.wsv.de/…/MAGDEBURG-STROMBR%C3%9CCKE/W/currentmeasurement.json
 - PM2.5 µg/m³ averaged over nearby sensors → data.sensor.community/airrohr/v1/filter/area=52.1205,11.6276,10 (show "No sensors active" if
 empty array)

 Static KPI strip: latest population (bevoelkerungsbestand-monatlich.json var5), registered vehicles, total 2024 tax revenue, avg rent/m².

 Folium map: OSM tiles, center 52.1205/11.6276, zoom 12, 5 hardcoded landmark markers (Rathaus, Dom, Elbe km-marker, Hauptbahnhof,
 Universität). Use streamlit_folium.st_folium().

 Sidebar: "Last refreshed" timestamp + Refresh button that calls st.cache_data.clear() on live-API functions only.

 ---
 Page 2 — Climate & Environment (pages/2_Climate.py)

 ┌──────────────────┬──────────────────────────────────────────────────────────────────────────┬───────────────────────────────────────────┐
 │      Chart       │                                 Dataset                                  │                Description                │
 ├──────────────────┼──────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────┤
 │ Temperature      │ sensor-data/json/klima-monat.json MO_TT                                  │ Bars above/below 1961–1990 baseline mean, │
 │ anomaly          │                                                                          │  10yr rolling line, year slider           │
 ├──────────────────┼──────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────┤
 │ Precipitation    │ same file, MO_RR                                                         │ Plotly heatmap year × month               │
 │ heatmap          │                                                                          │                                           │
 ├──────────────────┼──────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────┤
 │ Air pollutants   │ kiss-md/json/energie-und-umwelt/schadstoffkonzentration-in-der-luft.json │ NO₂ (var3), O₃ (var5), PM₁₀ (var7) lines, │
 │ trend            │                                                                          │  EU limit annotations                     │
 └──────────────────┴──────────────────────────────────────────────────────────────────────────┴───────────────────────────────────────────┘

 ---
 Page 3 — Population & Housing (pages/3_Population_Housing.py)

 ┌────────────────┬────────────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────┐
 │     Chart      │                            Dataset                             │                      Description                      │
 ├────────────────┼────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────┤
 │ Population     │ bevoelkerung/bevoelkerungsbestand-monatlich.json var5          │ Total + German vs. foreign stacked area, parse German │
 │ time series    │                                                                │  month names via MONTHS_DE                            │
 ├────────────────┼────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────┤
 │ Rent by        │                                                                │ Horizontal bar per Stadtteil for selected year + area │
 │ district       │ mietspiegel-2024/nach-wohnflaeche.json                         │  class; drop null rows; no choropleth (no GeoJSON     │
 │                │                                                                │ available)                                            │
 ├────────────────┼────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────┤
 │ Vacancy trend  │ bautaetigkeit-und-wohnen/leerstand-im-geschosswohnungsbau.json │ City-wide mean vacancy % 1999–present, annotate 2001  │
 │                │                                                                │ peak                                                  │
 └────────────────┴────────────────────────────────────────────────────────────────┴───────────────────────────────────────────────────────┘

 ---
 Page 4 — Mobility & Transport (pages/4_Mobility.py)

 ┌────────────────────┬──────────────────────────────────────────────────────────────────────────────────┬────────────────────────────────┐
 │       Chart        │                                     Dataset                                      │          Description           │
 ├────────────────────┼──────────────────────────────────────────────────────────────────────────────────┼────────────────────────────────┤
 │ Vehicle fleet      │ verkehr/entwicklung-des-kraftfahrzeugbestandes-in-magdeburg.json                 │ PKW + motorcycles + trucks +   │
 │ stacked area       │                                                                                  │ vans, 2011–2025                │
 ├────────────────────┼──────────────────────────────────────────────────────────────────────────────────┼────────────────────────────────┤
 │ MVB ridership vs.  │ befoerderte-personen-der-magdeburger-verkehrsbetriebe-gmbh-und-co-kg.json +      │ Dual y-axis 2011–2021          │
 │ fleet              │ fleet data                                                                       │                                │
 ├────────────────────┼──────────────────────────────────────────────────────────────────────────────────┼────────────────────────────────┤
 │ Accidents heatmap  │ verkehr/verkehrsunfaelle-nach-monaten.json                                       │ Year × month heatmap, seasonal │
 │                    │                                                                                  │  pattern                       │
 └────────────────────┴──────────────────────────────────────────────────────────────────────────────────┴────────────────────────────────┘

 ---
 Page 5 — Economy & Finance (pages/5_Economy.py)

 Chart: Tax revenue grouped bar
 Dataset: steuereinnahmen/json/steuereinnahmen-2010-2025.json
 Description: Major tax types as groups, years on x-axis; coalesce Grundsteuer-B split (see gotchas)
 ────────────────────────────────────────
 Chart: Business net balance
 Dataset: wirtschaft/gewerbean-und-abmeldungen-am-jahresende.json
 Description: Diverging bar: registrations above / deregistrations below x-axis
 ────────────────────────────────────────
 Chart: Employment by sector
 Dataset: arbeitsmarkt/sozialversicherungspflichtig-beschaeftigte-am-arbeitsort-je-wirtschaftsabschnitt-wz-2008-nach-geschlecht.json
 Description: Horizontal ranked bar for latest year

 ---
 Shared Utilities

 utils/constants.py

 DATA_ROOT = Path(__file__).parent.parent / "data"
 MONTHS_DE = {"Januar":1, "Februar":2, "März":3, "April":4, "Mai":5, "Juni":6,
              "Juli":7, "August":8, "September":9, "Oktober":10, "November":11, "Dezember":12}
 MONTHS_DE_ORDER = list(MONTHS_DE.keys())
 MD_TEAL, MD_ORANGE, MD_BLUE = "#007A6E", "#E87722", "#004B87"
 PLOTLY_TEMPLATE = "plotly_white"
 LAT, LON = 52.1205, 11.6276

 utils/data_loader.py — three patterns

 Generic KISS-MD loader (all 322 datasets):
 @st.cache_data
 def load_kiss(relative_path: str) -> pd.DataFrame:
     path = DATA_ROOT / "kiss-md" / "json" / relative_path
     raw = json.loads(path.read_bytes())
     label_map = {c["key"]: c.get("label") or c["key"] for c in raw["columns"]}
     return pd.DataFrame(raw["rows"]).rename(columns=label_map)

 klima-tag filtered loader (18 MB — never load all rows):
 @st.cache_data
 def load_klima_tag(year_from: int = 2000) -> pd.DataFrame:
     raw = json.loads((DATA_ROOT / "sensor-data/json/klima-tag.json").read_bytes())
     rows = [r for r in raw["rows"] if int(r["date"][:4]) >= year_from]
     df = pd.DataFrame(rows)
     df["date"] = pd.to_datetime(df["date"])
     return df
 Pass a fixed floor (2000), filter further in-memory per page. Never pass slider value into cache key.

 Mietspiegel loader:
 @st.cache_data
 def load_mietspiegel(by: str = "wohnflaeche") -> pd.DataFrame:
     fname = "nach-wohnflaeche.json" if by == "wohnflaeche" else "nach-baualter.json"
     raw = json.loads((DATA_ROOT / "mietspiegel-2024" / fname).read_bytes())
     return pd.DataFrame(raw["rows"]).dropna(subset=["nettokaltmiete_pro_qm"])

 utils/live_api.py

 All three functions use @st.cache_data(ttl=600) and return None on any exception. UI must check if value is None and show st.warning("Live
 data unavailable").

 - fetch_weather() → requests.get(brightsky_url, timeout=5).json()["weather"]
 - fetch_elbe_level() → pegelonline JSON {"timestamp": …, "value": <cm>}
 - fetch_air_quality() → iterate sensordatavalues, filter value_type == "P2", return mean or None

 utils/chart_helpers.py

 Three wrappers — line_chart(), bar_chart(), heatmap() — each calling fig.update_layout(template=PLOTLY_TEMPLATE) and returning a go.Figure
 passed to st.plotly_chart(fig, use_container_width=True).

 ---
 requirements.txt

 streamlit>=1.35.0
 plotly>=5.22.0
 pandas>=2.2.0
 requests>=2.31.0
 folium>=0.17.0
 streamlit-folium>=0.20.0

 .streamlit/config.toml

 [theme]
 primaryColor = "#007A6E"
 backgroundColor = "#FFFFFF"
 secondaryBackgroundColor = "#F0F2F6"
 textColor = "#1A1A1A"
 font = "sans serif"

 [runner]
 fastReruns = true

 ---
 Key Gotchas

 ┌──────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │        Issue         │                                                       Fix                                                        │
 ├──────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ Grundsteuer-B split  │ Coalesce at load: df["grundsteuer_b"] = df["grundsteuer-b-bis-2024"].fillna(0) +                                 │
 │ in 2025              │ df["grundsteuer-b-ab-2025-wohngrundstuecke"].fillna(0) +                                                         │
 │                      │ df["grundsteuer-b-ab-2025-nichtwohngrundstuecke"].fillna(0)                                                      │
 ├──────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ Sensor.Community     │ fetch_air_quality() returns None; UI shows greyed card with "No sensors active"                                  │
 │ empty array          │                                                                                                                  │
 ├──────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ Pegelonline URL      │ Use literal MAGDEBURG-STROMBR%C3%9CCKE in URL string, not via params= (double-encodes)                           │
 │ encoding             │                                                                                                                  │
 ├──────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ German month sort    │ Map through MONTHS_DE → integer, use MONTHS_DE_ORDER as category_orders in Plotly                                │
 │ order                │                                                                                                                  │
 ├──────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ KISS-MD null labels  │ load_kiss() falls back to varN key names; each page applies explicit df.rename() for columns it uses             │
 ├──────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ Stadtteil numeric    │ Datasets with numeric IDs (e.g. entwicklung-der-hauptwohnsitzbevoelkerung) should render by code, not name —     │
 │ IDs                  │ don't spend time building the full mapping                                                                       │
 ├──────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ macOS SSL on         │ Run /Applications/Python 3.x/Install Certificates.command if SSL errors on local dev                             │
 │ BrightSky            │                                                                                                                  │
 └──────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

 ---
 Build Order (24h)

 1. Hours 1–2: Scaffold (app.py, utils/, requirements.txt, .streamlit/config.toml), confirm Streamlit runs
 2. Hours 3–5: pages/1_Home.py — all live KPIs + Folium map (jury first impression)
 3. Hours 6–9: pages/5_Economy.py — cleanest dataset, highest-clarity charts
 4. Hours 10–14: pages/2_Climate.py — temperature anomaly + precipitation heatmap
 5. Hours 15–18: pages/3_Population_Housing.py — population line + rent bar
 6. Hours 19–22: pages/4_Mobility.py — fleet stacked area + accidents heatmap
 7. Hours 23–24: Polish: chart_helpers.py wrappers, consistent colours, st.caption() source attribution on every chart, null/fallback testing

 Skip if time runs out: choropleth rent map (no GeoJSON), daily klima-tag charts, MVB ticket-type breakdown (unlabelled columns), Overpass/GTFS
 integration.

 ---
 ├──────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ KISS-MD null labels  │ load_kiss() falls back to varN key names; each page applies explicit df.rename() for columns it uses             │
 ├──────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ Stadtteil numeric    │ Datasets with numeric IDs (e.g. entwicklung-der-hauptwohnsitzbevoelkerung) should render by code, not name —     │
 │ IDs                  │ don't spend time building the full mapping                                                                       │
 ├──────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ macOS SSL on         │ Run /Applications/Python 3.x/Install Certificates.command if SSL errors on local dev                             │
 │ BrightSky            │                                                                                                                  │
 └──────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

 ---
 Build Order (24h)

 1. Hours 1–2: Scaffold (app.py, utils/, requirements.txt, .streamlit/config.toml), confirm Streamlit runs
 2. Hours 3–5: pages/1_Home.py — all live KPIs + Folium map (jury first impression)
 3. Hours 6–9: pages/5_Economy.py — cleanest dataset, highest-clarity charts
 4. Hours 10–14: pages/2_Climate.py — temperature anomaly + precipitation heatmap
 5. Hours 15–18: pages/3_Population_Housing.py — population line + rent bar
 6. Hours 19–22: pages/4_Mobility.py — fleet stacked area + accidents heatmap
 7. Hours 23–24: Polish: chart_helpers.py wrappers, consistent colours, st.caption() source attribution on every chart, null/fallback testing

 Skip if time runs out: choropleth rent map (no GeoJSON), daily klima-tag charts, MVB ticket-type breakdown (unlabelled columns), Overpass/GTFS
 integration.

 ---
 Verification

 1. pip install -r requirements.txt && streamlit run app.py — confirm all 5 pages load without error
 2. Disconnect network → confirm all 4 live KPI cards show "unavailable" fallback (not a crash)
 3. Confirm klima-monat.json anomaly chart renders with year slider at 1950–2026 and 1900–2026
 4. Confirm steuereinnahmen chart shows continuous Grundsteuer-B bar across the 2024/2025 split
 5. Confirm rent chart shows only districts with non-null data for the selected year/area class