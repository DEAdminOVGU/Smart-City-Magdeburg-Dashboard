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
/* ── Global chrome ─────────────────────────────────────────── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1100px;
}

h1 { font-size: 2.1rem !important; font-weight: 800 !important; color: #1A1A1A !important; }
h2 { font-size: 1.35rem !important; font-weight: 700 !important; color: #2A2A2A !important; }
h3 { font-size: 1.1rem !important; font-weight: 700 !important; }

.js-plotly-plot { border-radius: 12px; }
hr { border-color: #e8ecec !important; }
.stCaption, caption { color: #999 !important; font-size: 0.78rem !important; }

/* ── Sidebar shell ─────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e8ecec !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}

/* Hide the auto-generated stSidebarNav — we use st.page_link() tiles instead */
[data-testid="stSidebarNav"] { display: none !important; }

/* ── Navigation tile base ──────────────────────────────────── */
[data-testid="stPageLink"] {
    width: 100% !important;
    margin: 0 !important;
    padding: 2px 12px !important;
}

[data-testid="stPageLink"] a,
[data-testid="stPageLink"] a:visited {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 13px !important;
    padding: 14px 16px !important;
    border-radius: 12px !important;
    border-left: 5px solid #e8ecec !important;
    background: #f9fafb !important;
    color: #52617a !important;
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.01em !important;
    text-decoration: none !important;
    transition: all 0.14s ease !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
    line-height: 1.25 !important;
}

/* Icon (first span inside the anchor) */
[data-testid="stPageLink"] a > span:first-child,
[data-testid="stPageLink"] a > p:first-child,
[data-testid="stPageLink"] a > div:first-child {
    font-size: 1.35rem !important;
    line-height: 1 !important;
    flex-shrink: 0 !important;
    width: 28px !important;
    text-align: center !important;
}

/* ── Hover state (all tiles — teal default) ────────────────── */
[data-testid="stPageLink"] a:hover {
    background: #f0f9f7 !important;
    border-left-color: #007A6E !important;
    color: #007A6E !important;
    box-shadow: 0 3px 10px rgba(0,122,110,0.13) !important;
    transform: translateX(2px);
}

/* ── Per-tile hover accent ─────────────────────────────────── */
[data-testid="stPageLink"]:nth-of-type(2) a:hover
{ border-left-color:#00897B!important;color:#00695C!important;background:#e8f7f4!important; }
[data-testid="stPageLink"]:nth-of-type(3) a:hover
{ border-left-color:#1565C0!important;color:#1565C0!important;background:#e8f0fb!important; }
[data-testid="stPageLink"]:nth-of-type(4) a:hover
{ border-left-color:#6A1B9A!important;color:#6A1B9A!important;background:#f4ecfb!important; }
[data-testid="stPageLink"]:nth-of-type(5) a:hover
{ border-left-color:#2E7D32!important;color:#2E7D32!important;background:#eaf4ea!important; }

/* ── Active tile (per-topic filled background) ─────────────── */
[data-testid="stPageLink"]:nth-of-type(1) a[aria-current="page"],
[data-testid="stPageLink"]:nth-of-type(1) a[aria-selected="true"] {
    background: #007A6E !important;
    border-left-color: #005a54 !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(0,122,110,0.30) !important;
}
[data-testid="stPageLink"]:nth-of-type(2) a[aria-current="page"],
[data-testid="stPageLink"]:nth-of-type(2) a[aria-selected="true"] {
    background: #00897B !important;
    border-left-color: #00695C !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(0,137,123,0.30) !important;
}
[data-testid="stPageLink"]:nth-of-type(3) a[aria-current="page"],
[data-testid="stPageLink"]:nth-of-type(3) a[aria-selected="true"] {
    background: #1565C0 !important;
    border-left-color: #0D47A1 !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(21,101,192,0.30) !important;
}
[data-testid="stPageLink"]:nth-of-type(4) a[aria-current="page"],
[data-testid="stPageLink"]:nth-of-type(4) a[aria-selected="true"] {
    background: #6A1B9A !important;
    border-left-color: #4A148C !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(106,27,154,0.30) !important;
}
[data-testid="stPageLink"]:nth-of-type(5) a[aria-current="page"],
[data-testid="stPageLink"]:nth-of-type(5) a[aria-selected="true"] {
    background: #2E7D32 !important;
    border-left-color: #1B5E20 !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(46,125,50,0.30) !important;
}

/* Keep icon white on active tiles */
[data-testid="stPageLink"] a[aria-current="page"] > span,
[data-testid="stPageLink"] a[aria-current="page"] > p,
[data-testid="stPageLink"] a[aria-current="page"] > div {
    color: #ffffff !important;
}

/* ── Sidebar section separator ─────────────────────────────── */
.sidebar-sep {
    height: 1px;
    background: #eef0f2;
    margin: 10px 12px;
}

/* ── Sidebar bottom caption ────────────────────────────────── */
.sidebar-footer {
    font-size: 0.7rem;
    color: #bbb;
    padding: 8px 20px 16px;
    line-height: 1.5;
}
</style>
"""
