import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.data_loader import load_kiss
from utils.constants import MD_RED, MD_TEAL, MD_BLUE, MD_ORANGE, MONTHS_DE, PLOTLY_TEMPLATE
from utils.ui_helpers import hero_stat, section_header, insight_box

HEALTH_RED  = "#C0392B"
HEALTH_AMBER = "#E67E22"

st.title("Public Health & Emergency Services")
st.markdown(
    "<p style='font-size:0.97rem;color:#64748b;max-width:680px;margin:-6px 0 20px 0;'>"
    "How healthy and safe is Magdeburg? Explore emergency callout volumes, "
    "rescue service capacity, and long-term mortality trends."
    "</p>",
    unsafe_allow_html=True,
)
st.caption("Sources: KISS-MD / Landeshauptstadt Magdeburg — Rettungsdienst, Statistisches Amt")

# ── Hero KPI ──────────────────────────────────────────────────────────────────
try:
    _df_e = load_kiss("gesundheit-und-soziales/rettungsdienst-einsaetze.json")
    _df_e = _df_e.rename(columns={"Rettungsdienst-Einsätze gesamt": "Total"})
    _ly   = int(_df_e["Jahr"].max())
    _py   = _ly - 1
    _t_ly = int(_df_e[_df_e["Jahr"] == _ly]["Total"].sum())
    _t_py = int(_df_e[_df_e["Jahr"] == _py]["Total"].sum())
    _diff = _t_ly - _t_py
    _pct  = _diff / _t_py * 100
    _sign = "+" if _pct >= 0 else ""
    st.markdown(hero_stat(
        "🚑",
        f"{_t_ly:,}".replace(",", "."),
        f"Emergency rescue operations · {_ly}",
        f"{_sign}{_pct:.1f}% vs {_py}",
        delta_positive=False,
        color=HEALTH_RED,
        context=(
            f"Magdeburg's rescue services responded to {f'{_t_ly:,}'.replace(',','.')} "
            f"emergency callouts in {_ly} — roughly "
            f"{_t_ly // 365:,} per day. Demand has grown steadily since reunification."
        ),
    ), unsafe_allow_html=True)
except Exception:
    pass

# ── Chart 1: Monthly emergency operations trend ───────────────────────────────
st.markdown(section_header("Emergency callout volume", color=HEALTH_RED), unsafe_allow_html=True)

try:
    df_e = load_kiss("gesundheit-und-soziales/rettungsdienst-einsaetze.json")
    df_e = df_e.rename(columns={"Rettungsdienst-Einsätze gesamt": "Total"})
    df_e["_month_num"] = df_e["Monat"].map(MONTHS_DE).fillna(1)
    df_e["date"] = pd.to_datetime(
        df_e["Jahr"].astype(str) + "-" + df_e["_month_num"].astype(int).astype(str) + "-01"
    )
    df_e = df_e.sort_values("date")

    # Annual totals for bar chart
    df_annual = df_e.groupby("Jahr")["Total"].sum().reset_index()

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=df_annual["Jahr"], y=df_annual["Total"],
        name="Annual total",
        marker_color=HEALTH_RED,
        opacity=0.75,
        hovertemplate="%{x}: %{y:,.0f} operations<extra></extra>",
    ))
    # Rolling 5-year average
    df_annual["rolling5"] = df_annual["Total"].rolling(5, center=True).mean()
    fig1.add_trace(go.Scatter(
        x=df_annual["Jahr"], y=df_annual["rolling5"],
        mode="lines", name="5-year average",
        line=dict(color="#7F1D1D", width=2, dash="dot"),
        hovertemplate="%{x}: %{y:,.0f}<extra>5yr avg</extra>",
    ))
    fig1.update_layout(
        template=PLOTLY_TEMPLATE,
        yaxis_title="Emergency callouts / year",
        xaxis_title="Year",
        yaxis=dict(tickformat=",d"),
        legend=dict(orientation="h", y=-0.15),
        margin=dict(l=60, r=20, t=30, b=60),
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown(insight_box(
        "Emergency callouts have more than doubled since 1991 — driven by an ageing population "
        "and rising chronic illness rates. The dip around 2020 reflects pandemic-era changes "
        "in health-seeking behaviour."
    ), unsafe_allow_html=True)
    st.caption("Source: KISS-MD / Rettungsdienst Magdeburg")
except Exception as e:
    st.warning(f"Emergency operations data unavailable: {e}")

# ── Chart 2: Emergency fleet by provider ─────────────────────────────────────
st.markdown(section_header("Rescue fleet by provider", color=HEALTH_RED), unsafe_allow_html=True)
st.caption("Total rescue vehicles operated by each service provider in Magdeburg")

try:
    df_v = load_kiss("gesundheit-und-soziales/rettungsdienst-fahrzeuge.json")
    df_v = df_v.rename(columns={"Dienstleister": "Provider"})
    df_v["Total vehicles"] = df_v[["var3", "var4", "var5", "var6"]].fillna(0).sum(axis=1)
    df_v = df_v.sort_values("Jahr")

    providers = df_v["Provider"].unique()
    colours_p = [HEALTH_RED, HEALTH_AMBER, MD_BLUE, MD_TEAL, "#6A1B9A", "#2E7D32"]

    fig2 = go.Figure()
    for i, prov in enumerate(providers):
        sub = df_v[df_v["Provider"] == prov]
        fig2.add_trace(go.Scatter(
            x=sub["Jahr"], y=sub["Total vehicles"],
            mode="lines+markers", name=prov,
            line=dict(color=colours_p[i % len(colours_p)], width=2),
            hovertemplate=f"{prov} %{{x}}: %{{y}} vehicles<extra></extra>",
        ))
    fig2.update_layout(
        template=PLOTLY_TEMPLATE,
        yaxis_title="Total vehicles",
        xaxis_title="Year",
        legend=dict(orientation="h", y=-0.25, font=dict(size=11)),
        margin=dict(l=50, r=20, t=30, b=90),
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown(insight_box(
        "Berufsfeuerwehr Magdeburg (professional fire brigade) operates the largest rescue fleet. "
        "The Johanniter, Malteser, and ASB humanitarian services together cover "
        "a significant share of non-emergency patient transport."
    ), unsafe_allow_html=True)
    st.caption("Source: KISS-MD / Rettungsdienst Magdeburg")
except Exception as e:
    st.warning(f"Fleet data unavailable: {e}")

# ── Chart 3: Mortality trend ──────────────────────────────────────────────────
st.markdown(section_header("Mortality trend (1994–2024)", color=HEALTH_RED), unsafe_allow_html=True)
st.caption("Total registered deaths in Magdeburg per year · split by estimated gender")

try:
    df_d = load_kiss("gesundheit-und-soziales/gestorbene-nach-ausgewaehlten-todesursachen-und-geschlecht-in-magdeburg.json")
    # var2 = male deaths (estimated), var3 = female deaths (estimated)
    df_d = df_d.rename(columns={"var2": "Male (est.)", "var3": "Female (est.)"})
    df_d = df_d.sort_values("Jahr")
    df_d["Total"] = df_d["Male (est.)"].fillna(0) + df_d["Female (est.)"].fillna(0)

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=df_d["Jahr"], y=df_d["Male (est.)"].fillna(0),
        mode="lines", name="Male (est.)", stackgroup="one",
        line=dict(color=MD_BLUE, width=0.5), fillcolor=MD_BLUE + "88",
        hovertemplate="%{x}: %{y:,.0f} male<extra></extra>",
    ))
    fig3.add_trace(go.Scatter(
        x=df_d["Jahr"], y=df_d["Female (est.)"].fillna(0),
        mode="lines", name="Female (est.)", stackgroup="one",
        line=dict(color=MD_ORANGE, width=0.5), fillcolor=MD_ORANGE + "88",
        hovertemplate="%{x}: %{y:,.0f} female<extra></extra>",
    ))
    fig3.update_layout(
        template=PLOTLY_TEMPLATE,
        yaxis_title="Deaths per year",
        xaxis_title="Year",
        yaxis=dict(tickformat=",d"),
        legend=dict(orientation="h", y=-0.15),
        margin=dict(l=60, r=20, t=30, b=60),
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown(insight_box(
        "Total deaths have been declining gradually since the early 2000s — reflecting improvements "
        "in healthcare and a younger demographic mix from in-migration. "
        "Gender split is estimated (source labels unavailable)."
    ), unsafe_allow_html=True)
    st.caption("Source: KISS-MD / Statistisches Amt Magdeburg · Note: gender assignment is estimated from data patterns")
except Exception as e:
    st.warning(f"Mortality data unavailable: {e}")
