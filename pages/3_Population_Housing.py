import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from utils.data_loader import load_kiss, load_mietspiegel
from utils.constants import MONTHS_DE, MD_TEAL, MD_ORANGE, MD_BLUE, MD_RED, PLOTLY_TEMPLATE
from utils.ui_helpers import hero_stat

st.title("Population & Housing")
st.caption("Sources: KISS-MD / Einwohnermeldeamt Magdeburg · Mietspiegel Magdeburg 2024")

# ── Hero KPI ──────────────────────────────────────────────────────────────────
try:
    _df_p  = load_kiss("bevoelkerung/bevoelkerungsbestand-monatlich.json")
    _df_p  = _df_p.sort_values("Jahr")
    _cy    = int(_df_p["Jahr"].max())
    _py    = _cy - 1
    _cp    = int(_df_p[_df_p["Jahr"] == _cy]["var5"].mean())
    _pp    = int(_df_p[_df_p["Jahr"] == _py]["var5"].mean())
    _delta = _cp - _pp
    _sign  = "+" if _delta >= 0 else ""
    st.markdown(hero_stat(
        "👥",
        f"{_cp:,}".replace(",", "."),
        f"Residents with primary registration (Hauptwohnsitz) · {_cy}",
        f"{_sign}{_delta:,} vs {_py}".replace(",", "."),
        delta_positive=_delta >= 0,
        color="#1565C0",
    ), unsafe_allow_html=True)
except Exception:
    pass

# ── Chart 1: Population time series ──────────────────────────────────────────
st.subheader("Population Development")

try:
    df_pop = load_kiss("bevoelkerung/bevoelkerungsbestand-monatlich.json")
    # var1=Jahr, var2=Monat, var5=total Hauptwohnsitz, var8=foreign total
    df_pop = df_pop.rename(columns={
        "var1": "Jahr", "var2": "Monat",
        "var5": "Gesamt", "var8": "Ausländer",
    })
    df_pop["_month_num"] = df_pop["Monat"].map(MONTHS_DE).fillna(1)
    df_pop["date"] = pd.to_datetime(
        df_pop["Jahr"].astype(str) + "-" + df_pop["_month_num"].astype(int).astype(str) + "-01"
    )
    df_pop = df_pop.sort_values("date")
    df_pop["Deutsche"] = df_pop["Gesamt"] - df_pop["Ausländer"].fillna(0)

    year_range = st.slider(
        "Year range", int(df_pop["Jahr"].min()), int(df_pop["Jahr"].max()),
        value=(2000, int(df_pop["Jahr"].max())), key="pop_years",
    )
    mask = (df_pop["Jahr"] >= year_range[0]) & (df_pop["Jahr"] <= year_range[1])
    df_plot = df_pop[mask]

    show_breakdown = st.checkbox("Show German / foreign breakdown", value=True, key="pop_breakdown")

    fig1 = go.Figure()
    if show_breakdown:
        fig1.add_trace(go.Scatter(
            x=df_plot["date"], y=df_plot["Deutsche"],
            mode="lines", name="German residents",
            stackgroup="one", line=dict(color=MD_BLUE),
            hovertemplate="%{x|%b %Y}: %{y:,.0f}<extra>German</extra>",
        ))
        fig1.add_trace(go.Scatter(
            x=df_plot["date"], y=df_plot["Ausländer"],
            mode="lines", name="Foreign residents",
            stackgroup="one", line=dict(color=MD_ORANGE),
            hovertemplate="%{x|%b %Y}: %{y:,.0f}<extra>Foreign</extra>",
        ))
    else:
        fig1.add_trace(go.Scatter(
            x=df_plot["date"], y=df_plot["Gesamt"],
            mode="lines", name="Total population",
            line=dict(color=MD_TEAL, width=2),
            hovertemplate="%{x|%b %Y}: %{y:,.0f}<extra></extra>",
        ))

    fig1.update_layout(
        template=PLOTLY_TEMPLATE,
        yaxis_title="Residents (Hauptwohnsitz)",
        xaxis_title="",
        legend=dict(orientation="h", y=-0.15),
        margin=dict(l=60, r=20, t=30, b=60),
        yaxis=dict(tickformat=",d"),
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.caption("Hauptwohnsitz (primary residence) · Source: KISS-MD / Einwohnermeldeamt")

except Exception as e:
    st.warning(f"Population data unavailable: {e}")

st.divider()

# ── Chart 2: Rent by district ─────────────────────────────────────────────────
st.subheader("Rental Prices by District (Mietspiegel)")

try:
    df_rent = load_mietspiegel("wohnflaeche")

    years = sorted(df_rent["year"].unique())
    area_classes = sorted(df_rent["wohnflaechenklasse"].unique())

    col_a, col_b = st.columns(2)
    with col_a:
        sel_year = st.selectbox("Year", years[::-1], key="rent_year")
    with col_b:
        sel_area = st.selectbox("Apartment size", area_classes, index=1, key="rent_area")

    df_r = df_rent[(df_rent["year"] == sel_year) & (df_rent["wohnflaechenklasse"] == sel_area)]
    df_r = df_r.sort_values("nettokaltmiete_pro_qm", ascending=True)

    def rent_colour(v):
        if v < 6:
            return MD_TEAL
        elif v < 8:
            return MD_ORANGE
        return MD_RED

    bar_colours = [rent_colour(v) for v in df_r["nettokaltmiete_pro_qm"]]

    fig2 = go.Figure(go.Bar(
        y=df_r["stadtteil"],
        x=df_r["nettokaltmiete_pro_qm"],
        orientation="h",
        marker_color=bar_colours,
        text=df_r["nettokaltmiete_pro_qm"].map(lambda v: f"€{v:.2f}"),
        textposition="outside",
        hovertemplate="%{y}: €%{x:.2f}/m²<extra></extra>",
    ))
    fig2.update_layout(
        template=PLOTLY_TEMPLATE,
        title=f"Net cold rent per m² · {sel_area} · {sel_year}",
        xaxis_title="€/m²",
        yaxis_title="",
        height=max(400, len(df_r) * 22),
        margin=dict(l=160, r=80, t=50, b=40),
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption(
        "Nettokaltmiete · Colours: teal < €6/m², amber €6–8/m², red > €8/m² · "
        "Districts with insufficient sample size excluded · Source: Mietspiegel Magdeburg 2024"
    )

    # Trend line for selected district
    st.markdown("**Rent trend for a specific district (2012–2026)**")
    districts = sorted(df_rent["stadtteil"].unique())
    sel_district = st.selectbox("District", districts, key="rent_district")
    df_trend = df_rent[(df_rent["stadtteil"] == sel_district) & (df_rent["wohnflaechenklasse"] == sel_area)]

    if not df_trend.empty:
        fig2b = go.Figure(go.Scatter(
            x=df_trend["year"], y=df_trend["nettokaltmiete_pro_qm"],
            mode="lines+markers", line=dict(color=MD_TEAL),
            hovertemplate="%{x}: €%{y:.2f}/m²<extra></extra>",
        ))
        fig2b.update_layout(
            template=PLOTLY_TEMPLATE,
            title=f"Rent trend — {sel_district} ({sel_area})",
            xaxis_title="Year",
            yaxis_title="€/m²",
            margin=dict(l=60, r=20, t=50, b=40),
        )
        st.plotly_chart(fig2b, use_container_width=True)

except Exception as e:
    st.warning(f"Rental data unavailable: {e}")

st.divider()

# ── Chart 3: Housing vacancy ──────────────────────────────────────────────────
st.subheader("Housing Vacancy Rate")
st.caption("Leerstand im Geschosswohnungsbau (multi-storey housing) — city-wide weighted mean")

try:
    df_leer = load_kiss("bautaetigkeit-und-wohnen/leerstand-im-geschosswohnungsbau.json")
    # Columns already labeled by load_kiss
    df_leer = df_leer.rename(columns={
        "Geschosswohnungen gesamt": "Gesamt",
        "Leerstehende Geschosswohnungen": "Leerstand",
    })
    df_leer = df_leer[df_leer["Leerstandsquote"].notna()]
    # Weighted mean by total apartments
    df_city = df_leer.groupby("Jahr").apply(
        lambda g: (g["Leerstand"].sum() / g["Gesamt"].sum() * 100) if g["Gesamt"].sum() > 0 else None
    ).reset_index(name="Leerstandsquote_gewichtet")

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=df_city["Jahr"], y=df_city["Leerstandsquote_gewichtet"],
        mode="lines+markers", fill="tozeroy",
        line=dict(color=MD_ORANGE), fillcolor="rgba(232,119,34,0.15)",
        hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
        name="Vacancy rate",
    ))
    peak_row = df_city.loc[df_city["Leerstandsquote_gewichtet"].idxmax()]
    fig3.add_annotation(
        x=peak_row["Jahr"], y=peak_row["Leerstandsquote_gewichtet"],
        text=f"Peak: {peak_row['Leerstandsquote_gewichtet']:.1f}% ({int(peak_row['Jahr'])})",
        showarrow=True, arrowhead=2, ax=40, ay=-30,
    )
    fig3.update_layout(
        template=PLOTLY_TEMPLATE,
        yaxis_title="Vacancy rate (%)",
        xaxis_title="Year",
        margin=dict(l=50, r=20, t=30, b=40),
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("Source: KISS-MD / Wohnungsmarktbericht Magdeburg · Stadtteil-Nr codes per KISS-MD")

except Exception as e:
    st.warning(f"Vacancy data unavailable: {e}")
