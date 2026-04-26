import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Explorador MPG",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

      html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
        background-color: #101827;
        color: #fce7f3;
      }
      #MainMenu {visibility: hidden;}
      footer {visibility: hidden;}

      .hero {
        background: linear-gradient(135deg, #111827 0%, #1e1b4b 55%, #831843 100%);
        border-bottom: 2px solid #f9a8d4;
        padding: 2rem 2.5rem 1.5rem;
        margin-bottom: 1.5rem;
      }
      .hero h1 {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 4rem;
        letter-spacing: .12em;
        color: #f9a8d4;
        margin: 0 0 .25rem;
        line-height: 1;
      }
      .hero p {
        font-family: 'IBM Plex Mono', monospace;
        font-size: .8rem;
        color: #f9a8d4;
        margin: 0;
        letter-spacing: .08em;
      }

      .metric-card {
        flex: 1;
        background: #1e293b;
        border: 1px solid #334155;
        border-top: 3px solid #f9a8d4;
        padding: 1rem 1.25rem;
        border-radius: 2px;
      }
      .metric-card .label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: .65rem;
        color: #666;
        letter-spacing: .1em;
        text-transform: uppercase;
        margin-bottom: .3rem;
      }
      .metric-card .value {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 2.2rem;
        color: #f9a8d4;
        line-height: 1;
      }
      .metric-card .sub {
        font-size: .75rem;
        color: #555;
        margin-top: .2rem;
      }

      .section-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: .7rem;
        letter-spacing: .2em;
        text-transform: uppercase;
        color: #f9a8d4;
        border-bottom: 1px solid #2a2a2a;
        padding-bottom: .4rem;
        margin-bottom: 1rem;
      }

      section[data-testid="stSidebar"] {
      background: #111827 !important;
      border-right: 1px solid #334155;
      }
      section[data-testid="stSidebar"] * { color: #e8e0d0 !important; }

      .js-plotly-plot { border: 1px solid #1e1e1e; border-radius: 2px; }

      .insight {
        background: #1e1b4b;
        border-left: 3px solid #f9a8d4;
        padding: .6rem 1rem;
        font-size: .8rem;
        color: #aaa;
        margin-top: .5rem;
        font-family: 'IBM Plex Mono', monospace;
        border-radius: 0 2px 2px 0;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

CARD_BG   = "#1e293b"
AMBER     = "#f9a8d4"
GRID_CLR  = "#334155"
TEXT_CLR  = "#fce7f3"

PLOT_LAYOUT = dict(
    paper_bgcolor=CARD_BG,
    plot_bgcolor=CARD_BG,
    font=dict(family="IBM Plex Mono, monospace", color=TEXT_CLR, size=11),
    xaxis=dict(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR, linecolor=GRID_CLR),
    yaxis=dict(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR, linecolor=GRID_CLR),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#2a2a2a"),
    margin=dict(l=50, r=30, t=55, b=50),
)

ORIGIN_PALETTE = {
    "usa": "#f9a8d4",
    "europe": "#93c5fd",
    "japan": "#c084fc"
}

ORIGIN_ES = {"usa": "EE.UU.", "europe": "Europa", "japan": "Japón"}

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/mpg.csv"
    try:
        df = pd.read_csv(url)
    except Exception:
        import io
        raw = """mpg,cylinders,displacement,horsepower,weight,acceleration,model_year,origin,name
18,8,307,130,3504,12,70,usa,chevrolet
15,8,350,165,3693,11.5,70,usa,buick
18,8,318,150,3436,11,70,usa,plymouth
16,8,304,150,3433,12,70,usa,amc
17,8,302,140,3449,10.5,70,usa,ford
28,4,140,90,2264,15.5,71,usa,chevrolet
19,6,232,100,2634,13,70,usa,amc
14,8,440,215,4312,8.5,70,usa,plymouth
14,8,455,225,4425,10,70,usa,pontiac
15,8,390,190,3850,8.5,70,usa,amc
26,4,97,46,1835,20.5,70,europe,volkswagen
24,4,107,90,2430,14.5,70,europe,toyota
22,4,104,95,2375,17.5,70,europe,opel
18,6,198,95,3102,16.5,74,usa,dodge
21,6,199,90,2648,15,70,usa,amc
25,4,110,87,2672,17.5,70,europe,peugeot
27,4,97,88,2130,14.5,71,japan,toyota
26,4,97,54,2254,23.5,72,europe,volkswagen
25,4,140,83,2639,17,75,usa,ford
24,4,113,95,2278,15.5,72,japan,toyota"""
        df = pd.read_csv(io.StringIO(raw))
    df = df.dropna(subset=["horsepower", "displacement"])
    df["horsepower"] = pd.to_numeric(df["horsepower"], errors="coerce")
    df = df.dropna(subset=["horsepower"])
    df["origen"] = df["origin"].map(ORIGIN_ES).fillna(df["origin"])
    return df

df_full = load_data()

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("### 🔧 Filtros")
    st.markdown("---")

    origins_available = sorted(df_full["origin"].dropna().unique().tolist())
    origins_es = [ORIGIN_ES.get(o, o) for o in origins_available]

    selected_origins_es = st.multiselect(
        "Origen",
        options=origins_es,
        default=origins_es,
    )
    es_to_en = {v: k for k, v in ORIGIN_ES.items()}
    selected_origins = [es_to_en.get(o, o) for o in selected_origins_es]

    cyl_options = sorted(df_full["cylinders"].dropna().unique().tolist())
    selected_cyls = st.multiselect(
        "Cilindros",
        options=[int(c) for c in cyl_options],
        default=[int(c) for c in cyl_options],
    )

    yr_min = int(df_full["model_year"].min())
    yr_max = int(df_full["model_year"].max())
    year_range = st.slider(
        "Año del modelo",
        min_value=yr_min,
        max_value=yr_max,
        value=(yr_min, yr_max),
    )

    st.markdown("---")
    st.markdown(
        "<p style='font-family:IBM Plex Mono,monospace;font-size:.65rem;"
        "color:#444;letter-spacing:.08em;'>DATASET MPG · UCI / SEABORN</p>",
        unsafe_allow_html=True,
    )

# ── FILTRO ──
df = df_full[
    df_full["origin"].isin(selected_origins)
    & df_full["cylinders"].isin(selected_cyls)
    & df_full["model_year"].between(*year_range)
].copy()

# ── HEADER ──
st.markdown(
    """
    <div class="hero">
      <h1>Explorador MPG</h1>
      <p>ECONOMÍA DE COMBUSTIBLE · RENDIMIENTO DEL MOTOR · ORIGEN GEOGRÁFICO — 1970–1982</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── MÉTRICAS ──
avg_mpg  = df["mpg"].mean()
avg_hp   = df["horsepower"].mean()
avg_disp = df["displacement"].mean()
n_cars   = len(df)

c1, c2, c3, c4 = st.columns(4)
for col, label, val, sub in [
    (c1, "VEHÍCULOS", f"{n_cars:,}", "en la selección actual"),
    (c2, "MPG PROMEDIO", f"{avg_mpg:.1f}", "millas por galón"),
    (c3, "POTENCIA PROM.", f"{avg_hp:.0f}", "caballos de fuerza"),
    (c4, "CILINDRADA PROM.", f"{avg_disp:.0f}", "pulgadas cúbicas"),
]:
    col.markdown(
        f"""<div class="metric-card">
          <div class="label">{label}</div>
          <div class="value">{val}</div>
          <div class="sub">{sub}</div>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── GRÁFICO 1: DISPERSIÓN ──
st.markdown('<div class="section-title">01 · Cilindrada vs Potencia</div>', unsafe_allow_html=True)

color_map_es = {ORIGIN_ES.get(o, o): ORIGIN_PALETTE.get(o, "#aaa") for o in origins_available}

fig_scatter = px.scatter(
    df,
    x="displacement",
    y="horsepower",
    color="origen",
    color_discrete_map=color_map_es,
    size="mpg",
    size_max=18,
    hover_data={"name": True, "cylinders": True, "model_year": True, "mpg": True, "origen": False},
    labels={
        "displacement": "Cilindrada (pulg. cúb.)",
        "horsepower": "Potencia (CV)",
        "origen": "Origen",
        "mpg": "MPG",
        "name": "Modelo",
        "cylinders": "Cilindros",
        "model_year": "Año",
    },
    title="Tamaño del Motor × Potencia",
    trendline=None,
)
fig_scatter.update_traces(
    marker=dict(opacity=0.75, line=dict(width=0.5, color="#0d0d0d")),
    selector=dict(mode="markers"),
)
fig_scatter.update_layout(
    **PLOT_LAYOUT,
    title_font=dict(family="Bebas Neue, sans-serif", size=20, color=AMBER),
    height=430,
)
st.plotly_chart(fig_scatter, use_container_width=True)
st.markdown(
    '<div class="insight">💡 Los motores con mayor cilindrada producen consistentemente más potencia, '
    "pero a un alto costo en eficiencia de combustible. Los vehículos de EE.UU. dominan la zona de alta cilindrada.</div>",
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# ── GRÁFICOS 2 y 3 ──
col_bar, col_box = st.columns([1, 1], gap="medium")

with col_bar:
    st.markdown('<div class="section-title">02 · Vehículos por Origen</div>', unsafe_allow_html=True)

    origin_counts = (
        df.groupby("origen", as_index=False)
        .agg(count=("origen", "count"), avg_mpg=("mpg", "mean"))
        .sort_values("count", ascending=False)
    )

    fig_bar = go.Figure()
    for _, row in origin_counts.iterrows():
        en_key = es_to_en.get(row["origen"], row["origen"])
        fig_bar.add_trace(
            go.Bar(
                x=[row["origen"]],
                y=[row["count"]],
                name=row["origen"],
                marker_color=ORIGIN_PALETTE.get(en_key, "#aaa"),
                customdata=[[row["avg_mpg"]]],
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Vehículos: %{y}<br>"
                    "MPG promedio: %{customdata[0]:.1f}<extra></extra>"
                ),
            )
        )

    fig_bar.update_layout(
        **PLOT_LAYOUT,
        showlegend=False,
        title="Cantidad de Vehículos por Región",
        title_font=dict(family="Bebas Neue, sans-serif", size=20, color=AMBER),
        height=370,
        bargap=0.35,
        xaxis_title="Origen",
        yaxis_title="Cantidad",
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown(
        '<div class="insight">💡 EE.UU. domina en volumen; Japón lidera en eficiencia de combustible.</div>',
        unsafe_allow_html=True,
    )

with col_box:
    st.markdown('<div class="section-title">03 · Distribución de MPG por Origen</div>', unsafe_allow_html=True)

    fig_box = go.Figure()
    for origin in origins_available:
        origen_es = ORIGIN_ES.get(origin, origin)
        subset = df[df["origin"] == origin]["mpg"]
        if subset.empty:
            continue
        fig_box.add_trace(
            go.Box(
                y=subset,
                name=origen_es,
                marker_color=ORIGIN_PALETTE.get(origin, "#aaa"),
                line_color=ORIGIN_PALETTE.get(origin, "#aaa"),
                fillcolor={"usa": "rgba(249,168,212,0.18)", "europe": "rgba(147,197,253,0.18)", "japan": "rgba(192,132,252,0.18)"}.get(origin, "rgba(170,170,170,0.15)"),
                boxmean="sd",
            )
        )

    fig_box.update_layout(
        **PLOT_LAYOUT,
        showlegend=False,
        title="Dispersión de Economía de Combustible",
        title_font=dict(family="Bebas Neue, sans-serif", size=20, color=AMBER),
        yaxis_title="Millas por Galón (MPG)",
        height=370,
    )
    st.plotly_chart(fig_box, use_container_width=True)
    st.markdown(
        '<div class="insight">💡 Los autos japoneses muestran la mediana de MPG más alta y la menor varianza.</div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── GRÁFICO 4: LÍNEA DE TENDENCIA ──
st.markdown('<div class="section-title">04 · Tendencia de Eficiencia a lo Largo del Tiempo</div>', unsafe_allow_html=True)

trend_df = (
    df.groupby(["model_year", "origen"], as_index=False)["mpg"]
    .mean()
    .rename(columns={"mpg": "mpg_promedio"})
)
trend_df["año"] = "19" + trend_df["model_year"].astype(str)

fig_line = px.line(
    trend_df,
    x="año",
    y="mpg_promedio",
    color="origen",
    color_discrete_map=color_map_es,
    markers=True,
    labels={"año": "Año del Modelo", "mpg_promedio": "MPG Promedio", "origen": "Origen"},
    title="MPG Promedio por Región · 1970–1982",
)
fig_line.update_traces(line_width=2.5, marker_size=7)
fig_line.update_layout(
    **PLOT_LAYOUT,
    title_font=dict(family="Bebas Neue, sans-serif", size=20, color=AMBER),
    height=360,
)
st.plotly_chart(fig_line, use_container_width=True)
st.markdown(
    '<div class="insight">💡 Tras la crisis del petróleo de 1973, todas las regiones apostaron por mayor eficiencia. '
    "Japón y Europa mantuvieron una ventaja constante en MPG durante toda la década.</div>",
    unsafe_allow_html=True,
)
