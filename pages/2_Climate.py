import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from utils.data_loader import load_klima_monat, load_kiss
from utils.chart_helpers import heatmap, line_chart
from utils.constants import MONTHS_DE, MONTHS_DE_ORDER, MD_TEAL, MD_BLUE, MD_RED, PLOTLY_TEMPLATE
from utils.ui_helpers import hero_stat

st.title("Climate & Environment")
st.caption("Sources: DWD Climate Data Center (station 03126 Magdeburg) · KISS-MD / Landeshauptstadt Magdeburg")

df = load_klima_monat()

# ── Hero KPI ──────────────────────────────────────────────────────────────────
try:
    _baseline = df[(df["year"] >= 1961) & (df["year"] <= 1990)]["MO_TT"].mean()
    _yearly   = df[df["MO_TT"].notna()].groupby("year")["MO_TT"].mean()
    _comp     = _yearly[_yearly.index < datetime.now().year]
    _la, _pya = float(_comp.iloc[-1]) - _baseline, float(_comp.iloc[-2]) - _baseline
    _yr       = int(_comp.index[-1])
    _sign     = "+" if _la >= 0 else ""
    _diff     = _la - _pya
    st.markdown(hero_stat(
        "🌡️",
        f"{_sign}{_la:.1f} °C",
        f"Annual temperature anomaly vs 1961–1990 baseline ({_baseline:.1f} °C) · {_yr}",
        f"{'+' if _diff>=0 else ''}{_diff:.1f} °C vs {_yr-1}",
        delta_positive=False,
        color="#00897B",
    ), unsafe_allow_html=True)
except Exception:
    pass

# ── Chart 1: Temperature anomaly ─────────────────────────────────────────────
st.subheader("Monthly Temperature Anomaly")
st.caption("Deviation from the 1961–1990 WMO baseline mean · 10-year rolling average overlay")

year_min, year_max = st.slider(
    "Year range", int(df["year"].min()), int(df["year"].max()),
    value=(1950, int(df["year"].max())), key="temp_years",
)

df_temp = df[df["MO_TT"].notna()].copy()
baseline = df_temp[(df_temp["year"] >= 1961) & (df_temp["year"] <= 1990)]["MO_TT"].mean()
df_temp["anomaly"] = df_temp["MO_TT"] - baseline

df_annual = (
    df_temp.groupby("year")["MO_TT"]
    .mean()
    .reset_index()
    .rename(columns={"MO_TT": "annual_mean"})
)
df_annual["anomaly"] = df_annual["annual_mean"] - baseline
df_annual["rolling10"] = df_annual["anomaly"].rolling(10, center=True).mean()
df_plot = df_annual[(df_annual["year"] >= year_min) & (df_annual["year"] <= year_max)]

fig1 = go.Figure()
colours = [MD_RED if v >= 0 else MD_BLUE for v in df_plot["anomaly"]]
fig1.add_trace(go.Bar(
    x=df_plot["year"], y=df_plot["anomaly"],
    marker_color=colours, name="Annual anomaly",
    hovertemplate="%{x}: %{y:+.2f} °C<extra></extra>",
))
fig1.add_trace(go.Scatter(
    x=df_plot["year"], y=df_plot["rolling10"],
    mode="lines", name="10-year rolling mean",
    line=dict(color="black", width=2, dash="dot"),
))
fig1.add_hline(y=0, line_color="grey", line_width=1)
fig1.update_layout(
    template=PLOTLY_TEMPLATE,
    yaxis_title="Temperature anomaly (°C)",
    xaxis_title="Year",
    legend=dict(orientation="h", y=-0.15),
    margin=dict(l=40, r=20, t=30, b=60),
    title=f"Magdeburg Annual Temperature Anomaly vs 1961–1990 baseline ({baseline:.1f} °C)",
)
st.plotly_chart(fig1, use_container_width=True)
st.caption(f"Baseline (1961–1990 monthly mean): **{baseline:.2f} °C** · Data from 1834, showing years {year_min}–{year_max}")

st.divider()

# ── Chart 2: Precipitation heatmap ───────────────────────────────────────────
st.subheader("Monthly Precipitation Heatmap")
st.caption("Monthly precipitation totals (mm) — colour scale: white = dry, blue = wet")

n_years = st.selectbox("Show last N years", [20, 30, 50, "All"], index=0, key="prec_nyears")
df_prec = df[df["MO_RR"].notna()].copy()
if n_years != "All":
    max_year = int(df_prec["year"].max())
    df_prec = df_prec[df_prec["year"] >= max_year - int(n_years) + 1]

df_prec["month_name"] = df_prec["month"].map({v: k for k, v in MONTHS_DE.items()})
pivot = df_prec.pivot_table(index="year", columns="month_name", values="MO_RR", aggfunc="mean")
# Reorder months correctly
pivot = pivot.reindex(columns=[m for m in MONTHS_DE_ORDER if m in pivot.columns])

fig2 = heatmap(
    pivot,
    title="Monthly Precipitation (mm)",
    colorscale="Blues",
    zmin=0,
    x_label="Month",
    y_label="Year",
)
fig2.update_layout(margin=dict(l=50, r=20, t=50, b=40))
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Chart 3: Air pollutants ───────────────────────────────────────────────────
st.subheader("Air Pollutant Trends (Annual Monthly Data)")
st.caption("Source: KISS-MD / LüSA Messnetz Magdeburg · EU annual limit: NO₂ 40 µg/m³, PM₁₀ 40 µg/m³")

try:
    df_air = load_kiss("energie-und-umwelt/schadstoffkonzentration-in-der-luft.json")
    # After load_kiss the columns already carry their German labels; map to short display names
    df_air = df_air.rename(columns={
        "Stickstoffdioxid (NO₂)": "NO₂ (µg/m³)",
        "Ozon (O₃)": "O₃ (µg/m³)",
        "Schwefeldioxid (SO₂)": "SO₂ (µg/m³)",
        "Feinstaub (PM₁₀)": "PM₁₀ (µg/m³)",
    })

    poll_options = [c for c in ["NO₂ (µg/m³)", "O₃ (µg/m³)", "SO₂ (µg/m³)", "PM₁₀ (µg/m³)"] if c in df_air.columns]
    selected = st.multiselect("Pollutants to display", poll_options,
                              default=["NO₂ (µg/m³)", "PM₁₀ (µg/m³)"], key="pollutants")

    if selected:
        df_ann = df_air.groupby("Jahr")[selected].mean().reset_index()

        fig3 = go.Figure()
        colours3 = px.colors.qualitative.Set1
        for i, col in enumerate(selected):
            sub = df_ann[df_ann[col].notna()]
            fig3.add_trace(go.Scatter(
                x=sub["Jahr"], y=sub[col], mode="lines+markers",
                name=col, line=dict(color=colours3[i % len(colours3)]),
                hovertemplate=f"{col}: %{{y:.1f}} µg/m³<extra></extra>",
            ))

        # EU limit lines
        eu_limits = {"NO₂ (µg/m³)": 40, "PM₁₀ (µg/m³)": 40}
        for col, limit in eu_limits.items():
            if col in selected:
                fig3.add_hline(y=limit, line_dash="dash", line_color="grey",
                               annotation_text=f"EU limit {col}: {limit} µg/m³",
                               annotation_position="bottom right")

        fig3.update_layout(
            template=PLOTLY_TEMPLATE,
            yaxis_title="Concentration (µg/m³)",
            xaxis_title="Year",
            legend=dict(orientation="h", y=-0.2),
            margin=dict(l=40, r=20, t=30, b=70),
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Select at least one pollutant to display.")

except Exception as e:
    st.warning(f"Air quality data could not be loaded: {e}")
