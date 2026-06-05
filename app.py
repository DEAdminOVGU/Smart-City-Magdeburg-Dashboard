
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Smart Magdeburg Dashboard", layout="wide")

LAT = 52.1205
LON = 11.6276

@st.cache_data(ttl=600)
def get_weather():
    return requests.get(
        f"https://api.brightsky.dev/current_weather?lat={LAT}&lon={LON}",
        timeout=10
    ).json()

@st.cache_data(ttl=600)
def get_air_quality():
    return requests.get(
        f"https://data.sensor.community/airrohr/v1/filter/area={LAT},{LON},10",
        timeout=20
    ).json()

@st.cache_data(ttl=600)
def get_water_level():
    return requests.get(
        "https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations/MAGDEBURG-STROMBR%C3%9CCKE/W/currentmeasurement.json",
        timeout=10
    ).json()

st.title("🏙️ Smart Magdeburg Dashboard")

c1, c2, c3 = st.columns(3)

try:
    weather = get_weather()["weather"]
    c1.metric("Temperature", f"{weather['temperature']} °C")
except Exception:
    c1.metric("Temperature", "N/A")

try:
    water = get_water_level()
    c2.metric("Elbe Level", f"{water['value']} cm")
except Exception:
    c2.metric("Elbe Level", "N/A")

try:
    air = get_air_quality()
    c3.metric("Air Sensors", len(air))
except Exception:
    c3.metric("Air Sensors", "N/A")

st.divider()

tab1, tab2, tab3 = st.tabs(["Weather", "Air Quality", "Water Level"])

with tab1:
    st.json(get_weather())

with tab2:
    st.write("Raw Sensor.Community data")
    st.json(get_air_quality()[:5] if get_air_quality() else [])

with tab3:
    st.json(get_water_level())

st.divider()
st.info("Next steps: add Folium map, Overpass POIs, GTFS data, and AI assistant.")
