import requests
import streamlit as st
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from collections import defaultdict
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


@st.cache_data(ttl=1800)
def fetch_weather_forecast() -> list:
    """Returns list of daily forecast dicts for the next 3 days from Bright Sky."""
    try:
        today = datetime.now().date()
        end   = today + timedelta(days=3)
        r = requests.get(
            "https://api.brightsky.dev/weather",
            params={"lat": LAT, "lon": LON,
                    "date": today.isoformat(),
                    "last_date": end.isoformat()},
            timeout=8,
        )
        r.raise_for_status()
        hours = r.json().get("weather", [])
        by_day = defaultdict(list)
        for h in hours:
            day = (h.get("timestamp") or "")[:10]
            if day:
                by_day[day].append(h)
        result = []
        for day_str in sorted(by_day.keys()):
            hs = by_day[day_str]
            temps = [h["temperature"] for h in hs if h.get("temperature") is not None]
            conds = [h.get("condition") or "" for h in hs if h.get("condition")]
            result.append({
                "date": day_str,
                "temp_max": max(temps) if temps else None,
                "temp_min": min(temps) if temps else None,
                "condition": max(set(conds), key=conds.count) if conds else "dry",
            })
        return result
    except Exception:
        return []


@st.cache_data(ttl=3600)
def fetch_city_news() -> list:
    """Tries Magdeburg city RSS feeds. Returns list of dicts or [] on failure."""
    feeds = [
        "https://www.magdeburg.de/RSS/",
        "https://www.magdeburg.de/rss.xml",
        "https://www.magdeburg.de/Start/B%C3%BCrger-Stadt/Newsroom/Pressemitteilungen?format=feed&type=rss",
    ]
    for url in feeds:
        try:
            r = requests.get(url, timeout=6,
                             headers={"User-Agent": "Mozilla/5.0 (compatible)"})
            if r.status_code != 200:
                continue
            root = ET.fromstring(r.content)
            channel = root.find("channel") or root
            items = []
            for item in channel.findall("item")[:5]:
                title = (item.findtext("title") or "").strip()
                link  = (item.findtext("link")  or "").strip()
                desc  = (item.findtext("description") or "").strip()
                pub   = (item.findtext("pubDate") or "")[:16].strip()
                if title:
                    items.append({"title": title[:90], "link": link,
                                  "summary": desc[:130] if desc else "", "date": pub})
            if items:
                return items
        except Exception:
            continue
    return []
