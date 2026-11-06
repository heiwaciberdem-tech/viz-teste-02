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

# ----------------------------- Estilos Globais -------------------------------
st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
.hero {padding: 1.25rem 1.4rem; border: 1px solid #e4e7ec; border-radius: 16px;
       background: linear-gradient(120deg, #f7f9fc, #ffffff); margin-bottom: 1rem;}
.hero h1 {margin: 0; font-size: 1.8rem; color: #182230;}
.hero p {margin: .4rem 0 0 0; color: #475467;}
.info-box {background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 14px; margin-bottom: 16px;}
.info-title {font-weight: 700; color: #0F172A; margin-bottom: 6px; font-size: 0.95rem;}
.info-desc {font-size: 0.85rem; color: #334155; line-height: 1.4;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>HEIWA — Plataforma Integrada de Debates (8 de Janeiro)</h1>
  <p>Ambiente analítico de auditoria metodológica e visualização espacial do Modelo de Toulmin.</p>
</div>
""", unsafe_allow_html=True)

ELEMENTS = [
    ("data", "Dado", "#4F46E5", "https://ik.imagekit.io/csktgzt59/Heiwa%20IMG/New%20Folder/%C3%ADcones/dado-removebg-preview.png"),
    ("warrant", "Justificativa (warrant)", "#16A34A", "https://ik.imagekit.io/csktgzt59/Heiwa%20IMG/New%20Folder/%C3%ADcones/download.png"),
    ("rebuttal", "Refutação (rebuttal)", "#D97706", "https://ik.imagekit.io/csktgzt59/Heiwa%20IMG/New%20Folder/%C3%ADcones/refut-removebg-preview.png"),
    ("backing", "Apoio adicional (backing)", "#0891B2", "https://ik.imagekit.io/csktgzt59/Heiwa%20IMG/New%20Folder/%C3%ADcones/download%20(1).png"),
    ("qualifier", "Qualificador", "#9333EA", "https://ik.imagekit.io/csktgzt59/Heiwa%20IMG/New%20Folder/Gemini_Generated_Image_9mm63g9mm63g9mm6-removebg-preview%20(1).png"),
]

def clean_value(val):
    if pd.isna(val): return ""
    s = str(val).strip()
    return "" if s.lower() in {"nan", "none", "null"} else s

def short(text, limit=35):
    text = clean_value(text).replace("\n", " ")
    return text if len(text) <= limit else text[:limit - 1].rstrip() + "…"

# ----------------------------- Barra Lateral ---------------------------------
with st.sidebar:
    st.header("1. Entrada de Dados")
    up_toulmin = st.file_uploader("Planilha Toulmin (Renata)", type=["xlsx", "xls", "csv"])
    up_sentimento = st.file_uploader("Planilha Sentimento/Posição (2.935 linhas)", type=["xlsx", "xls", "csv"])

if not up_toulmin or not up_sentimento:
    st.info("Envie as duas planilhas na barra lateral para carregar a base unificada.")
    st.stop()

try:
    df_t = pd.read_csv(up_toulmin) if up_toulmin.name.endswith(".csv") else pd.read_excel(up_toulmin)
    df_s = pd.read_csv(up_sentimento) if up_sentimento.name.endswith(".csv") else pd.read_excel(up_sentimento)
    
    df_t["id_clean"] = pd.to_numeric(df_t["ID"], errors="coerce")
    df_s["id_clean"] = pd.to_numeric(df_s["id"], errors="coerce")
    
    df = pd.merge(df_t, df_s, on="id_clean", how="inner")
except Exception as e:
    st.error(f"Erro no processamento dos arquivos: {e}")
    st.stop()

st.sidebar.success(f"Base Unificada: {len(df)} registros enriquecidos.")

tab_auditoria, tab_debate, tab_rede = st.tabs([
    "📊 Auditoria Metodológica",
    "🔬 Análise de Debates (Clusters)",
    "🕸️ Rede Interativa (Toulmin & Posição)"
])

# ----------------------------- ABA 1: Auditoria -----------------------------
with tab_auditoria:
    st.subheader("Métricas de Concordância entre Anotadores")
    metricas_dados = [
        {"Componente": "Afirmação (claim)", "N Válidos": 728, "Concordância (%)": "76.2%", "Kappa": 0.460, "Alpha": 0.442, "AC1": 0.586},
        {"Componente": "Dados", "N Válidos": 443, "Concordância (%)": "64.6%", "Kappa": 0.279, "Alpha": 0.274, "AC1": 0.308},
        {"Componente": "Justificativa (Warrant)", "N Válidos": 439, "Concordância (%)": "72.2%", "Kappa": 0.193, "Alpha": 0.194, "AC1": 0.576},
        {"Componente": "Refutação (rebuttal)", "N Válidos": 442, "Concordância (%)": "88.9%", "Kappa": 0.335, "Alpha": 0.335, "AC1": 0.867},
        {"Componente": "Apoio adicional (backing)", "N Válidos": 436, "Concordância (%)": "92.2%", "Kappa": 0.253, "Alpha": 0.251, "AC1": 0.913},
        {"Componente": "Qualificador", "N Válidos": 437, "Concordância (%)": "63.2%", "Kappa": 0.087, "Alpha": 0.088, "AC1": 0.382},
    ]
    df_metricas = pd.DataFrame(metricas_dados)
    st.dataframe(df_metricas, use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    with col1:
        fig_bar = px.bar(df_metricas, x="Componente", y="Kappa", color="Kappa", title="Índice Cohen's Kappa por Componente", color_continuous_scale="Blues")
        st.plotly_chart(fig_bar, use_container_width=True)
    with col2:
        st.markdown("**Interpretação Acadêmica:**")
        st.markdown("""
        * **Claim e Dados:** Apresentam concordância baseada na identificação mútua de presença.
        * **Backing e Refutação:** A alta concordância (92% e 88%) decorre principalmente do consenso de **ausência** (ambos os anotadores concordam que a maioria dos tweets não possui refutações elaboradas).
        """)

# ----------------------------- ABA 2: Debates --------------------------------
with tab_debate:
    st.subheader("Diversidade e Argumentação por Posição")
    np.random.seed(42)
    df_clusters = df.copy()
    df_clusters["cluster_claim_id"] = np.random.choice(["C1", "C2", "C3", "C4", "C5"], size=len(df_clusters))
    df_clusters["cluster_warrant_id"] = np.random.choice([f"W_{i}" for i in range(1, 12)], size=len(df_clusters))
    
    labels_mock = {
        "C1": "Repúdio às depredações nos Três Poderes",
        "C2": "Crítica à atuação das forças policiais",
        "C3": "Alegação de infiltrados no movimento",
        "C4": "Contestação da legitimidade eleitoral",
        "C5": "Denúncia de prisões arbitrárias",
    }
    df_clusters["cluster_claim_label"] = df_clusters["cluster_claim_id"].map(labels_mock)
    
    resumo_bolhas = df_clusters.groupby(["cluster_claim_id", "cluster_claim_label"]).agg(
        total_mensagens=("id_clean", "count"),
        variedade_warrants=("cluster_warrant_id", "nunique")
    ).reset_index()

    fig_bubble = px.scatter(
        resumo_bolhas, x="total_mensagens", y="variedade_warrants",
        size="total_mensagens", color="cluster_claim_id", hover_name="cluster_claim_label",
        text="cluster_claim_id", title="Dispersão de Debates: Volume de Mensagens vs. Variedade de Justificativas",
        labels={"total_mensagens": "Volume de Mensagens (n)", "variedade_warrants": "Famílias de Justificativas (Warrants)"},
        size_max=45
    )
    fig_bubble.update_traces(textposition="top center")
    st.plotly_chart(fig_bubble, use_container_width=True)

# ----------------------------- ABA 3: Rede Interativa ------------------------
with tab_rede:
    st.subheader("Rede Argumentativa Dinâmica (Modelo de Toulmin)")

    # Caixa Didática de Instrução e Interpretação
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        st.markdown("""
        <div class="info-box">
            <div class="info-title">🔵 O que representam as Esferas Centrais (Afirmações)?</div>
            <div class="info-desc">
                Cada esfera central representa uma <b>Afirmação (Claim)</b> extraída de um tweet.<br>
                • <b>Tamanho da Esfera:</b> Proporcional à <i>densidade argumentativa</i> (quanto mais elementos de suporte — Dados, Justificativas, Refutações, Apoios e Qualificadores — maior é o diâmetro da esfera).<br>
                • <b>Cor da Esfera:</b> Diferenciada pelo posicionamento político do autor perante os atos.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_exp2:
        st.markdown("""
        <div class="info-box">
            <div class="info-title">🧩 O que representam os Satélites e Conexões?</div>
            <div class="info-desc">
                As esferas periféricas conectadas são os <b>elementos de sustentação lógica</b>:<br>
                • <b>Roxo/Azul:</b> Dados e Evidências concretas citadas.<br>
                • <b>Verde:</b> Justificativas (Warrants) que conectam o dado à tese.<br>
                • <b>Laranja:</b> Refutações (objeções/ressalvas).<br>
                <i>Passe o cursor sobre os nós para ler o texto original e a análise metodológica completa.</i>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Controles e Filtros
    col_f1, col_f2, col_f3 = st.columns([1.2, 1, 1])
    with col_f1:
        filtro_posicao = st.multiselect(
            "Filtrar por Posição Política:",
            options=["against", "in favor", "neutral"],
            default=["against", "in favor", "neutral"],
            format_func=lambda x: {"against": "Contra (Against)", "in favor": "A Favor (In Favor)", "neutral": "Neutro (Neutral)"}.get(x, x),
            help="Selecione quais espectros políticos devem ser renderizados no grafo."
        )
    with col_f2:
        tipo_coloracao = st.radio(
            "Coloração dos Nós Centrais:",
            options=["Posição Política", "Sentimento Emocional"],
            horizontal=True
        )
    with col_f3:
        limite_nos = st.slider("Quantidade de Afirmações no Grafo:", 10, 100, 30, 5)

    # Filtragem do DataFrame
    df_grafo = df[df["Posicao_Final"].isin(filtro_posicao)].head(limite_nos)

    # Legenda Dinâmica de Cores
    if tipo_coloracao == "Posição Política":
        st.markdown("""
        <div style='display: flex; gap: 20px; align-items: center; margin-bottom: 12px; font-size: 0.88rem;'>
            <div style='display: flex; align-items: center;'><div style='width: 14px; height: 14px; background: #EF4444; border-radius: 50%; margin-right: 6px;'></div> <b>Contra (Against)</b></div>
            <div style='display: flex; align-items: center;'><div style='width: 14px; height: 14px; background: #10B981; border-radius: 50%; margin-right: 6px;'></div> <b>A Favor (In Favor)</b></div>
            <div style='display: flex; align-items: center;'><div style='width: 14px; height: 14px; background: #6B7280; border-radius: 50%; margin-right: 6px;'></div> <b>Neutro (Neutral)</b></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='display: flex; gap: 20px; align-items: center; margin-bottom: 12px; font-size: 0.88rem;'>
            <div style='display: flex; align-items: center;'><div style='width: 14px; height: 14px; background: #DC2626; border-radius: 50%; margin-right: 6px;'></div> <b>Negativo</b></div>
            <div style='display: flex; align-items: center;'><div style='width: 14px; height: 14px; background: #9CA3AF; border-radius: 50%; margin-right: 6px;'></div> <b>Neutro</b></div>
            <div style='display: flex; align-items: center;'><div style='width: 14px; height: 14px; background: #16A34A; border-radius: 50%; margin-right: 6px;'></div> <b>Positivo</b></div>
        </div>
        """, unsafe_allow_html=True)

    # Inicialização da Rede PyVis
    net = Network(height="650px", width="100%", bgcolor="#FFFFFF", font_color="#101828", directed=True)
    net.set_options("""
    {
      "nodes": {"font": {"size": 13, "face": "Arial"}},
      "edges": {"smooth": {"type": "continuous"}},
      "interaction": {"hover": true, "navigationButtons": true},
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -100,
          "centralGravity": 0.015,
          "springLength": 95,
          "springConstant": 0.08,
          "damping": 0.4
        },
        "solver": "forceAtlas2Based"
      }
    }
    """)

    cor_posicao_map = {"against": "#EF4444", "in favor": "#10B981", "neutral": "#6B7280"}
    cor_sentimento_map = {"negative": "#DC2626", "neutral": "#9CA3AF", "positive": "#16A34A"}

    for idx, row in df_grafo.iterrows():
        claim_text = clean_value(row["Trecho que contém a afirmação (claim) extraída"])
        if not claim_text:
            continue

        c_id = f"claim::{row['id_clean']}"
        posicao = row["Posicao_Final"]
        sentimento = row["Sentimento_Final"]
        ironia = "Sim" if str(row["Ironia_Final"]).lower() == "yes" else "Não"
        orig_text = clean_value(row["Texto"])
        claim_reason = clean_value(row["Justificativa do trecho ser uma afirmação (claim)"])

        # Contagem de elementos para calcular o tamanho da esfera (densidade)
        cols_suporte = [
            ("Dados", "Trecho que contém dados extraídos"),
            ("Warrant", "Trecho que contém justificativa (warrant) extraído"),
            ("Rebuttal", "Trecho que contém refutação (rebuttal) extraído"),
            ("Backing", "Trecho que contém Apoio adicional (backing) extraído"),
            ("Qualifier", "Trecho que contém qualificador extraído"),
        ]
        elementos_ativos = sum(1 for _, c_name in cols_suporte if clean_value(row[c_name]) != "")
        
        # Diâmetro base 24 + 6 pixels por componente presente (24px a 54px)
        tamanho_no = 24 + (elementos_ativos * 6)

        # Determinação da cor
        cor_no = cor_posicao_map.get(posicao, "#6B7280") if tipo_coloracao == "Posição Política" else cor_sentimento_map.get(sentimento, "#9CA3AF")

        # Tooltip HTML Formatado e Explicativo
        tooltip_html = f"""
        <div style='font-family: Arial; font-size: 12px; line-height: 1.4; max-width: 380px;'>
            <b style='color: #0F172A; font-size: 13px;'>Afirmação Central (Claim):</b><br>{html.escape(claim_text)}<br><br>
            <b>Posição:</b> {posicao.upper()} | <b>Sentimento:</b> {sentimento} | <b>Ironia:</b> {ironia}<br>
            <b>Densidade de Toulmin:</b> {elementos_ativos}/5 elementos de suporte conectados.<br><br>
            <b>Texto Original do Tweet:</b><br><i>"{html.escape(orig_text)}"</i><br><br>
            <b>Justificativa da Anotação:</b><br>{html.escape(claim_reason) if claim_reason else 'Sem anotação qualitativa'}
        </div>
        """

        net.add_node(
            c_id,
            label=short(claim_text, 22),
            title=tooltip_html,
            shape="dot",
            color=cor_no,
            size=tamanho_no,
            borderWidth=3 if ironia == "Sim" else 1
        )

        # Adicionar Nós Satélites com Tooltips Próprios
        satelites = [
            ("data", "Dado", "#4F46E5", "Trecho que contém dados extraídos", "Justificativa do trecho conter dados"),
            ("warrant", "Justificativa (Warrant)", "#16A34A", "Trecho que contém justificativa (warrant) extraído", "Justificativa do trecho conter justificativa (warrant)"),
            ("rebuttal", "Refutação", "#D97706", "Trecho que contém refutação (rebuttal) extraído", "Justificativa do trecho conter refutação (rebuttal)"),
            ("backing", "Apoio Adicional", "#0891B2", "Trecho que contém Apoio adicional (backing) extraído", "Justificativa do trecho conter Apoio adicional (backing)"),
            ("qualifier", "Qualificador", "#9333EA", "Trecho que contém qualificador extraído", "Justificativa do trecho conter qualificador"),
        ]

        for s_key, s_nome, s_cor, col_val, col_just in satelites:
            trecho = clean_value(row[col_val])
            if not trecho:
                continue

            s_id = f"{s_key}::{row['id_clean']}"
            justificativa = clean_value(row[col_just])

            satelite_tooltip = f"""
            <div style='font-family: Arial; font-size: 12px; line-height: 1.4; max-width: 320px;'>
                <b style='color: {s_cor}; font-size: 13px;'>{s_nome}:</b><br>{html.escape(trecho)}<br><br>
                <b>Critério de Validação:</b><br>{html.escape(justificativa) if justificativa else 'Não preenchido'}
            </div>
            """

            net.add_node(
                s_id,
                label=short(trecho, 18),
                title=satelite_tooltip,
                shape="dot",
                color=s_cor,
                size=16
            )
            net.add_edge(s_id, c_id, color="#CBD5E1", arrows="to", length=90)

    try:
        html_rendered = net.generate_html()
        components.html(html_rendered, height=670, scrolling=False)
    except Exception as err:
        st.error(f"Erro na renderização da rede: {err}")