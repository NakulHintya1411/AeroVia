"""AeroVia Design System — safe, precise selectors only."""

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Sora:wght@700;800&display=swap');

/* ── Tokens ─────────────────────────────────────────────────── */
:root {
  --bg:            #ffffff;
  --bg-subtle:     #f8f9fc;
  --bg-inset:      #f1f4f9;
  --border:        #e2e7f0;
  --border-strong: #c8d0e2;
  --text:          #0f1724;
  --text-2:        #3d4f6b;
  --text-3:        #7a8ba8;
  --text-4:        #b0bdd0;
  --accent:        #2563eb;
  --accent-subtle: #eff4ff;
  --accent-mid:    #bfcffe;
  --green:         #059669;
  --green-subtle:  #ecfdf5;
  --red:           #dc2626;
  --red-subtle:    #fef2f2;
  --amber:         #d97706;
  --amber-subtle:  #fffbeb;
  --shadow-sm:     0 1px 3px rgba(15,23,36,0.07), 0 1px 2px rgba(15,23,36,0.04);
  --shadow-md:     0 4px 14px rgba(15,23,36,0.10), 0 2px 4px rgba(15,23,36,0.05);
  --r: 8px; --rs: 5px;
}

/* ── App background ─────────────────────────────────────────── */
.stApp { background: var(--bg) !important; }
.main .block-container { 
  background: var(--bg) !important;
  padding: 2rem 2.5rem 4rem !important;
  max-width: 1320px !important;
}

/* ── Body text — only Streamlit's markdown elements ────────── */
.stMarkdown p, .stMarkdown li, .stMarkdown span,
.stText, .stCaption p,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
  color: var(--text-2) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 14px !important;
  line-height: 1.6 !important;
}

/* ── Headings ───────────────────────────────────────────────── */
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {
  color: var(--text) !important;
  font-family: 'Sora', sans-serif !important;
}

/* ── Sidebar ────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: var(--bg-subtle) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .block-container {
  padding: 0 !important;
}

/* Sidebar text */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div {
  color: var(--text-2) !important;
  font-family: 'Inter', sans-serif !important;
}

/* ── Sidebar multipage nav ──────────────────────────────────── */
[data-testid="stSidebarNav"] {
  padding: 4px 0 !important;
}
[data-testid="stSidebarNav"] ul {
  padding: 0 8px !important;
}
[data-testid="stSidebarNav"] li { margin: 1px 0 !important; }
[data-testid="stSidebarNav"] a {
  display: flex !important;
  align-items: center !important;
  padding: 8px 12px !important;
  border-radius: var(--rs) !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  color: var(--text-2) !important;
  text-decoration: none !important;
  transition: background 0.12s !important;
}
[data-testid="stSidebarNav"] a:hover {
  background: var(--bg-inset) !important;
  color: var(--text) !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
  background: var(--accent-subtle) !important;
  color: var(--accent) !important;
  font-weight: 600 !important;
}
/* Hide default "Navigation" heading */
[data-testid="stSidebarNav"]::before { display: none !important; }
[data-testid="stSidebarNavSeparator"] { display: none !important; }

/* ── Logo block ─────────────────────────────────────────────── */
.av-logo {
  padding: 22px 20px 18px;
  border-bottom: 1px solid var(--border);
}
.av-logo-mark { display: flex; align-items: center; gap: 10px; }
.av-logo-icon {
  width: 34px; height: 34px; background: var(--accent);
  border-radius: 9px; display: flex; align-items: center;
  justify-content: center; font-size: 17px; flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(37,99,235,0.25);
}
.av-logo-text {
  font-family: 'Sora', sans-serif !important;
  font-size: 17px !important; font-weight: 700 !important;
  color: var(--text) !important; letter-spacing: -0.3px;
}
.av-logo-sub {
  font-size: 11px !important; color: var(--text-3) !important;
  margin-top: 5px; font-weight: 400 !important;
}
.nav-group-label {
  font-size: 10px !important; font-weight: 600 !important;
  letter-spacing: 1px; text-transform: uppercase;
  color: var(--text-4) !important;
  padding: 14px 20px 5px;
  font-family: 'Inter', sans-serif !important;
}
.sidebar-footer {
  padding: 14px 20px;
  border-top: 1px solid var(--border);
  margin-top: 16px;
}
.sidebar-version {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 10px !important; color: var(--text-4) !important;
}

/* ── Page header ────────────────────────────────────────────── */
.ph-wrap {
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border);
}
.ph-eyebrow {
  font-size: 11px; font-weight: 600;
  letter-spacing: 0.8px; text-transform: uppercase;
  color: var(--accent); margin-bottom: 5px;
  font-family: 'Inter', sans-serif;
}
.ph-title {
  font-family: 'Sora', sans-serif;
  font-size: 26px; font-weight: 700;
  color: var(--text); letter-spacing: -0.5px; margin: 0;
}
.ph-sub {
  font-size: 13px; color: var(--text-3);
  margin-top: 6px; line-height: 1.55;
  font-family: 'Inter', sans-serif;
}

/* ── Section label ──────────────────────────────────────────── */
.sec-label {
  font-size: 11px; font-weight: 600;
  letter-spacing: 0.6px; text-transform: uppercase;
  color: var(--text-3); margin: 26px 0 12px;
  display: flex; align-items: center; gap: 10px;
  font-family: 'Inter', sans-serif;
}
.sec-label::after { content: ''; flex: 1; height: 1px; background: var(--border); }

/* ── KPI Cards ──────────────────────────────────────────────── */
.kpi-card {
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 18px 20px;
  box-shadow: var(--shadow-sm);
  margin-bottom: 4px;
}
.kpi-card.kv-positive { border-left: 3px solid var(--green); }
.kpi-card.kv-negative { border-left: 3px solid var(--red); }
.kpi-card.kv-amber    { border-left: 3px solid var(--amber); }
.kpi-card.kv-accent   { border-left: 3px solid var(--accent); }
.kpi-label {
  font-size: 11px; font-weight: 600; letter-spacing: 0.4px;
  text-transform: uppercase; color: var(--text-3); margin-bottom: 9px;
  font-family: 'Inter', sans-serif;
}
.kpi-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 24px; font-weight: 600;
  color: var(--text); line-height: 1;
}
.kpi-delta {
  display: flex; align-items: center; gap: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px; font-weight: 500; margin-top: 8px;
}
.kpi-delta.up   { color: var(--green); }
.kpi-delta.down { color: var(--red); }
.kpi-sub { font-size: 11px; color: var(--text-4); margin-top: 4px; font-family: 'Inter', sans-serif; }

/* ── Badges ─────────────────────────────────────────────────── */
.badge {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 3px 10px 3px 8px; border-radius: 20px;
  font-size: 11px; font-weight: 600;
  font-family: 'Inter', sans-serif;
}
.badge::before { content: '●'; font-size: 7px; }
.badge-profit { background: var(--green-subtle); color: var(--green); }
.badge-loss   { background: var(--red-subtle);   color: var(--red); }
.badge-break  { background: var(--amber-subtle); color: var(--amber); }

/* ── Route display ──────────────────────────────────────────── */
.route-meta-bar { display: flex; align-items: center; gap: 12px; margin: 14px 0 22px; flex-wrap: wrap; }
.route-display {
  display: inline-flex; align-items: center; gap: 10px;
  background: var(--bg-inset); border: 1px solid var(--border);
  border-radius: var(--rs); padding: 8px 16px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 15px; font-weight: 600; color: var(--text);
}
.route-arrow { color: var(--text-4); font-size: 11px; }
.route-meta  { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text-3); }
.route-sep   { color: var(--border-strong); }

/* ── Info panel ─────────────────────────────────────────────── */
.info-panel {
  background: var(--bg-inset); border: 1px solid var(--border);
  border-left: 3px solid var(--accent-mid);
  border-radius: 0 var(--rs) var(--rs) 0;
  padding: 12px 16px; font-size: 13px;
  color: var(--text-2); line-height: 1.6;
  font-family: 'Inter', sans-serif;
}

/* ── Form inputs ────────────────────────────────────────────── */
[data-testid="stSelectbox"] label,
[data-testid="stNumberInput"] label,
[data-testid="stTextInput"] label,
[data-testid="stSlider"] label,
[data-testid="stFileUploader"] label {
  color: var(--text-2) !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  font-family: 'Inter', sans-serif !important;
}
[data-testid="stSelectbox"] > div > div {
  background: #fff !important;
  border: 1px solid var(--border-strong) !important;
  color: var(--text) !important;
  border-radius: var(--rs) !important;
}
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {
  background: #fff !important;
  border: 1px solid var(--border-strong) !important;
  color: var(--text) !important;
  border-radius: var(--rs) !important;
  font-family: 'Inter', sans-serif !important;
}
[data-testid="stSelectbox"] > div > div:focus-within,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextInput"] input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(37,99,235,0.10) !important;
  outline: none !important;
}
/* Slider track & thumb */
[data-testid="stSlider"] [role="slider"] {
  background: var(--accent) !important;
  border: 2px solid #fff !important;
  box-shadow: 0 0 0 2px var(--accent) !important;
}
[data-testid="stSlider"] [data-testid="stSliderTrack"] > div:last-child {
  background: var(--accent) !important;
}

/* ── Buttons ────────────────────────────────────────────────── */
.stButton > button {
  background: #fff !important;
  border: 1px solid var(--border-strong) !important;
  color: var(--text-2) !important;
  border-radius: var(--rs) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 12px !important; font-weight: 600 !important;
  padding: 6px 16px !important;
  box-shadow: var(--shadow-sm) !important;
  transition: all 0.12s !important;
}
.stButton > button:hover {
  border-color: var(--accent) !important;
  color: var(--accent) !important;
  background: var(--accent-subtle) !important;
  box-shadow: none !important;
}

/* ── Tabs ───────────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {
  border-bottom: 1px solid var(--border) !important;
  gap: 0 !important; background: transparent !important;
}
[data-testid="stTabs"] button[role="tab"] {
  font-family: 'Inter', sans-serif !important;
  font-size: 12px !important; font-weight: 600 !important;
  color: var(--text-3) !important;
  padding: 8px 18px !important;
  border: none !important;
  border-bottom: 2px solid transparent !important;
  background: transparent !important;
  border-radius: 0 !important;
  margin-bottom: -1px !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
  color: var(--accent) !important;
  border-bottom-color: var(--accent) !important;
}
[data-testid="stTabs"] button[role="tab"]:hover:not([aria-selected="true"]) {
  color: var(--text-2) !important;
}

/* ── Expander ───────────────────────────────────────────────── */
[data-testid="stExpander"] {
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  background: #fff !important;
  box-shadow: var(--shadow-sm) !important;
  overflow: hidden !important;
}
[data-testid="stExpander"] summary {
  font-size: 12px !important; font-weight: 600 !important;
  color: var(--text-2) !important; padding: 12px 16px !important;
  background: var(--bg-inset) !important;
  font-family: 'Inter', sans-serif !important;
}

/* ── Dataframe ──────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  box-shadow: var(--shadow-sm) !important;
}

/* ── File uploader ──────────────────────────────────────────── */
[data-testid="stFileUploader"] {
  border: 2px dashed var(--border-strong) !important;
  border-radius: var(--r) !important;
  background: var(--bg-inset) !important;
}

/* ── Toggle ─────────────────────────────────────────────────── */
[data-testid="stToggle"] [role="switch"][aria-checked="true"] {
  background-color: var(--accent) !important;
}

/* ── Chat messages ──────────────────────────────────────────── */
[data-testid="stChatMessage"] {
  background: #fff !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  box-shadow: var(--shadow-sm) !important;
}

/* ── Download button ────────────────────────────────────────── */
[data-testid="stDownloadButton"] button {
  background: #fff !important;
  border: 1px solid var(--border-strong) !important;
  color: var(--text-3) !important;
  border-radius: var(--rs) !important;
  font-size: 12px !important; font-weight: 600 !important;
  font-family: 'Inter', sans-serif !important;
}
[data-testid="stDownloadButton"] button:hover {
  border-color: var(--green) !important;
  color: var(--green) !important;
  background: var(--green-subtle) !important;
}

/* ── Plotly wrapper ─────────────────────────────────────────── */
[data-testid="stPlotlyChart"] {
  border: 1px solid var(--border);
  border-radius: var(--r);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

/* ── Native st.metric ───────────────────────────────────────── */
[data-testid="metric-container"] {
  background: #fff !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  padding: 16px 18px !important;
  box-shadow: var(--shadow-sm) !important;
}
[data-testid="stMetricLabel"] > div {
  font-size: 11px !important; font-weight: 600 !important;
  text-transform: uppercase !important; letter-spacing: 0.5px !important;
  color: var(--text-3) !important;
  font-family: 'Inter', sans-serif !important;
}
[data-testid="stMetricValue"] {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 22px !important; color: var(--text) !important;
}

/* ── Alert ──────────────────────────────────────────────────── */
[data-testid="stAlert"] {
  border-radius: var(--rs) !important;
  font-size: 13px !important;
  font-family: 'Inter', sans-serif !important;
}

/* ── Caption ────────────────────────────────────────────────── */
[data-testid="stCaptionContainer"] p {
  color: var(--text-3) !important;
  font-size: 12px !important;
  font-family: 'Inter', sans-serif !important;
}

/* ── Divider ────────────────────────────────────────────────── */
hr { border-color: var(--border) !important; margin: 20px 0 !important; }



/* ── Scrollbar ──────────────────────────────────────────────── */

/* Hide auto-generated app nav item */
[data-testid="stSidebarNav"] li:first-child { display: none !important; }
[data-testid="stSidebarNav"] a[href="/"] { display: none !important; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-subtle); }
::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 3px; }
</style>
"""

PLOTLY_THEME = dict(
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    font=dict(family="Inter, sans-serif", color="#7a8ba8", size=11),
    xaxis=dict(gridcolor="#f1f4f9", linecolor="#e2e7f0",
               tickcolor="#e2e7f0", zerolinecolor="#e2e7f0"),
    yaxis=dict(gridcolor="#f1f4f9", linecolor="#e2e7f0",
               tickcolor="#e2e7f0", zerolinecolor="#e2e7f0"),
    margin=dict(l=14, r=14, t=40, b=14),
    colorway=["#2563eb","#059669","#dc2626","#d97706","#7c3aed","#0891b2"],
)

COLORS = dict(
    accent="#2563eb",  accent_subtle="#eff4ff",  accent_mid="#bfcffe",
    green="#059669",   green_subtle="#ecfdf5",
    red="#dc2626",     red_subtle="#fef2f2",
    amber="#d97706",   amber_subtle="#fffbeb",
    text="#0f1724",    text2="#3d4f6b",  text3="#7a8ba8",  text4="#b0bdd0",
    bg="#ffffff",      bg_subtle="#f8f9fc",  bg_card="#ffffff",  bg_inset="#f1f4f9",
    border="#e2e7f0",  border_strong="#c8d0e2",
)
