import streamlit as st
from utils.ui_helpers import GLOBAL_CSS

st.set_page_config(
    page_title="Smart City Magdeburg",
    page_icon="utils/Wappen_Magdeburg.svg.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

pages = {
    "Dashboard": [
        st.Page("pages/1_Home.py",
                title="Home Page",               icon="🏠"),
        st.Page("pages/CityNav.py",
                title="City Navigation",         icon="🗺️",  url_path="navigation"),
        st.Page("pages/2_Climate.py",
                title="Climate & Environment",   icon="🌡️",  url_path="climate"),
        st.Page("pages/3_Population_Housing.py",
                title="Population & Housing",    icon="🏘️",  url_path="population"),
        st.Page("pages/5_Economy.py",
                title="Economy & Finance",       icon="💶",  url_path="economy"),
        st.Page("pages/6_Health.py",
                title="Health & Safety",         icon="🏥",  url_path="health"),
        st.Page("pages/7_Education.py",
                title="Education & Culture",     icon="🎓",  url_path="education"),
    ]
}

pg = st.navigation(pages, position="hidden")

# ── Horizontal top nav ────────────────────────────────────────────────────────
with st.container():
    st.markdown('<span class="nav-sentinel"></span>', unsafe_allow_html=True)

    brand_col, c1, c2, c3, c4, c5, c6, c7 = st.columns([2, 1, 1, 1, 1, 1, 1, 1])

    with brand_col:
        st.markdown("""
<div class="topnav-brand">
  <span class="brand-icon"></span>
  <div class="brand-text">
    <div class="brand-name">Magdeburg</div>
    <div class="brand-sub">Smart City Dashboard</div>
  </div>
</div>""", unsafe_allow_html=True)

    with c1: st.page_link("pages/1_Home.py",                label="Home Page",   icon="🏠")
    with c2: st.page_link("pages/CityNav.py",               label="Navigation",  icon="🗺️")
    with c3: st.page_link("pages/2_Climate.py",             label="Climate",     icon="🌡️")
    with c4: st.page_link("pages/3_Population_Housing.py",  label="Population",  icon="🏘️")
    with c5: st.page_link("pages/5_Economy.py",             label="Economy",     icon="💶")
    with c6: st.page_link("pages/6_Health.py",              label="Health",      icon="🏥")
    with c7: st.page_link("pages/7_Education.py",           label="Education",   icon="🎓")

pg.run()
