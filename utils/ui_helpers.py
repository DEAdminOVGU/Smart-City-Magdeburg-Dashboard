"""Shared HTML components for the Smart City Magdeburg Dashboard."""


def hero_stat(icon: str, value: str, description: str,
              delta_text: str, delta_positive: bool,
              color: str = "#007A6E") -> str:
    """Bold hero KPI block shown at the top of each page."""
    arrow = "↑" if delta_positive else "↓"
    delta_color = "#1B5E20" if delta_positive else "#B71C1C"
    delta_bg = "#E8F5E9" if delta_positive else "#FFEBEE"
    return f"""
<div style="background:linear-gradient(135deg,{color}18 0%,{color}04 100%);
            border-left:5px solid {color};border-radius:0 16px 16px 0;
            padding:24px 32px;margin-bottom:28px;">
  <div style="font-size:2.2rem;line-height:1;">{icon}</div>
  <div style="font-size:3rem;font-weight:800;color:#1A1A1A;line-height:1.15;margin-top:6px;">{value}</div>
  <div style="font-size:1.05rem;color:#555;margin-top:8px;">{description}</div>
  <div style="margin-top:12px;display:inline-block;background:{delta_bg};
              color:{delta_color};border-radius:20px;padding:4px 16px;
              font-size:0.88rem;font-weight:700;">{arrow}&nbsp;{delta_text}</div>
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
<div style="background:#fff;border-radius:14px;padding:22px 18px;
            box-shadow:0 2px 16px rgba(0,0,0,0.07);
            border-top:4px solid {color};margin-bottom:4px;">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
    <span style="font-size:1.8rem;line-height:1;">{icon}</span>
    <span style="font-size:0.68rem;color:#bbb;font-weight:700;
                 text-transform:uppercase;letter-spacing:0.06em;">{year}</span>
  </div>
  <div style="font-size:0.7rem;font-weight:800;color:#999;text-transform:uppercase;
              letter-spacing:0.12em;margin-bottom:5px;">{title}</div>
  <div style="font-size:2rem;font-weight:800;color:#1A1A1A;line-height:1.1;">{value}</div>
  <div style="font-size:0.78rem;color:#bbb;margin-top:3px;margin-bottom:14px;">{unit}</div>
  <div style="display:inline-block;background:{delta_bg};color:{delta_color};
              border-radius:16px;padding:3px 12px;font-size:0.76rem;font-weight:700;">
    {arrow}&nbsp;{delta_text}
  </div>
</div>
"""


def live_card(icon: str, title: str, value: str, subtitle: str,
              status_color: str = "#007A6E") -> str:
    """Compact live-data indicator card."""
    return f"""
<div style="background:#fff;border-radius:12px;padding:18px 16px;
            box-shadow:0 2px 12px rgba(0,0,0,0.06);
            border-left:4px solid {status_color};margin-bottom:4px;">
  <div style="font-size:1.5rem;line-height:1;margin-bottom:6px;">{icon}</div>
  <div style="font-size:0.68rem;font-weight:800;color:#999;text-transform:uppercase;
              letter-spacing:0.1em;margin-bottom:4px;">{title}</div>
  <div style="font-size:1.8rem;font-weight:800;color:#1A1A1A;line-height:1.1;">{value}</div>
  <div style="font-size:0.78rem;color:#999;margin-top:4px;">{subtitle}</div>
</div>
"""


GLOBAL_CSS = """
<style>
/* ── Streamlit chrome ──────────────────────────────────────── */
#MainMenu          { visibility: hidden; }
footer             { visibility: hidden; }
header             { visibility: hidden; }
[data-testid="stSidebar"]         { display: none !important; }
[data-testid="collapsedControl"]  { display: none !important; }
[data-testid="stSidebarNav"]      { display: none !important; }
.nav-sentinel      { display: none; }

/* ── Main content padding ───────────────────────────────────── */
.block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1160px;
}

/* ── Nav container visual styling (non-sticky, part of normal flow) ───────── */
[data-testid="stVerticalBlock"] .nav-sentinel {
    display: none !important;
}
/* Give the columns row containing the nav a bottom border */
[data-testid="stHorizontalBlock"]:has([data-testid="stPageLink"]) {
    border-bottom: 2px solid #eef0f2 !important;
    padding-bottom: 2px !important;
    margin-bottom: 8px !important;
    background: #ffffff !important;
}

/* ── Brand block ──────────────────────────────────────────── */
.topnav-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 4px;
}
.brand-icon { font-size: 1.6rem; line-height: 1; }
.brand-name {
    font-size: 1.05rem;
    font-weight: 900;
    color: #007A6E;
    letter-spacing: -0.03em;
    line-height: 1.1;
}
.brand-sub {
    font-size: 0.6rem;
    color: #aaa;
    text-transform: uppercase;
    letter-spacing: 0.13em;
    font-weight: 600;
}

/* ── st.page_link() tab style ─────────────────────────────── */
[data-testid="stPageLink"] {
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
}

[data-testid="stPageLink"] a,
[data-testid="stPageLink"] a:visited {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 3px !important;
    padding: 10px 4px 9px !important;
    border-bottom: 3px solid transparent !important;
    border-radius: 0 !important;
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    color: #64748b !important;
    text-decoration: none !important;
    text-align: center !important;
    transition: all 0.15s ease !important;
    white-space: normal !important;
    word-break: keep-all !important;
    width: 100% !important;
}

/* Icon inside page_link */
[data-testid="stPageLink"] a p {
    font-size: 1.2rem !important;
    margin: 0 !important;
    line-height: 1 !important;
}

/* Hover — default teal */
[data-testid="stPageLink"] a:hover {
    color: #007A6E !important;
    border-bottom-color: #007A6E !important;
    background: #f0faf8 !important;
}

/* ── Active tab (per-topic) ───────────────────────────────── */
[data-testid="stPageLink"]:nth-of-type(1) a[aria-current="page"] {
    color: #007A6E !important;
    border-bottom-color: #007A6E !important;
    background: #f0faf8 !important;
}
[data-testid="stPageLink"]:nth-of-type(2) a[aria-current="page"] {
    color: #00897B !important;
    border-bottom-color: #00897B !important;
    background: #e8f7f4 !important;
}
[data-testid="stPageLink"]:nth-of-type(3) a[aria-current="page"] {
    color: #1565C0 !important;
    border-bottom-color: #1565C0 !important;
    background: #e8f0fb !important;
}
[data-testid="stPageLink"]:nth-of-type(4) a[aria-current="page"] {
    color: #6A1B9A !important;
    border-bottom-color: #6A1B9A !important;
    background: #f4ecfb !important;
}
[data-testid="stPageLink"]:nth-of-type(5) a[aria-current="page"] {
    color: #2E7D32 !important;
    border-bottom-color: #2E7D32 !important;
    background: #eaf4ea !important;
}

/* ── Per-topic hover accents ─────────────────────────────── */
[data-testid="stPageLink"]:nth-of-type(2) a:hover
  { color:#00695C!important; border-bottom-color:#00897B!important; background:#e8f7f4!important; }
[data-testid="stPageLink"]:nth-of-type(3) a:hover
  { color:#1565C0!important; border-bottom-color:#1565C0!important; background:#e8f0fb!important; }
[data-testid="stPageLink"]:nth-of-type(4) a:hover
  { color:#6A1B9A!important; border-bottom-color:#6A1B9A!important; background:#f4ecfb!important; }
[data-testid="stPageLink"]:nth-of-type(5) a:hover
  { color:#2E7D32!important; border-bottom-color:#2E7D32!important; background:#eaf4ea!important; }

/* ── Typography ─────────────────────────────────────────── */
h1 { font-size: 2.1rem !important; font-weight: 800 !important; color: #1A1A1A !important; }
h2 { font-size: 1.35rem !important; font-weight: 700 !important; color: #2A2A2A !important; }
h3 { font-size: 1.1rem  !important; font-weight: 700 !important; }
.js-plotly-plot { border-radius: 12px; }
hr { border-color: #e8ecec !important; }
.stCaption, caption { color: #999 !important; font-size: 0.78rem !important; }
</style>
"""
