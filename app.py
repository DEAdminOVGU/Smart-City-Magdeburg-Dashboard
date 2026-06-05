import streamlit as st
from utils.ui_helpers import GLOBAL_CSS

st.set_page_config(
    page_title="Smart City Magdeburg",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

pages = {
    "Dashboard": [
        st.Page("pages/1_Home.py", title="Overview",                icon="🏠"),
        st.Page("pages/2_Climate.py", title="Climate & Environment", icon="🌡️"),
        st.Page("pages/3_Population_Housing.py", title="Population & Housing", icon="🏘️"),
        st.Page("pages/4_Mobility.py", title="Mobility & Transport", icon="🚌"),
        st.Page("pages/5_Economy.py", title="Economy & Finance",     icon="💶"),
    ]
}

pg = st.navigation(pages, position="hidden")  # routing only — nav UI below

# ── Custom sidebar tile navigation ────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div style="padding:20px 20px 14px;border-bottom:1px solid #eef0f2;margin-bottom:6px;">
  <div style="font-size:1.5rem;font-weight:900;color:#007A6E;
              letter-spacing:-0.03em;line-height:1;">Magdeburg</div>
  <div style="font-size:0.68rem;color:#aaa;text-transform:uppercase;
              letter-spacing:0.15em;margin-top:3px;font-weight:600;">Smart City Dashboard</div>
</div>
<div style="padding:6px 0 4px 20px;font-size:0.65rem;font-weight:800;color:#ccc;
            text-transform:uppercase;letter-spacing:0.15em;margin-bottom:2px;">Topics</div>
""", unsafe_allow_html=True)

    st.page_link("pages/1_Home.py",
                 label="Overview",             icon="🏠")
    st.page_link("pages/2_Climate.py",
                 label="Climate & Environment", icon="🌡️")
    st.page_link("pages/3_Population_Housing.py",
                 label="Population & Housing",  icon="🏘️")
    st.page_link("pages/4_Mobility.py",
                 label="Mobility & Transport",  icon="🚌")
    st.page_link("pages/5_Economy.py",
                 label="Economy & Finance",     icon="💶")

    st.markdown('<div class="sidebar-sep"></div>', unsafe_allow_html=True)

pg.run()
