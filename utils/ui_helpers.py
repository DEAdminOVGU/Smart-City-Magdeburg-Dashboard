"""Shared HTML components for the Smart City Magdeburg Dashboard."""

from pathlib import Path


def _load_global_css() -> str:
    css_path = Path(__file__).resolve().parents[1] / "assets" / "theme.css"
    return f"<style>{css_path.read_text(encoding='utf-8')}</style>"


def hero_stat(icon: str, value: str, description: str,
              delta_text: str, delta_positive: bool,
              color: str = "#007A6E") -> str:
    """Bold hero KPI block shown at the top of each page."""
    arrow = "↑" if delta_positive else "↓"
    delta_color = "#1B5E20" if delta_positive else "#B71C1C"
    delta_bg = "#E8F5E9" if delta_positive else "#FFEBEE"
    return f"""
<div class="theme-card hero-card" style="--accent:{color};">
    <div class="hero-card__icon">{icon}</div>
    <div class="hero-card__value">{value}</div>
    <div class="hero-card__description">{description}</div>
    <div class="hero-card__delta" style="--delta-bg:{delta_bg};--delta-fg:{delta_color};">{arrow}&nbsp;{delta_text}</div>
</div>
"""


def topic_card(icon: str, title: str, value: str, unit: str,
               delta_text: str, delta_positive: bool,
               year: str, color: str = "#007A6E") -> str:
    """Topic card for the Home page grid."""
    arrow = "↑" if delta_positive else "↓"
    delta_color = "#1B5E20" if delta_positive else "#B71C1C"
    delta_bg = "#E8F5E9" if delta_positive else "#FFEBEE"
    return f"""
<div class="theme-card topic-card" style="--accent:{color};--delta-bg:{delta_bg};--delta-fg:{delta_color};">
    <div class="topic-card__header">
        <span class="topic-card__icon">{icon}</span>
        <span class="topic-card__year">{year}</span>
    </div>
    <div class="topic-card__title">{title}</div>
    <div class="topic-card__value">{value}</div>
    <div class="topic-card__unit">{unit}</div>
    <div class="topic-card__delta">{arrow}&nbsp;{delta_text}</div>
</div>
"""


def live_card(icon: str, title: str, value: str, subtitle: str,
              status_color: str = "#007A6E") -> str:
    """Compact live-data indicator card."""
    return f"""
<div class="theme-card live-card" style="--accent:{status_color};">
  <div class="live-card__icon">{icon}</div>
  <div class="live-card__title">{title}</div>
  <div class="live-card__value">{value}</div>
  <div class="live-card__subtitle">{subtitle}</div>
</div>
"""


GLOBAL_CSS = _load_global_css()
