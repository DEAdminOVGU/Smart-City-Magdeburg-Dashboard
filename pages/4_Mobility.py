import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.data_loader import load_kiss
from utils.constants import MD_TEAL, MD_ORANGE, MD_BLUE, MD_RED, MONTHS_DE, MONTHS_DE_ORDER, PLOTLY_TEMPLATE
from utils.chart_helpers import heatmap
from utils.ui_helpers import hero_stat

st.title("Mobility & Transport")
st.caption("Sources: KISS-MD / Kraftfahrtbundesamt, MVB GmbH & Co. KG, Landeshauptstadt Magdeburg")

# ── Hero KPI ──────────────────────────────────────────────────────────────────
try:
    _kfz    = load_kiss("verkehr/entwicklung-des-kraftfahrzeugbestandes-in-magdeburg.json")
    _kfz    = _kfz.sort_values("Jahr")
    _kly    = int(_kfz["Jahr"].max())
    _kpy    = _kly - 1
    _pkw_ly = float(_kfz[_kfz["Jahr"] == _kly]["var4"].values[0])
    _pkw_py = float(_kfz[_kfz["Jahr"] == _kpy]["var4"].values[0])
    _pop    = load_kiss("bevoelkerung/bevoelkerungsbestand-monatlich.json")
    _pop    = _pop.sort_values("Jahr")
    _p_ly   = float(_pop[_pop["Jahr"] == _kly]["var5"].mean())
    _p_py   = float(_pop[_pop["Jahr"] == _kpy]["var5"].mean())
    _cly    = round(_pkw_ly / _p_ly * 1000)
    _cpy    = round(_pkw_py / _p_py * 1000)
    _diff   = _cly - _cpy
    _sign   = "+" if _diff >= 0 else ""
    st.markdown(hero_stat(
        "🚗",
        str(_cly),
        f"Cars per 1,000 residents · {_kly}",
        f"{_sign}{_diff} vs {_kpy}",
        delta_positive=False,
        color="#6A1B9A",
    ), unsafe_allow_html=True)
except Exception:
    pass

# ── Chart 1: Vehicle fleet stacked area ──────────────────────────────────────
st.subheader("Vehicle Fleet Composition")

try:
    df_kfz = load_kiss("verkehr/entwicklung-des-kraftfahrzeugbestandes-in-magdeburg.json")
    # After load_kiss: "Kraftfahrzeugbestand gesamt", "Motorräder", "Transporter" already labeled;
    # var4 (PKW/cars) and var7 (trucks) have null labels and remain as var4/var7
    df_kfz = df_kfz.rename(columns={
        "Kraftfahrzeugbestand gesamt": "Gesamt",
        "var4": "PKW (Personenkraftwagen)",
        "var7": "LKW",
    })
    df_kfz = df_kfz.sort_values("Jahr")
    # "Other" = total minus known categories
    known = ["PKW (Personenkraftwagen)", "Motorräder", "LKW", "Transporter"]
    df_kfz["Sonstige"] = (
        df_kfz["Gesamt"]
        - df_kfz[["PKW (Personenkraftwagen)", "Motorräder", "LKW", "Transporter"]].fillna(0).sum(axis=1)
    ).clip(lower=0)

    fig1 = go.Figure()
    colours_fleet = [MD_BLUE, MD_TEAL, MD_RED, MD_ORANGE, "#888888"]
    segments = ["PKW (Personenkraftwagen)", "Motorräder", "LKW", "Transporter", "Sonstige"]
    for seg, col in zip(segments, colours_fleet):
        if seg in df_kfz.columns:
            fig1.add_trace(go.Scatter(
                x=df_kfz["Jahr"], y=df_kfz[seg].fillna(0),
                mode="lines", name=seg, stackgroup="one",
                line=dict(color=col, width=0.5),
                fillcolor=col,
                hovertemplate=f"{seg}: %{{y:,.0f}}<extra></extra>",
            ))

    fig1.update_layout(
        template=PLOTLY_TEMPLATE,
        yaxis_title="Registered vehicles",
        xaxis_title="Year",
        legend=dict(orientation="h", y=-0.2),
        margin=dict(l=60, r=20, t=30, b=80),
        yaxis=dict(tickformat=",d"),
    )
    st.plotly_chart(fig1, use_container_width=True)

    # KPI: cars per 1000 inhabitants
    try:
        pop_df = load_kiss("bevoelkerung/bevoelkerungsbestand-monatlich.json")
        latest_pop = int(pop_df["var5"].iloc[0])
        latest_cars = int(df_kfz["PKW (Personenkraftwagen)"].iloc[-1])
        cars_per_1000 = round(latest_cars / latest_pop * 1000)
        st.metric("🚗 Cars per 1,000 residents", str(cars_per_1000),
                  help=f"{latest_cars:,} PKW / {latest_pop:,} inhabitants")
    except Exception:
        pass

    st.caption("Source: KISS-MD / Kraftfahrtbundesamt · LKW = trucks, Transporter = vans")

except Exception as e:
    st.warning(f"Vehicle data unavailable: {e}")

st.divider()

# ── Chart 2: MVB ridership vs fleet ──────────────────────────────────────────
st.subheader("Public Transit vs. Private Vehicle Ownership")
st.caption("MVB = Magdeburger Verkehrsbetriebe · comparing transit ridership with private vehicle fleet growth")

try:
    df_mvb = load_kiss("verkehr/befoerderte-personen-der-magdeburger-verkehrsbetriebe-gmbh-und-co-kg.json")
    df_mvb = df_mvb.rename(columns={"var1": "Jahr", "var2": "MVB Fahrgäste"})
    df_mvb = df_mvb[["Jahr", "MVB Fahrgäste"]].dropna().sort_values("Jahr")

    df_kfz2 = load_kiss("verkehr/entwicklung-des-kraftfahrzeugbestandes-in-magdeburg.json")
    # "Kraftfahrzeugbestand gesamt" is the labeled column name after load_kiss
    df_kfz2 = df_kfz2.rename(columns={"Kraftfahrzeugbestand gesamt": "Kfz gesamt"})
    df_kfz2 = df_kfz2[["Jahr", "Kfz gesamt"]].sort_values("Jahr")

    # Merge on year
    merged = pd.merge(df_mvb, df_kfz2, on="Jahr", how="outer").sort_values("Jahr")

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=df_mvb["Jahr"], y=df_mvb["MVB Fahrgäste"],
        name="MVB Passengers (left)",
        marker_color=MD_TEAL,
        opacity=0.8,
        yaxis="y",
        hovertemplate="MVB %{x}: %{y:,.0f} passengers<extra></extra>",
    ))
    fig2.add_trace(go.Scatter(
        x=df_kfz2["Jahr"], y=df_kfz2["Kfz gesamt"],
        name="Registered vehicles (right)",
        mode="lines+markers",
        line=dict(color=MD_ORANGE, width=2),
        yaxis="y2",
        hovertemplate="Fleet %{x}: %{y:,.0f}<extra></extra>",
    ))
    fig2.update_layout(
        template=PLOTLY_TEMPLATE,
        yaxis=dict(title="MVB passengers / year", tickformat=",d"),
        yaxis2=dict(title="Registered vehicles", overlaying="y", side="right", tickformat=",d"),
        legend=dict(orientation="h", y=-0.2),
        margin=dict(l=70, r=80, t=30, b=80),
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("Source: KISS-MD / MVB GmbH & Co. KG · Kraftfahrtbundesamt")

except Exception as e:
    st.warning(f"Ridership data unavailable: {e}")

st.divider()

# ── Chart 3: Traffic accidents heatmap ───────────────────────────────────────
st.subheader("Traffic Accidents by Month & Year")
st.caption("Seasonal pattern of road accidents in Magdeburg · darker = more accidents")

try:
    df_acc = load_kiss("verkehr/verkehrsunfaelle-nach-monaten.json")
    # After load_kiss: Jahr, Monat already labeled; rename the accident count column
    df_acc = df_acc.rename(columns={"Straßenverkehrsunfälle": "Unfälle"})
    df_acc = df_acc[df_acc["Unfälle"].notna()]

    pivot = df_acc.pivot_table(index="Jahr", columns="Monat", values="Unfälle", aggfunc="sum")
    # Reorder months
    ordered_months = [m for m in MONTHS_DE_ORDER if m in pivot.columns]
    pivot = pivot.reindex(columns=ordered_months)

    fig3 = heatmap(
        pivot,
        title="Monthly Traffic Accidents",
        colorscale="YlOrRd",
        x_label="Month",
        y_label="Year",
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("Source: KISS-MD / Polizeidirektion Sachsen-Anhalt Nord")

except Exception as e:
    st.warning(f"Accident data unavailable: {e}")
