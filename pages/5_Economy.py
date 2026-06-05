import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.data_loader import load_kiss, load_steuereinnahmen
from utils.constants import MD_TEAL, MD_ORANGE, MD_BLUE, MD_RED, MD_GREY, PLOTLY_TEMPLATE
from utils.ui_helpers import hero_stat

st.title("Economy & Finance")
st.caption("Sources: Landeshauptstadt Magdeburg (Steuerstatistik) · KISS-MD / Statistisches Amt")

# ── Hero KPI ──────────────────────────────────────────────────────────────────
try:
    _tax    = load_steuereinnahmen()
    _cols   = ["gewerbesteuer", "gemeindeanteil-an-der-einkommensteuer",
               "grundsteuer_b", "gemeindeanteil-an-der-umsatzsteuer"]
    _t24    = sum(float(_tax[_tax["jahr"] == 2024].iloc[0].get(c, 0) or 0) for c in _cols)
    _t23    = sum(float(_tax[_tax["jahr"] == 2023].iloc[0].get(c, 0) or 0) for c in _cols)
    _pct    = (_t24 - _t23) / _t23 * 100
    _sign   = "+" if _pct >= 0 else ""
    st.markdown(hero_stat(
        "💶",
        f"€{_t24/1e6:.0f}M",
        "Total municipal tax revenue · 2024",
        f"{_sign}{_pct:.1f}% vs 2023",
        delta_positive=_pct >= 0,
        color="#2E7D32",
    ), unsafe_allow_html=True)
except Exception:
    pass

# ── Chart 1: Tax revenue ──────────────────────────────────────────────────────
st.subheader("Municipal Tax Revenue")

try:
    df_tax = load_steuereinnahmen()

    tax_cols = {
        "gewerbesteuer": "Gewerbesteuer",
        "gemeindeanteil-an-der-einkommensteuer": "Einkommensteuer (Gem.anteil)",
        "grundsteuer_b": "Grundsteuer B",
        "gemeindeanteil-an-der-umsatzsteuer": "Umsatzsteuer (Gem.anteil)",
        "hundesteuer": "Hundesteuer",
    }
    available = {k: v for k, v in tax_cols.items() if k in df_tax.columns}
    df_tax_plot = df_tax.sort_values("jahr")

    selected_taxes = st.multiselect(
        "Tax types to display",
        list(available.values()),
        default=[v for k, v in available.items() if k != "hundesteuer"],
        key="tax_types",
    )
    reverse_map = {v: k for k, v in available.items()}
    sel_keys = [reverse_map[t] for t in selected_taxes if t in reverse_map]

    colours_tax = [MD_BLUE, MD_TEAL, MD_ORANGE, MD_RED, MD_GREY]
    fig1 = go.Figure()
    for i, (key, label) in enumerate([(k, v) for k, v in available.items() if k in sel_keys]):
        vals = df_tax_plot[key].fillna(0) / 1e6
        fig1.add_trace(go.Bar(
            x=df_tax_plot["jahr"], y=vals,
            name=label,
            marker_color=colours_tax[i % len(colours_tax)],
            hovertemplate=f"{label}: €%{{y:.1f}} M<extra></extra>",
        ))

    fig1.update_layout(
        template=PLOTLY_TEMPLATE,
        barmode="group",
        yaxis_title="Revenue (€ million)",
        xaxis_title="Year",
        legend=dict(orientation="h", y=-0.2),
        margin=dict(l=60, r=20, t=30, b=80),
        xaxis=dict(dtick=1),
    )
    st.plotly_chart(fig1, use_container_width=True)

    # KPI cards
    try:
        y2024 = df_tax[df_tax["jahr"] == 2024].iloc[0]
        y2023 = df_tax[df_tax["jahr"] == 2023].iloc[0]
        total_2024 = sum(float(y2024.get(k, 0) or 0) for k in available)
        total_2023 = sum(float(y2023.get(k, 0) or 0) for k in available)
        pct_change = (total_2024 - total_2023) / total_2023 * 100 if total_2023 else None
        gew_share = float(y2024.get("gewerbesteuer", 0) or 0) / total_2024 * 100 if total_2024 else None

        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("Total Revenue 2024", f"€{total_2024/1e6:.0f} M",
                      delta=f"{pct_change:+.1f}% vs 2023" if pct_change else None)
        with k2:
            st.metric("Gewerbesteuer 2024", f"€{float(y2024.get('gewerbesteuer', 0) or 0)/1e6:.0f} M")
        with k3:
            st.metric("Gewerbesteuer share", f"{gew_share:.0f}%" if gew_share else "—")
    except Exception:
        pass

    st.caption("Source: Landeshauptstadt Magdeburg — Steuerstatistik · Grundsteuer B: coalesced across 2024/2025 reform split")

except Exception as e:
    st.warning(f"Tax data unavailable: {e}")

st.divider()

# ── Chart 2: Business registrations / deregistrations ────────────────────────
st.subheader("Business Registrations & Deregistrations")
st.caption("Net balance of new business filings in Magdeburg")

try:
    df_biz = load_kiss("wirtschaft/gewerbean-und-abmeldungen-am-jahresende.json")
    # After load_kiss: "Gewerbeanmeldungen", "Gewerbeabmeldungen" already labeled; var4 is net balance
    df_biz = df_biz.rename(columns={"var4": "Nettobestand"})
    df_biz = df_biz.sort_values("Jahr")

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=df_biz["Jahr"], y=df_biz["Gewerbeanmeldungen"],
        name="Registrations",
        marker_color=MD_TEAL,
        hovertemplate="Registrations %{x}: %{y:,}<extra></extra>",
    ))
    fig2.add_trace(go.Bar(
        x=df_biz["Jahr"], y=-df_biz["Gewerbeabmeldungen"],
        name="Deregistrations",
        marker_color=MD_RED,
        hovertemplate="Deregistrations %{x}: %{y:,}<extra></extra>",
    ))
    fig2.add_trace(go.Scatter(
        x=df_biz["Jahr"], y=df_biz["Nettobestand"],
        mode="lines+markers", name="Net balance",
        line=dict(color="black", width=2, dash="dot"),
        hovertemplate="Net %{x}: %{y:+,}<extra></extra>",
    ))
    fig2.add_hline(y=0, line_color="grey", line_width=1)
    fig2.update_layout(
        template=PLOTLY_TEMPLATE,
        barmode="overlay",
        yaxis_title="Number of businesses",
        xaxis_title="Year",
        legend=dict(orientation="h", y=-0.2),
        margin=dict(l=60, r=20, t=30, b=80),
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("Source: KISS-MD / Ordnungsamt Magdeburg")

except Exception as e:
    st.warning(f"Business data unavailable: {e}")

st.divider()

# ── Chart 3: Employment by sector ─────────────────────────────────────────────
st.subheader("Employment by Economic Sector")
st.caption("Sozialversicherungspflichtig Beschäftigte am Arbeitsort (insured employees)")

try:
    df_emp = load_kiss(
        "arbeitsmarkt/sozialversicherungspflichtig-beschaeftigte-am-arbeitsort-je-wirtschaftsabschnitt-wz-2008-nach-geschlecht.json"
    )
    # After load_kiss: "Wirtschaftsabschnitt (WZ 2008)", "Männlich Beschäftigte", "Weiblich Beschäftigte" already labeled
    df_emp = df_emp.rename(columns={
        "Wirtschaftsabschnitt (WZ 2008)": "Sektor",
        "Männlich Beschäftigte": "Männlich",
        "Weiblich Beschäftigte": "Weiblich",
    })
    df_emp = df_emp[df_emp["Sektor"].notna()]
    df_emp["Gesamt"] = df_emp["Männlich"].fillna(0) + df_emp["Weiblich"].fillna(0)

    years_emp = sorted(df_emp["Jahr"].dropna().unique())
    sel_year_emp = st.selectbox("Year", [int(y) for y in years_emp[::-1]], key="emp_year")

    df_y = df_emp[df_emp["Jahr"] == sel_year_emp].copy()
    # Shorten sector labels
    def shorten(s):
        if "(" in s and ")" in s:
            return s[s.rfind("(")+1 : s.rfind(")")]  # extract WZ code
        return s[:40]

    df_y["Sektor_kurz"] = df_y["Sektor"].apply(shorten)
    df_y = df_y.sort_values("Gesamt", ascending=True)

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        y=df_y["Sektor_kurz"], x=df_y["Weiblich"].fillna(0),
        orientation="h", name="Female", marker_color=MD_ORANGE,
        hovertemplate="%{y}: %{x:,} female<extra></extra>",
    ))
    fig3.add_trace(go.Bar(
        y=df_y["Sektor_kurz"], x=df_y["Männlich"].fillna(0),
        orientation="h", name="Male", marker_color=MD_BLUE,
        hovertemplate="%{y}: %{x:,} male<extra></extra>",
    ))
    fig3.update_layout(
        template=PLOTLY_TEMPLATE,
        barmode="stack",
        xaxis_title="Insured employees",
        yaxis_title="",
        legend=dict(orientation="h", y=-0.1),
        height=max(450, len(df_y) * 28),
        margin=dict(l=50, r=20, t=30, b=60),
        xaxis=dict(tickformat=",d"),
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.caption(
        f"Year: {sel_year_emp} · WZ 2008 sector codes · "
        "Source: KISS-MD / Bundesagentur für Arbeit"
    )

except Exception as e:
    st.warning(f"Employment data unavailable: {e}")
