import os
import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AirLab France",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════════════════════
# CSS — Thème clair, lisible, professionnel
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --bg:        #F4F6FA;
    --surface:   #FFFFFF;
    --surface2:  #F0F2F8;
    --border:    #DDE1EE;
    --accent:    #2563EB;
    --accent-lt: #EEF3FF;
    --good:      #16A34A;
    --good-lt:   #DCFCE7;
    --mod:       #D97706;
    --mod-lt:    #FEF3C7;
    --bad:       #DC2626;
    --bad-lt:    #FEE2E2;
    --text-h:    #0F172A;
    --text-b:    #1E293B;
    --text-m:    #475569;
    --text-s:    #94A3B8;
    --shadow:    0 1px 4px rgba(15,23,42,.08), 0 4px 16px rgba(15,23,42,.06);
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text-b) !important;
}

/* ─── Hide default chrome ─── */
header[data-testid="stHeader"]         { display: none !important; }
[data-testid="stDecoration"]           { display: none !important; }
#MainMenu                              { display: none !important; }
footer                                 { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ─── Sidebar ─── */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1.5px solid var(--border) !important;
    padding-top: 0 !important;
}
section[data-testid="stSidebar"] > div { padding: 0 !important; }
section[data-testid="stSidebar"] * { color: var(--text-b) !important; }
section[data-testid="stSidebar"] label { color: var(--text-m) !important; font-size: .78rem !important; font-weight: 600 !important; text-transform: uppercase; letter-spacing: .06em; }

/* ─── Metrics override ─── */
[data-testid="metric-container"] {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 1.1rem 1.3rem !important;
    box-shadow: var(--shadow) !important;
}
[data-testid="stMetricLabel"] {
    font-size: .72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: .07em;
    color: var(--text-m) !important;
}
[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: var(--text-h) !important;
    line-height: 1.1 !important;
}

/* ─── Tabs (nav en haut) ─── */
.stTabs { padding: 0 !important; }
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-bottom: 2px solid var(--border) !important;
    padding: 0 2rem !important;
    gap: 0 !important;
    border-radius: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 3px solid transparent !important;
    border-radius: 0 !important;
    padding: .85rem 1.2rem !important;
    font-size: .85rem !important;
    font-weight: 600 !important;
    color: var(--text-m) !important;
    margin-bottom: -2px !important;
}
.stTabs [aria-selected="true"] {
    border-bottom: 3px solid var(--accent) !important;
    color: var(--accent) !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] { padding: 1.5rem 2rem !important; }

/* ─── Cards ─── */
.card {
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    box-shadow: var(--shadow);
    margin-bottom: .75rem;
}
.card-title {
    font-size: .68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .08em;
    color: var(--text-m);
    margin-bottom: .5rem;
}
.kpi-num {
    font-size: 2.4rem;
    font-weight: 800;
    line-height: 1;
    color: var(--text-h);
}
.kpi-sub {
    font-size: .8rem;
    color: var(--text-m);
    margin-top: .35rem;
}

/* ─── Badges ─── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: .3rem;
    padding: .25rem .75rem;
    border-radius: 999px;
    font-size: .72rem;
    font-weight: 700;
    letter-spacing: .04em;
}
.b-good { background: var(--good-lt); color: var(--good); }
.b-mod  { background: var(--mod-lt);  color: var(--mod);  }
.b-bad  { background: var(--bad-lt);  color: var(--bad);  }

/* ─── Top header bar ─── */
.topbar {
    background: var(--surface);
    border-bottom: 1.5px solid var(--border);
    padding: .85rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
}
.topbar-brand { display: flex; align-items: center; gap: .7rem; }
.topbar-brand .logo { font-size: 1.25rem; font-weight: 800; color: var(--accent); }
.topbar-brand .tagline { font-size: .75rem; color: var(--text-m); }
.topbar-date {
    background: var(--accent-lt);
    border: 1.5px solid #BFDBFE;
    border-radius: 8px;
    padding: .4rem .9rem;
    font-size: .78rem;
    font-weight: 700;
    color: var(--accent);
}

/* ─── Section headers ─── */
.sec-hdr {
    font-size: .68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .1em;
    color: var(--text-m);
    margin: 1.4rem 0 .7rem;
    display: flex;
    align-items: center;
    gap: .5rem;
}
.sec-hdr::after {
    content: '';
    flex: 1;
    height: 1.5px;
    background: var(--border);
    border-radius: 2px;
}

/* ─── Alert banner ─── */
.alert-banner {
    background: #FFF1F2;
    border: 1.5px solid #FECDD3;
    border-left: 5px solid var(--bad);
    border-radius: 10px;
    padding: .9rem 1.2rem;
    font-size: .875rem;
    font-weight: 600;
    color: #991B1B;
    margin-bottom: 1rem;
}

/* ─── Dataframe ─── */
[data-testid="stDataFrame"] {
    border: 1.5px solid var(--border) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    box-shadow: var(--shadow) !important;
}

/* ─── Select / multiselect ─── */
[data-baseweb="select"] { border-radius: 8px !important; }
[data-baseweb="tag"] {
    background: var(--accent-lt) !important;
    color: var(--accent) !important;
    border: 1px solid #BFDBFE !important;
    border-radius: 6px !important;
}

/* ─── Login page ─── */
.login-outer {
    display: flex; align-items: center; justify-content: center;
    min-height: 80vh;
}
.login-box {
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: 20px;
    padding: 2.8rem 2.4rem;
    max-width: 400px;
    width: 100%;
    box-shadow: var(--shadow);
    text-align: center;
}
.login-icon { font-size: 2.5rem; margin-bottom: .5rem; }
.login-title { font-size: 1.5rem; font-weight: 800; color: var(--text-h); margin-bottom: .3rem; }
.login-sub   { font-size: .85rem; color: var(--text-m); margin-bottom: 2rem; }

/* ─── Sidebar sections ─── */
.sb-section {
    padding: .5rem 1.2rem;
    font-size: .65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .1em;
    color: var(--text-s) !important;
    margin-top: .5rem;
}
.sb-logo {
    padding: 1.2rem 1.2rem .8rem;
    border-bottom: 1.5px solid var(--border);
    margin-bottom: .5rem;
}
.sb-logo .name { font-size: 1.1rem; font-weight: 800; color: var(--accent) !important; }
.sb-logo .desc { font-size: .72rem; color: var(--text-m) !important; }
.sb-date-box {
    margin: .8rem 1.2rem;
    background: var(--accent-lt);
    border: 1.5px solid #BFDBFE;
    border-radius: 10px;
    padding: .7rem 1rem;
}
.sb-date-label { font-size: .62rem; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: var(--accent) !important; }
.sb-date-val   { font-size: .92rem; font-weight: 800; color: var(--accent) !important; margin-top: .15rem; }

hr { border-color: var(--border) !important; margin: .6rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════════════════════
APP_PASSWORD = os.getenv("APP_PASSWORD", "airlab2024")

def login_page():
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("""
        <div style='height:3rem'></div>
        <div style='text-align:center'>
            <div style='font-size:3rem'>🔬</div>
            <div style='font-size:1.6rem;font-weight:800;color:#0F172A;margin:.4rem 0 .3rem'>AirLab France</div>
            <div style='font-size:.9rem;color:#475569;margin-bottom:2rem'>Accès restreint — Entrez votre mot de passe</div>
        </div>
        """, unsafe_allow_html=True)

        pwd = st.text_input("Mot de passe", type="password",
                            placeholder="••••••••••••",
                            label_visibility="collapsed")
        btn = st.button("→ Accéder au dashboard", type="primary", use_container_width=True)

        if btn:
            if pwd == APP_PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            elif pwd:
                st.error("❌ Mot de passe incorrect.")
            else:
                st.warning("Veuillez entrer un mot de passe.")

        st.markdown("""
        <div style='text-align:center;margin-top:1.5rem;font-size:.75rem;color:#94A3B8'>
            Accès sur autorisation — GoodAir · AirLab France
        </div>
        """, unsafe_allow_html=True)

if not st.session_state.get("authenticated"):
    login_page()
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# DATA
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource
def get_supabase():
    return create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

supabase = get_supabase()

@st.cache_data(ttl=3600)
def load_data():
    air = pd.DataFrame(supabase.table("air_quality").select("*").order("ts").execute().data)
    wth = pd.DataFrame(supabase.table("weather").select("*").order("ts").execute().data)
    if not air.empty: air["ts"] = pd.to_datetime(air["ts"])
    if not wth.empty: wth["ts"] = pd.to_datetime(wth["ts"])
    return air, wth

air_df, wth_df = load_data()

COORDS = {
    "Paris":     (48.8566,  2.3522),
    "Lyon":      (45.7640,  4.8357),
    "Marseille": (43.2965,  5.3698),
    "Bordeaux":  (44.8378, -0.5792),
    "Lille":     (50.6292,  3.0573),
}

# Plotly layout — fond blanc
PL = dict(
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(family="Plus Jakarta Sans", color="#475569", size=12),
    xaxis=dict(gridcolor="#E2E8F0", showline=False, zeroline=False),
    yaxis=dict(gridcolor="#E2E8F0", showline=False, zeroline=False),
    margin=dict(l=10, r=10, t=36, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#475569")),
)
COLORS = ["#2563EB","#7C3AED","#059669","#D97706","#DC2626"]

def aqi_color(v):
    if v is None: return "#94A3B8"
    if v <= 50:   return "#16A34A"
    if v <= 100:  return "#D97706"
    if v <= 150:  return "#DC2626"
    return "#9F1239"

def aqi_badge(v):
    if v is None: return ""
    if v <= 50:  return '<span class="badge b-good">● Bon</span>'
    if v <= 100: return '<span class="badge b-mod">● Modéré</span>'
    return '<span class="badge b-bad">● Mauvais</span>'

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">
        <div class="name">🔬 AirLab France</div>
        <div class="desc">Monitoring qualité de l'air</div>
    </div>
    """, unsafe_allow_html=True)

    # Date dernière collecte
    if not air_df.empty:
        lu = air_df["ts"].max()
        st.markdown(f"""
        <div class="sb-date-box">
            <div class="sb-date-label">Dernière collecte</div>
            <div class="sb-date-val">{lu.strftime('%d/%m/%Y — %Hh%M')}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section">Filtres</div>', unsafe_allow_html=True)

    cities_list = sorted(air_df["city"].unique().tolist()) if not air_df.empty else []
    cities_sel  = st.multiselect(
        "Villes",
        cities_list,
        default=cities_list,
        placeholder="Sélectionner des villes..."
    )
    days = st.select_slider(
        "Période",
        options=[1, 3, 7, 14, 30],
        value=7,
        format_func=lambda x: f"{x} jour{'s' if x > 1 else ''}"
    )

    st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)
    st.divider()

    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# FILTRES
# ══════════════════════════════════════════════════════════════════════════════
if not air_df.empty and cities_sel:
    cutoff  = air_df["ts"].max() - pd.Timedelta(days=days)
    air_fil = air_df[air_df["city"].isin(cities_sel) & (air_df["ts"] >= cutoff)]
    wth_fil = wth_df[wth_df["city"].isin(cities_sel) & (wth_df["ts"] >= cutoff)] if not wth_df.empty else pd.DataFrame()
else:
    air_fil = wth_fil = pd.DataFrame()

# ══════════════════════════════════════════════════════════════════════════════
# NAVIGATION EN HAUT — Tabs Streamlit natifs
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊  Vue globale",
    "📈  Évolution AQI",
    "🔗  Corrélations",
    "🚨  Alertes",
    "📖  Indicateurs",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — VUE GLOBALE
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    if not air_fil.empty:
        latest  = air_fil.sort_values("ts").groupby("city").last().reset_index()
        alertes = latest[latest["is_alert"] == True]

        if not alertes.empty:
            villes = ", ".join(alertes["city"].tolist())
            st.markdown(f'<div class="alert-banner">🚨 Alerte seuil OMS dépassé — <strong>{villes}</strong></div>', unsafe_allow_html=True)

        # ── KPI cards AQI par ville ──────────────────────────────────────────
        st.markdown('<div class="sec-hdr">AQI par ville</div>', unsafe_allow_html=True)
        cols = st.columns(len(latest))
        for i, (_, row) in enumerate(latest.iterrows()):
            aqi = int(row["aqi"]) if pd.notna(row["aqi"]) else 0
            c   = aqi_color(aqi)
            with cols[i]:
                st.markdown(f"""
                <div class="card" style="border-top: 4px solid {c}; text-align:center">
                    <div class="card-title">{row['city']}</div>
                    <div class="kpi-num" style="color:{c}">{aqi}</div>
                    <div class="kpi-sub">{aqi_badge(aqi)}</div>
                </div>
                """, unsafe_allow_html=True)

        # ── Métriques moyennes ───────────────────────────────────────────────
        st.markdown('<div class="sec-hdr">Indicateurs moyens</div>', unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("AQI moyen",   f"{latest['aqi'].mean():.0f}")
        c2.metric("PM2.5 moy.",  f"{latest['pm25'].mean():.1f} µg/m³")
        c3.metric("PM10 moy.",   f"{latest['pm10'].mean():.1f} µg/m³")
        c4.metric("O3 moyen",    f"{latest['o3'].mean():.1f} µg/m³")
        c5.metric("Villes OK",   f"{len(latest[latest['aqi'] <= 100])} / {len(latest)}")

        # ── Carte ────────────────────────────────────────────────────────────
        st.markdown('<div class="sec-hdr">Carte France — AQI en temps réel</div>', unsafe_allow_html=True)
        latest["lat"]   = latest["city"].map(lambda c: COORDS.get(c, (0,0))[0])
        latest["lon"]   = latest["city"].map(lambda c: COORDS.get(c, (0,0))[1])
        latest["aqi_i"] = latest["aqi"].fillna(0).astype(int)
        fig = px.scatter_mapbox(
            latest, lat="lat", lon="lon",
            size="aqi_i", color="aqi_i",
            hover_name="city",
            hover_data={"aqi_i": True, "aqi_label": True, "lat": False, "lon": False},
            color_continuous_scale=[[0,"#16A34A"],[0.3,"#D97706"],[0.6,"#DC2626"],[1,"#9F1239"]],
            range_color=[0, 200], size_max=50, zoom=4,
            mapbox_style="carto-positron",
            labels={"aqi_i": "AQI"}
        )
        fig.update_layout(
            paper_bgcolor="#FFFFFF",
            margin={"r":0,"t":0,"l":0,"b":0},
            height=420
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sélectionnez des villes dans la barre latérale.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ÉVOLUTION AQI
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    if not air_fil.empty:
        sub1, sub2, sub3 = st.tabs(["AQI global", "PM2.5 / PM10", "O3 / NO2"])

        with sub1:
            fig = px.line(
                air_fil, x="ts", y="aqi", color="city",
                labels={"ts": "", "aqi": "AQI", "city": "Ville"},
                color_discrete_sequence=COLORS
            )
            fig.add_hline(y=100, line_dash="dot", line_color="#D97706",
                          annotation_text="Seuil modéré 100",
                          annotation_font_color="#D97706", annotation_font_size=11)
            fig.add_hline(y=150, line_dash="dot", line_color="#DC2626",
                          annotation_text="Seuil mauvais 150",
                          annotation_font_color="#DC2626", annotation_font_size=11)
            fig.update_traces(line=dict(width=2.5))
            fig.update_layout(**PL, height=380)
            st.plotly_chart(fig, use_container_width=True)

        with sub2:
            c1, c2 = st.columns(2)
            with c1:
                f2 = px.area(air_fil, x="ts", y="pm25", color="city",
                             labels={"ts":"","pm25":"µg/m³","city":"Ville"},
                             color_discrete_sequence=COLORS)
                f2.update_layout(**PL, height=300, title="<b>PM2.5</b>")
                st.plotly_chart(f2, use_container_width=True)
            with c2:
                f3 = px.area(air_fil, x="ts", y="pm10", color="city",
                             labels={"ts":"","pm10":"µg/m³","city":"Ville"},
                             color_discrete_sequence=COLORS)
                f3.update_layout(**PL, height=300, title="<b>PM10</b>")
                st.plotly_chart(f3, use_container_width=True)

        with sub3:
            c1, c2 = st.columns(2)
            with c1:
                f4 = px.line(air_fil, x="ts", y="o3", color="city",
                             labels={"ts":"","o3":"µg/m³","city":"Ville"},
                             color_discrete_sequence=COLORS)
                f4.update_layout(**PL, height=300, title="<b>Ozone (O3)</b>")
                st.plotly_chart(f4, use_container_width=True)
            with c2:
                f5 = px.line(air_fil, x="ts", y="no2", color="city",
                             labels={"ts":"","no2":"µg/m³","city":"Ville"},
                             color_discrete_sequence=COLORS)
                f5.update_layout(**PL, height=300, title="<b>Dioxyde d'azote (NO2)</b>")
                st.plotly_chart(f5, use_container_width=True)
    else:
        st.info("Aucune donnée disponible pour cette sélection.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CORRÉLATIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    if not air_fil.empty and not wth_fil.empty:
        merged = pd.merge_asof(
            air_fil.sort_values("ts"),
            wth_fil.sort_values("ts"),
            on="ts", suffixes=("", "_w")
        ).dropna(subset=["aqi", "temperature"])

        c1, c2 = st.columns(2)
        with c1:
            fig = px.scatter(merged, x="temperature", y="aqi", color="city",
                             trendline="ols", color_discrete_sequence=COLORS,
                             labels={"temperature": "Température (°C)", "aqi": "AQI", "city": "Ville"})
            fig.update_layout(**PL, height=320, title="<b>AQI vs Température</b>")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig2 = px.scatter(merged, x="humidity", y="aqi", color="city",
                              trendline="ols", color_discrete_sequence=COLORS,
                              labels={"humidity": "Humidité (%)", "aqi": "AQI", "city": "Ville"})
            fig2.update_layout(**PL, height=320, title="<b>AQI vs Humidité</b>")
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<div class="sec-hdr">Matrice de corrélation</div>', unsafe_allow_html=True)
        cols_c  = ["aqi","pm25","pm10","o3","no2","temperature","humidity","wind_speed","pressure"]
        corr    = merged[[c for c in cols_c if c in merged.columns]].corr().round(2)
        fig3    = px.imshow(
            corr, text_auto=True, aspect="auto",
            color_continuous_scale=[[0,"#DC2626"],[0.5,"#F8FAFC"],[1,"#2563EB"]],
            zmin=-1, zmax=1
        )
        fig3.update_layout(
            paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
            font=dict(family="Plus Jakarta Sans", color="#475569"),
            margin=dict(l=10,r=10,t=10,b=10), height=380
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Pas assez de données pour les corrélations.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ALERTES
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    if not air_df.empty:
        al = air_df[air_df["city"].isin(cities_sel) & (air_df["is_alert"] == True)].copy()

        c1, c2, c3 = st.columns(3)
        c1.metric("Total alertes",   len(al))
        c2.metric("Villes touchées", al["city"].nunique() if not al.empty else 0)
        c3.metric("AQI max relevé",  f"{int(al['aqi'].max())}" if not al.empty else "—")

        if al.empty:
            st.success("✅ Aucune alerte détectée pour la sélection en cours.")
        else:
            ca, cb = st.columns([2, 1])
            with ca:
                st.markdown('<div class="sec-hdr">Historique des alertes</div>', unsafe_allow_html=True)
                fig = px.scatter(al, x="ts", y="aqi", color="city", size="aqi",
                                 color_discrete_sequence=COLORS,
                                 labels={"ts":"","aqi":"AQI","city":"Ville"})
                fig.add_hline(y=100, line_dash="dot", line_color="#D97706")
                fig.update_layout(**PL, height=300)
                st.plotly_chart(fig, use_container_width=True)
            with cb:
                st.markdown('<div class="sec-hdr">Par ville</div>', unsafe_allow_html=True)
                cnt  = al.groupby("city").size().reset_index(name="n")
                fig2 = px.bar(cnt, x="n", y="city", orientation="h", color="n",
                              color_continuous_scale=[[0,"#FEF3C7"],[1,"#DC2626"]],
                              labels={"n":"Alertes","city":""})
                fig2.update_layout(**PL, height=300, showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

            st.markdown('<div class="sec-hdr">Détail des alertes</div>', unsafe_allow_html=True)
            disp = al[["ts","city","aqi","aqi_label","pm25","dominant_pol"]]\
                     .sort_values("ts", ascending=False).head(100).copy()
            disp.columns = ["Date","Ville","AQI","Niveau","PM2.5 (µg/m³)","Polluant principal"]
            disp["Date"] = disp["Date"].dt.strftime("%d/%m/%Y  %Hh%M")
            st.dataframe(disp, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — INDICATEURS
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="sec-hdr">Échelle AQI — Seuils OMS</div>', unsafe_allow_html=True)
    oms = pd.DataFrame({
        "Niveau":          ["Bon","Modéré","Mauvais (groupes sensibles)","Mauvais","Très mauvais","Dangereux"],
        "AQI":             ["0 – 50","51 – 100","101 – 150","151 – 200","201 – 300","300+"],
        "Indicateur":      ["🟢","🟡","🟠","🔴","🟣","⚫"],
        "Qui est concerné":["Personne","Personnes très sensibles","Asthmatiques, enfants, personnes âgées",
                            "Population générale","Effets graves sur tous","Urgence sanitaire"],
    })
    st.dataframe(oms, use_container_width=True, hide_index=True)

    st.markdown('<div class="sec-hdr">Polluants mesurés</div>', unsafe_allow_html=True)
    polluants = [
        ("PM2.5", "#DC2626", "Particules fines < 2.5 µm",
         "Pénètrent profondément dans les poumons et le sang. Principal indicateur de risque sanitaire. Sources : trafic, industrie, chauffage au bois. <strong>Seuil OMS : 15 µg/m³/an.</strong>"),
        ("PM10", "#D97706", "Particules < 10 µm",
         "Irritent les voies respiratoires supérieures. Sources : poussières de route, chantiers, agriculture. <strong>Seuil OMS : 45 µg/m³/an.</strong>"),
        ("O3", "#2563EB", "Ozone troposphérique",
         "Polluant secondaire formé par réaction solaire. Pic en été, en milieu de journée. Irrite les poumons. <strong>Seuil OMS : 100 µg/m³ sur 8h.</strong>"),
        ("NO2", "#7C3AED", "Dioxyde d'azote",
         "Émis par les moteurs thermiques et la combustion. Aggrave l'asthme et les bronchites. <strong>Seuil OMS : 25 µg/m³ sur 24h.</strong>"),
    ]
    c1, c2 = st.columns(2)
    for i, (nom, col, sub, desc) in enumerate(polluants):
        with (c1 if i % 2 == 0 else c2):
            st.markdown(f"""
            <div class="card" style="border-left:4px solid {col}; margin-bottom:.8rem">
                <div style="font-size:1.15rem;font-weight:800;color:{col};margin-bottom:.2rem">{nom}</div>
                <div style="font-size:.75rem;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:.06em;margin-bottom:.5rem">{sub}</div>
                <div style="font-size:.875rem;color:#1E293B;line-height:1.65">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="sec-hdr">Indicateurs météorologiques</div>', unsafe_allow_html=True)
    meteo_items = [
        ("🌡️  Température (°C)", "Favorise la formation d'ozone en été. Une hausse de température augmente la réactivité chimique des polluants."),
        ("💧  Humidité (%)",      "Une humidité élevée peut piéger les particules fines et amplifier la pollution locale."),
        ("💨  Vent (km/h)",       "Le vent disperse et dilue les polluants. Un vent faible (< 5 km/h) favorise l'accumulation."),
        ("🌧️  Précipitations (mm)","La pluie lessive l'atmosphère : elle fait chuter les concentrations de PM2.5 et NO2 rapidement."),
        ("🔵  Pression (hPa)",    "Un anticyclone (haute pression) bloque les échanges verticaux d'air — risque élevé de pic de pollution."),
    ]
    for nom, desc in meteo_items:
        st.markdown(f"""
        <div style="display:flex;gap:1rem;align-items:flex-start;
                    padding:.8rem 0;border-bottom:1.5px solid #DDE1EE">
            <div style="min-width:200px;font-weight:700;color:#0F172A;font-size:.875rem">{nom}</div>
            <div style="color:#475569;font-size:.875rem;line-height:1.6">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="sec-hdr">Sources de données</div>', unsafe_allow_html=True)
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown("""
        <div class="card">
            <div style="font-size:1rem;font-weight:800;color:#2563EB">AQICN</div>
            <div style="font-size:.78rem;color:#475569;margin-top:.3rem">World Air Quality Index Project</div>
            <div style="font-size:.75rem;color:#94A3B8;margin-top:.15rem">aqicn.org</div>
        </div>
        """, unsafe_allow_html=True)
    with sc2:
        st.markdown("""
        <div class="card">
            <div style="font-size:1rem;font-weight:800;color:#2563EB">Open-Meteo</div>
            <div style="font-size:.78rem;color:#475569;margin-top:.3rem">Données météo open source</div>
            <div style="font-size:.75rem;color:#94A3B8;margin-top:.15rem">open-meteo.com</div>
        </div>
        """, unsafe_allow_html=True)
    with sc3:
        st.markdown("""
        <div class="card">
            <div style="font-size:1rem;font-weight:800;color:#2563EB">Collecte automatique</div>
            <div style="font-size:.78rem;color:#475569;margin-top:.3rem">Chaque jour à 16h00</div>
            <div style="font-size:.75rem;color:#94A3B8;margin-top:.15rem">Stockage Supabase — EU (RGPD)</div>
        </div>
        """, unsafe_allow_html=True)