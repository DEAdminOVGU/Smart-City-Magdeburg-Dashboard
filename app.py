import streamlit as st

st.set_page_config(
    page_title="Smart City Magdeburg",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

pages = {
    "Dashboard": [
        st.Page("pages/1_Home.py", title="Overview", icon="🏠"),
        st.Page("pages/2_Climate.py", title="Climate & Environment", icon="🌡️"),
        st.Page("pages/3_Population_Housing.py", title="Population & Housing", icon="🏘️"),
        st.Page("pages/4_Mobility.py", title="Mobility & Transport", icon="🚌"),
        st.Page("pages/5_Economy.py", title="Economy & Finance", icon="💶"),
    ]
}

pg = st.navigation(pages)
pg.run()
