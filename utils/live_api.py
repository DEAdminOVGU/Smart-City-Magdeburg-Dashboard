import requests
import streamlit as st
from utils.constants import LAT, LON


@st.cache_data(ttl=600)
def fetch_weather() -> dict | None:
    try:
        r = requests.get(
            "https://api.brightsky.dev/current_weather",
            params={"lat": LAT, "lon": LON},
            timeout=5,
        )
        r.raise_for_status()
        return r.json().get("weather", {})
    except Exception:
        return None


@st.cache_data(ttl=600)
def fetch_elbe_level() -> dict | None:
    url = (
        "https://www.pegelonline.wsv.de/webservices/rest-api/v2"
        "/stations/MAGDEBURG-STROMBR%C3%9CCKE/W/currentmeasurement.json"
    )
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


@st.cache_data(ttl=600)
def fetch_air_quality() -> float | None:
    url = f"https://data.sensor.community/airrohr/v1/filter/area={LAT},{LON},10"
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        sensors = r.json()
        pm25_values = []
        for s in sensors:
            for sv in s.get("sensordatavalues", []):
                if sv.get("value_type") == "P2":
                    try:
                        pm25_values.append(float(sv["value"]))
                    except (ValueError, TypeError):
                        pass
        return round(sum(pm25_values) / len(pm25_values), 1) if pm25_values else None
    except Exception:
        return None
