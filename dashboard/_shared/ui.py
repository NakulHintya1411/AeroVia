"""Shared UI helpers."""
import streamlit as st
import copy, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dashboard._shared.styles import COLORS, PLOTLY_THEME


def inject_css():
    from dashboard._shared.styles import GLOBAL_CSS
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def empty_state(icon: str, title: str, subtitle: str, tip: str = ""):
    """Render a clean empty state — shown when no data/selection yet."""
    st.markdown(f"""
    <div style="
        display: flex; flex-direction: column; align-items: center;
        justify-content: center; padding: 64px 32px; text-align: center;
        background: var(--bg-inset); border: 1px dashed var(--border-strong);
        border-radius: 12px; margin: 24px 0;
    ">
        <div style="font-size: 40px; margin-bottom: 16px; opacity: 0.6">{icon}</div>
        <div style="
            font-family: 'Sora', sans-serif; font-size: 18px; font-weight: 700;
            color: var(--text); margin-bottom: 8px; letter-spacing: -0.3px;
        ">{title}</div>
        <div style="
            font-size: 13px; color: var(--text-3); max-width: 380px;
            line-height: 1.6; margin-bottom: {"16px" if tip else "0"};
        ">{subtitle}</div>
        {"<div style='font-size:12px;color:var(--accent);font-weight:600;background:var(--accent-subtle);padding:6px 14px;border-radius:20px'>" + tip + "</div>" if tip else ""}
    </div>
    """, unsafe_allow_html=True)


def sidebar_logo():
    st.markdown("""
    <div class="av-logo">
      <div class="av-logo-mark">
        <div class="av-logo-icon">✈</div>
        <span class="av-logo-text">AeroVia</span>
      </div>
      <div class="av-logo-sub">Route Profitability Simulator</div>
    </div>
    <div class="nav-group-label">Pages</div>
    """, unsafe_allow_html=True)


def page_header(eyebrow, title, subtitle=""):
    st.markdown(f"""
    <div class="ph-wrap">
      <div class="ph-eyebrow">{eyebrow}</div>
      <div class="ph-title">{title}</div>
      {"<div class='ph-sub'>" + subtitle + "</div>" if subtitle else ""}
    </div>""", unsafe_allow_html=True)


def section(label):
    st.markdown(f'<div class="sec-label">{label}</div>', unsafe_allow_html=True)


def kpi_row(items):
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        kv = f"kv-{item['variant']}" if item.get("variant") else ""
        delta_html = ""
        if item.get("delta"):
            pos = item.get("delta_pos", True)
            delta_html = f'<div class="kpi-delta {"up" if pos else "down"}">{"↑" if pos else "↓"} {item["delta"]}</div>'
        sub_html = f'<div class="kpi-sub">{item["sub"]}</div>' if item.get("sub") else ""
        col.markdown(f"""
        <div class="kpi-card {kv}">
          <div class="kpi-label">{item['label']}</div>
          <div class="kpi-value">{item['value']}</div>
          {delta_html}{sub_html}
        </div>""", unsafe_allow_html=True)


def route_meta_bar(origin, destination, distance_km, flight_time_hr, margin_pct):
    badge_cls = "badge-profit" if margin_pct > 2 else "badge-loss" if margin_pct < 0 else "badge-break"
    badge_txt = "Profitable" if margin_pct > 2 else "Loss-Making" if margin_pct < 0 else "Break-Even"
    st.markdown(f"""
    <div class="route-meta-bar">
      <div class="route-display">{origin} <span class="route-arrow">→</span> {destination}</div>
      <span class="route-meta">{distance_km:,.0f} km</span>
      <span class="route-sep">·</span>
      <span class="route-meta">{flight_time_hr:.1f} hr</span>
      <span class="badge {badge_cls}">{badge_txt}</span>
    </div>""", unsafe_allow_html=True)


def apply_theme(fig, title="", height=320):
    t = copy.deepcopy(PLOTLY_THEME)
    fig.update_layout(
        **t,
        title=dict(text=title,
                   font=dict(size=12, color=COLORS["text3"], family="Inter, sans-serif"),
                   x=0, pad=dict(l=2)),
        height=height,
        legend=dict(bgcolor=COLORS["bg_card"], bordercolor=COLORS["border"],
                    borderwidth=1,
                    font=dict(size=11, color=COLORS["text3"], family="Inter, sans-serif")),
    )
    return fig
