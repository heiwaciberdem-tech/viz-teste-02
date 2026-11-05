import html
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

st.set_page_config(
    page_title="HEIWA | Análise de Argumentos e Debates",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- Estilos ---------------------------------------
st.markdown(
    """
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
.hero {padding: 1.25rem 1.4rem; border: 1px solid #e4e7ec; border-radius: 16px;
       background: linear-gradient(120deg, #f7f9fc, #ffffff); margin-bottom: 1rem;}
.hero h1 {margin: 0; font-size: 1.8rem; color: #182230;}
.hero p {margin: .4rem 0 0 0; color: #475467;}
div[data-testid="stMetric"] {border: 1px solid #eaecf0; padding: 12px 14px; border-radius: 12px;}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="hero">
  <h1>HEIWA — Plataforma Integrada de Debates (8 de Janeiro)</h1>
  <p>Ambiente de validação metodológica acadêmica e exploração de redes argumentativas.</p>
</div>
""",
    unsafe_allow_html=True,
)

ELEMENTS = [
    (
        "claim",
        "Afirmação (claim)",
        "#D92D20",
        "image",
        "https://ik.imagekit.io/csktgzt59/Heiwa%20IMG/New%20Folder/%C3%ADcones/afir-removebg-preview.png",
    ),
    (
        "data",
        "Dado",
        "#4F46E5",
        "image",
        "https://ik.imagekit.io/csktgzt59/Heiwa%20IMG/New%20Folder/%C3%ADcones/dado-removebg-preview.png",
    ),
    (
        "warrant",
        "Justificativa (warrant)",
        "#16A34A",
        "image",
        "https://ik.imagekit.io/csktgzt59/Heiwa%20IMG/New%20Folder/%C3%ADcones/download.png",
    ),
    (
        "rebuttal",
        "Refutação (rebuttal)",
        "#D97706",
        "image",
        "https://ik.imagekit.io/csktgzt59/Heiwa%20IMG/New%20Folder/%C3%ADcones/refut-removebg-preview.png",
    ),
    (
        "backing",
        "Apoio adicional (backing)",
        "#0891B2",
        "image",
        "https://ik.imagekit.io/csktgzt59/Heiwa%20IMG/New%20Folder/%C3%ADcones/download%20(1).png",
    ),
    (
        "qualifier",
        "Qualificador",
        "#9333EA",
        "image",
        "https://ik.imagekit.io/csktgzt59/Heiwa%20IMG/New%20Folder/Gemini_Generated_Image_9mm63g9mm63g9mm6-removebg-preview%20(1).png",
    ),
]


def clean_value(val):
  if pd.isna(val):
    return ""
  s = str(val).strip()
  return "" if s.lower() in {"nan", "none", "null"} else s


def short(text, limit=40):
  text = clean_value(text).replace("\n", " ")
  return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


# ----------------------------- Barra Lateral (Uploads) -----------------------
with st.sidebar:
  st.header("1. Entrada de Arquivos")
  up_toulmin = st.file_uploader(
      "Planilha Toulmin (Renata)", type=["xlsx", "xls", "csv"]
  )
  up_sentimento = st.file_uploader(
      "Planilha Sentimento/Posição (2.935 linhas)", type=["xlsx", "xls", "csv"]
  )
  st.caption("Faça o upload de ambas para ativar a integração completa.")

if not up_toulmin or not up_sentimento:
  st.info(
      "Por favor, envie ambos os arquivos na barra lateral para carregar a base"
      " unificada."
  )
  st.stop()

# Leitura e Tratamento
try:
  df_t = (
      pd.read_csv(up_toulmin)
      if up_toulmin.name.endswith(".csv")
      else pd.read_excel(up_toulmin)
  )
  df_s = (
      pd.read_csv(up_sentimento)
      if up_sentimento.name.endswith(".csv")
      else pd.read_excel(up_sentimento)
  )

  df_t["id_clean"] = pd.to_numeric(df_t["ID"], errors="coerce")
  df_s["id_clean"] = pd.to_numeric(df_s["id"], errors="coerce")

  df = pd.merge(df_t, df_s, on="id_clean", how="inner")
except Exception as e:
  st.error(f"Erro ao processar as planilhas: {e}")
  st.stop()

st.sidebar.success(
    f"Base Unificada com Sucesso! {len(df)} argumentos enriquecidos."
)

# ----------------------------- Abas Principais -------------------------------
tab_auditoria, tab_debate, tab_rede = st.tabs([
    "📊 Auditoria Metodológica",
    "🔬 Análise de Debates (Toulmin & Clusters)",
    "🕸️ Rede Interativa (PyVis)",
])

# ----------------------------- ABA 1: Auditoria -----------------------------
with tab_auditoria:
  st.subheader("Métricas de Concordância entre Anotadores (Ground Truth)")
  st.markdown(
      "Validação formal dos índices estatísticos exigidos para a banca de"
      " mestrado."
  )

  # Dados oficiais extraídos do documento da Renata
  metricas_dados = [
      {
          "Componente": "Afirmação (claim)",
          "N Válidos": 728,
          "Concordância (%)": "76.2%",
          "Kappa": 0.460,
          "Alpha": 0.442,
          "AC1": 0.586,
      },
      {
          "Componente": "Dados",
          "N Válidos": 443,
          "Concordância (%)": "64.6%",
          "Kappa": 0.279,
          "Alpha": 0.274,
          "AC1": 0.308,
      },
      {
          "Componente": "Justificativa (Warrant)",
          "N Válidos": 439,
          "Concordância (%)": "72.2%",
          "Kappa": 0.193,
          "Alpha": 0.194,
          "AC1": 0.576,
      },
      {
          "Componente": "Refutação (rebuttal)",
          "N Válidos": 442,
          "Concordância (%)": "88.9%",
          "Kappa": 0.335,
          "Alpha": 0.335,
          "AC1": 0.867,
      },
      {
          "Componente": "Apoio adicional (backing)",
          "N Válidos": 436,
          "Concordância (%)": "92.2%",
          "Kappa": 0.253,
          "Alpha": 0.251,
          "AC1": 0.913,
      },
      {
          "Componente": "Qualificador",
          "N Válidos": 437,
          "Concordância (%)": "63.2%",
          "Kappa": 0.087,
          "Alpha": 0.088,
          "AC1": 0.382,
      },
  ]
  df_metricas = pd.DataFrame(metricas_dados)
  st.dataframe(df_metricas, use_container_width=True, hide_index=True)

  col1, col2 = st.columns(2)
  with col1:
    fig_bar = px.bar(
        df_metricas,
        x="Componente",
        y="Kappa",
        color="Kappa",
        title="Índice Cohen's Kappa por Componente",
        color_continuous_scale="Blues",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

  with col2:
    st.markdown("**Origem da Concordância (Sim vs. Não)**")
    st.markdown("""
        * **Consenso sobre Presença:** Predomina em **Claim** (82.9%) e **Dados** (69.4%).
        * **Consenso sobre Ausência:** Domina os componentes de suporte, como **Backing** (95.9%) e **Refutação** (93.9%).
        * *Conclusão Metodológica:* A concordância global elevada em refutação/backing decorre da concordância de que a maioria dos tweets não os possui.
        """)

# ----------------------------- ABA 2: Análise de Debates --------------------
with tab_debate:
  st.subheader("Estrutura do Debate: Afirmações vs. Justificativas")

  # Mock de preparação de clusters para quando a Julia entregar os dados
  np.random.seed(42)
  df_clusters = df.copy()
  df_clusters["cluster_claim_id"] = np.random.choice(
      ["C1", "C2", "C3", "C4", "C5"], size=len(df_clusters)
  )
  df_clusters["cluster_warrant_id"] = np.random.choice(
      [f"W_{i}" for i in range(1, 12)], size=len(df_clusters)
  )

  labels = {
      "C1": "Repúdio às depredações / Terrorismo",
      "C2": "Críticas à atuação das Forças de Segurança",
      "C3": "Alegação de infiltrados no movimento",
      "C4": "Contestação da legitimidade eleitoral",
      "C5": "Denúncia de violação de direitos e prisões",
  }
  df_clusters["cluster_claim_label"] = df_clusters["cluster_claim_id"].map(
      labels
  )

  # Gráfico de Bolhas (Slide 7 da Renata)
  resumo_bolhas = (
      df_clusters.groupby(["cluster_claim_id", "cluster_claim_label"])
      .agg(
          total_mensagens=("id_clean", "count"),
          variedade_warrants=("cluster_warrant_id", "nunique"),
      )
      .reset_index()
  )

  fig_bubble = px.scatter(
      resumo_bolhas,
      x="total_mensagens",
      y="variedade_warrants",
      size="total_mensagens",
      color="cluster_claim_id",
      hover_name="cluster_claim_label",
      text="cluster_claim_id",
      title="Diversidade de Justificativas por Família de Afirmações (Mock Julia)",
      labels={
          "total_mensagens": "Volume de Mensagens (n)",
          "variedade_warrants": "Variedade de Justificativas (Warrants)",
      },
      size_max=45,
  )
  fig_bubble.update_traces(textposition="top center")
  st.plotly_chart(fig_bubble, use_container_width=True)

  st.markdown("---")
  st.subheader("Completude Argumentativa por Posição Política")
  col_pos1, col_pos2 = st.columns([1, 1.2])

  with col_pos1:
    fig_pos = px.pie(
        df,
        names="Posicao_Final",
        title="Distribuição da Posição Política",
        color="Posicao_Final",
        color_discrete_map={
            "against": "#EF4444",
            "in favor": "#10B981",
            "neutral": "#6B7280",
        },
    )
    st.plotly_chart(fig_pos, use_container_width=True)

  with col_pos2:
    # Contagem de dados presentes por posição
    df["tem_dados"] = (
        df["Trecho que contém dados extraídos"].apply(clean_value) != ""
    )
    cruzamento = (
        df.groupby(["Posicao_Final", "tem_dados"])
        .size()
        .reset_index(name="contagem")
    )
    fig_cruz = px.bar(
        cruzamento,
        x="Posicao_Final",
        y="contagem",
        color="tem_dados",
        barmode="group",
        title="Uso de Dados Reais por Posição Política",
        labels={"tem_dados": "Possui Dado Concreto?", "contagem": "Volume"},
    )
    st.plotly_chart(fig_cruz, use_container_width=True)

# ----------------------------- ABA 3: Rede PyVis ----------------------------
with tab_rede:
  st.subheader("Navegação Espacial na Rede Argumentativa")

  col_f1, col_f2, col_f3 = st.columns(3)
  with col_f1:
    filtro_posicao = st.multiselect(
        "Filtrar por Posição:",
        options=df["Posicao_Final"].unique(),
        default=df["Posicao_Final"].unique(),
    )
  with col_f2:
    modo_calor = st.checkbox("Mapa de Calor (Sentimento)", value=False)
  with col_f3:
    max_nos = st.slider("Limite de Afirmações no Grafo:", 10, 100, 35)

  df_rede = df[df["Posicao_Final"].isin(filtro_posicao)].head(max_nos)

  net = Network(
      height="600px",
      width="100%",
      bgcolor="#FFFFFF",
      font_color="#101828",
      directed=True,
  )
  net.set_options("""
    {
      "nodes": {"font": {"size": 13, "face": "Arial"}},
      "edges": {"smooth": {"type": "continuous"}},
      "physics": {
        "forceAtlas2Based": {"gravitationalConstant": -90, "springLength": 90, "springConstant": 0.08},
        "solver": "forceAtlas2Based"
      }
    }
    """)

  for idx, row in df_rede.iterrows():
    c_id = f"claim::{row['id_clean']}"
    claim_txt = clean_value(
        row["Trecho que contém a afirmação (claim) extraída"]
    )
    if not claim_txt:
      continue

    sentimento = row["Sentimento_Final"]
    posicao = row["Posicao_Final"]
    tooltip = (
        f"<b>Afirmação:</b> {html.escape(claim_txt)}<br><b>Posição:</b>"
        f" {posicao}<br><b>Sentimento:</b> {sentimento}"
    )

    if modo_calor:
      cor_map = {
          "negative": "#DC2626",
          "neutral": "#9CA3AF",
          "positive": "#16A34A",
      }
      net.add_node(
          c_id,
          label=short(claim_txt, 22),
          title=tooltip,
          shape="dot",
          color=cor_map.get(sentimento, "#9CA3AF"),
          size=28,
      )
    else:
      net.add_node(
          c_id,
          label=short(claim_txt, 22),
          title=tooltip,
          shape="image",
          image=ELEMENTS[0][4],
          size=28,
      )

    # Conectar Dado se existir
    dado_txt = clean_value(row["Trecho que contém dados extraídos"])
    if dado_txt:
      d_id = f"data::{row['id_clean']}"
      net.add_node(
          d_id,
          label=short(dado_txt, 16),
          title=f"<b>Dado:</b> {html.escape(dado_txt)}",
          shape="dot" if modo_calor else "image",
          image=ELEMENTS[1][4],
          color="#4F46E5",
          size=18,
      )
      net.add_edge(d_id, c_id, color="#D0D5DD", arrows="to")

    # Conectar Justificativa se existir
    warr_txt = clean_value(
        row["Trecho que contém justificativa (warrant) extraído"]
    )
    if warr_txt:
      w_id = f"warr::{row['id_clean']}"
      net.add_node(
          w_id,
          label=short(warr_txt, 16),
          title=f"<b>Warrant:</b> {html.escape(warr_txt)}",
          shape="dot" if modo_calor else "image",
          image=ELEMENTS[2][4],
          color="#16A34A",
          size=18,
      )
      net.add_edge(w_id, c_id, color="#D0D5DD", arrows="to")

  try:
    html_net = net.generate_html()
    components.html(html_net, height=620, scrolling=False)
  except Exception as err:
    st.error(f"Erro na renderização da rede: {err}")