import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.data_loader import load_kiss
from utils.constants import MD_BLUE, MD_TEAL, MD_ORANGE, MD_RED, MONTHS_DE, PLOTLY_TEMPLATE
from utils.ui_helpers import hero_stat, section_header, insight_box

EDU_AMBER = "#F57F17"
EDU_DEEP  = "#E65100"

st.title("Education & Culture")
st.markdown(
    "<p style='font-size:0.97rem;color:#64748b;max-width:680px;margin:-6px 0 20px 0;'>"
    "Magdeburg as a university city — explore student enrollment trends, "
    "where students come from, library use, and the city's school landscape."
    "</p>",
    unsafe_allow_html=True,
)
st.caption("Sources: KISS-MD / Hochschulen Magdeburg, Stadtbibliothek, Statistisches Amt")

# ── Hero KPI ──────────────────────────────────────────────────────────────────
try:
    _df_s = load_kiss("bildung-und-kultur/anzahl-der-studierenden-im-wintersemester.json")
    # var2=Hochschule/Standort, var4=total students at that institution
    _df_s = _df_s.rename(columns={"Hochschule/Standort": "Institution", "var4": "Students"})
    _df_s = _df_s[_df_s["Students"].notna()]
    _ly   = int(_df_s["Jahr"].max())
    _py   = _ly - 1
    _t_ly = int(_df_s[_df_s["Jahr"] == _ly]["Students"].sum())
    _t_py = int(_df_s[_df_s["Jahr"] == _py]["Students"].sum())
    _diff = _t_ly - _t_py
    _pct  = _diff / _t_py * 100
    _sign = "+" if _pct >= 0 else ""
    st.markdown(hero_stat(
        "🎓",
        f"{_t_ly:,}".replace(",", "."),
        f"University students in Magdeburg · Winter {_ly}/{_ly+1}",
        f"{_sign}{_pct:.1f}% vs {_py}",
        delta_positive=_diff >= 0,
        color=EDU_AMBER,
        context=(
            f"Magdeburg's universities enrolled {f'{_t_ly:,}'.replace(',','.')} students "
            f"in the {_ly}/{_ly+1} winter semester. "
            "Otto-von-Guericke-Universität is the largest, with strong engineering and medical faculties."
        ),
    ), unsafe_allow_html=True)
except Exception:
    pass

# ── Chart 1: Enrollment by institution ───────────────────────────────────────
st.markdown(section_header("University enrollment trend", color=EDU_AMBER), unsafe_allow_html=True)

try:
    df_s = load_kiss("bildung-und-kultur/anzahl-der-studierenden-im-wintersemester.json")
    df_s = df_s.rename(columns={"Hochschule/Standort": "Institution", "var4": "Students"})
    df_s = df_s[df_s["Students"].notna()].sort_values("Jahr")

    institutions = df_s["Institution"].unique()
    colours_i = [MD_BLUE, EDU_AMBER, MD_TEAL, MD_RED, "#6A1B9A", "#888"]

    fig1 = go.Figure()
    for i, inst in enumerate(institutions):
        sub = df_s[df_s["Institution"] == inst].groupby("Jahr")["Students"].sum().reset_index()
        # Clean up long institution names
        short = (inst.replace("Otto-von-Guericke-Universität", "OVGU")
                    .replace("Hochschule Magdeburg-Stendal", "HS Magdeburg-Stendal")
                    .replace(" - Standort", "–")
                    .replace("Standort", ""))
        fig1.add_trace(go.Scatter(
            x=sub["Jahr"], y=sub["Students"],
            mode="lines+markers", name=short,
            stackgroup="one",
            line=dict(color=colours_i[i % len(colours_i)], width=0.5),
            fillcolor=colours_i[i % len(colours_i)] + "99",
            hovertemplate=f"{short} %{{x}}: %{{y:,.0f}} students<extra></extra>",
        ))
    fig1.update_layout(
        template=PLOTLY_TEMPLATE,
        yaxis_title="Students enrolled",
        xaxis_title="Winter semester year",
        yaxis=dict(tickformat=",d"),
        legend=dict(orientation="h", y=-0.2, font=dict(size=11)),
        margin=dict(l=60, r=20, t=30, b=80),
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown(insight_box(
        "Total enrollment peaked around 2012–2015 and has been gradually declining — "
        "a pattern seen across many eastern German universities as demographics shift. "
        "International student numbers have partially offset the decline."
    ), unsafe_allow_html=True)
    st.caption("Source: KISS-MD / Statistische Ämter · Winter semester data")
except Exception as e:
    st.warning(f"Enrollment data unavailable: {e}")

# ── Chart 2: Student origin breakdown ────────────────────────────────────────
st.markdown(section_header("Where students come from", color=EDU_AMBER), unsafe_allow_html=True)
st.caption("OVGU — student origin by home region (2014 onwards)")

try:
    df_h = load_kiss("bildung-und-kultur/anzahl-der-studierenden-nach-herkunft.json")
    df_h = df_h.rename(columns={
        "Hochschule": "University",
        "Herkunftsgebiet": "Origin",
        "var4": "Total",
    })
    df_h = df_h[df_h["Total"].notna()]

    # Filter to OVGU for consistency
    df_ovgu = df_h[df_h["University"].str.contains("Guericke", na=False)]

    # Shorten origin labels
    origin_map = {
        "Sachsen-Anhalt": "Saxony-Anhalt",
        "Deutsche Staatsbürgerschaft außerhalb Sachsen-Anhalt": "Other German states",
        "Ausländische Staatsbürgerschaft": "International",
        "Ohne Angabe": "Not stated",
    }
    df_ovgu = df_ovgu.copy()
    df_ovgu["Origin"] = df_ovgu["Origin"].map(lambda x: origin_map.get(x, x))

    years = sorted(df_ovgu["Jahr"].unique())
    origins = df_ovgu["Origin"].unique()
    colours_o = [MD_BLUE, MD_TEAL, EDU_AMBER, "#888"]

    fig2 = go.Figure()
    for i, origin in enumerate(origins):
        sub = df_ovgu[df_ovgu["Origin"] == origin].sort_values("Jahr")
        fig2.add_trace(go.Bar(
            x=sub["Jahr"], y=sub["Total"],
            name=origin,
            marker_color=colours_o[i % len(colours_o)],
            hovertemplate=f"{origin} %{{x}}: %{{y:,.0f}}<extra></extra>",
        ))
    fig2.update_layout(
        template=PLOTLY_TEMPLATE,
        barmode="stack",
        yaxis_title="Students",
        xaxis_title="Winter semester year",
        yaxis=dict(tickformat=",d"),
        legend=dict(orientation="h", y=-0.15),
        margin=dict(l=60, r=20, t=30, b=60),
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown(insight_box(
        "International students now make up a growing share of OVGU enrollment — "
        "partly due to strong engineering and computer science programmes with global recognition. "
        "Students from other German states consistently outnumber locals from Saxony-Anhalt."
    ), unsafe_allow_html=True)
    st.caption("Source: KISS-MD / OVGU · Otto-von-Guericke-Universität Magdeburg")
except Exception as e:
    st.warning(f"Student origin data unavailable: {e}")

# ── Chart 3: Library loans & visitors ────────────────────────────────────────
st.markdown(section_header("City library — visitors & loans", color=EDU_AMBER), unsafe_allow_html=True)
st.caption("Stadtbibliothek Magdeburg · monthly loans and visitor counts 1990–2018")

try:
    df_lib = load_kiss("bildung-und-kultur/monatliche-besuchszahlen-bestaende-und-entleihungen.json")
    df_lib = df_lib.rename(columns={
        "Besucher": "Visitors",
        "Entleihungen gesamt": "Loans",
        "Medienbestand": "Media inventory",
    })
    df_lib["_month_num"] = df_lib["Monat"].map(MONTHS_DE).fillna(1)
    df_lib["date"] = pd.to_datetime(
        df_lib["Jahr"].astype(str) + "-" + df_lib["_month_num"].astype(int).astype(str) + "-01"
    )
    df_lib = df_lib.sort_values("date")

    # Annual totals
    df_lib_annual = df_lib.groupby("Jahr").agg(
        Visitors=("Visitors", "sum"),
        Loans=("Loans", "sum"),
    ).reset_index()
    df_lib_annual = df_lib_annual[(df_lib_annual["Visitors"] > 0) | (df_lib_annual["Loans"] > 0)]

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=df_lib_annual["Jahr"], y=df_lib_annual["Visitors"],
        name="Visitors (left)",
        marker_color=EDU_AMBER, opacity=0.8,
        yaxis="y",
        hovertemplate="%{x}: %{y:,.0f} visitors<extra></extra>",
    ))
    fig3.add_trace(go.Scatter(
        x=df_lib_annual["Jahr"], y=df_lib_annual["Loans"],
        mode="lines+markers", name="Loans (right)",
        line=dict(color=MD_BLUE, width=2),
        yaxis="y2",
        hovertemplate="%{x}: %{y:,.0f} loans<extra></extra>",
    ))
    fig3.update_layout(
        template=PLOTLY_TEMPLATE,
        yaxis=dict(title="Visitors / year", tickformat=",d"),
        yaxis2=dict(title="Items loaned / year", overlaying="y", side="right", tickformat=",d"),
        legend=dict(orientation="h", y=-0.15),
        margin=dict(l=60, r=80, t=30, b=60),
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown(insight_box(
        "Library loans have been declining since the mid-2000s — mirroring national trends "
        "as digital media replaced physical borrowing. Visitor counts held up longer, "
        "suggesting libraries remain valued community spaces even as lending falls."
    ), unsafe_allow_html=True)
    st.caption("Source: KISS-MD / Stadtbibliothek Magdeburg · Data available through 2018")
except Exception as e:
    st.warning(f"Library data unavailable: {e}")

# ── Chart 4: Schools by type ──────────────────────────────────────────────────
st.markdown(section_header("Schools by type", color=EDU_AMBER), unsafe_allow_html=True)
st.caption("Number of schools in Magdeburg by school type and year")

try:
    df_sch = load_kiss("bildung-und-kultur/schulen-in-der-stadt-magdeburg.json")
    df_sch = df_sch.rename(columns={"Schultyp": "Type", "Schulartgruppe": "Group"})
    df_sch = df_sch[df_sch["Type"].notna()]

    years_sch = sorted(df_sch["Jahr"].dropna().unique())
    sel_year_sch = st.selectbox("Year", [int(y) for y in years_sch[::-1]], key="sch_year")
    df_y_sch = df_sch[df_sch["Jahr"] == sel_year_sch]

    counts = df_y_sch.groupby("Type").size().reset_index(name="Count").sort_values("Count", ascending=True)

    colours_sch = [MD_BLUE, MD_TEAL, EDU_AMBER, MD_RED, "#6A1B9A", "#2E7D32",
                   "#888", "#004B87", "#C0392B", "#F39C12"]

    fig4 = go.Figure(go.Bar(
        y=counts["Type"], x=counts["Count"],
        orientation="h",
        marker_color=[colours_sch[i % len(colours_sch)] for i in range(len(counts))],
        text=counts["Count"].astype(str),
        textposition="outside",
        hovertemplate="%{y}: %{x} schools<extra></extra>",
    ))
    fig4.update_layout(
        template=PLOTLY_TEMPLATE,
        xaxis_title="Number of schools",
        yaxis_title="",
        height=max(380, len(counts) * 34),
        margin=dict(l=160, r=60, t=30, b=40),
    )
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown(insight_box(
        "Grundschulen (primary schools) form the largest group. Magdeburg maintains a diverse "
        "range of school types including Sekundarschulen, Gymnasien, and specialist schools — "
        "reflecting the comprehensive German state school system."
    ), unsafe_allow_html=True)
    st.caption("Source: KISS-MD / Schulamt Magdeburg")
except Exception as e:
    st.warning(f"School data unavailable: {e}")
