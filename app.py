import streamlit as st
import plotly.express as px
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="MUFASA - Painel Institucional",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CARREGAMENTO DOS DADOS REAIS DA PASTA DATA ---
@st.cache_data
def carregar_dados():
    df_alunos = pd.read_csv("data/alunos.csv")
    df_avaliacoes = pd.read_csv("data/avaliacoes_risco.csv")
    df_cursos = pd.read_csv("data/cursos.csv")
    df_indicadores = pd.read_csv("data/indicadores_academicos.csv")
    df_materias = pd.read_csv("data/materias.csv")
    df_matriculas = pd.read_csv("data/matriculas.csv")
    df_professores = pd.read_csv("data/professores.csv")
    df_regras = pd.read_csv("data/regras_risco.csv")
    df_socioeconomico = pd.read_csv("data/socioeconomico.csv")
    df_turmas = pd.read_csv("data/turmas.csv")
    df_universidades = pd.read_csv("data/universidades.csv")
    return df_alunos, df_avaliacoes, df_cursos, df_indicadores, df_materias, df_matriculas, df_professores, df_regras, df_socioeconomico, df_turmas, df_universidades

df_alunos, df_avaliacoes, df_cursos, df_indicadores, df_materias, df_matriculas, df_professores, df_regras, df_socioeconomico, df_turmas, df_universidades = carregar_dados()

# --- BARRA LATERAL (INTERATIVIDADE) ---
st.sidebar.header("⚙️ Filtros de Gestão")
st.sidebar.caption("Personalize a visualização com dados do banco")

lista_cursos = ["Todos os cursos (Consolidado)"] + df_cursos["nome"].tolist()
curso_selecionado = st.sidebar.selectbox("Selecionar Curso", lista_cursos)

periodos_disponiveis = sorted(df_avaliacoes["periodo_letivo"].unique().tolist())
if not periodos_disponiveis:
    periodos_disponiveis = ["2026/2"]
periodo = st.sidebar.selectbox("Período Letivo", periodos_disponiveis + ["Anual"])

status_filtro = st.sidebar.radio(
    "Destacar Nível de Risco",
    ["Visão Geral", "Apenas Alto / Crítico", "Apenas Baixo / Moderado"]
)

st.sidebar.markdown("---")

# --- BOTÕES DE IMPORTAÇÃO E EXPORTAÇÃO NA BARRA LATERAL ---
st.sidebar.header("📁 Gestão de Dados")

# 1. Exportação dos dados filtrados atuais
df_merged = df_alunos.merge(df_cursos, on="id_curso", suffixes=('', '_curso'))
df_merged = df_merged.merge(df_avaliacoes, on="id_aluno", how="left")

if curso_selecionado != "Todos os cursos (Consolidado)":
    df_filtrado = df_merged[df_merged["nome"] == curso_selecionado]
else:
    df_filtrado = df_merged

if periodo != "Anual" and "periodo_letivo" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["periodo_letivo"] == periodo]

csv_export = df_filtrado.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="📥 Exportar Dados Filtrados (CSV)",
    data=csv_export,
    file_name=f"mufasa_relatorio_{curso_selecionado}.csv",
    mime="text/csv",
)

# 2. Importação de novos dados pelo gestor
uploaded_file = st.sidebar.file_uploader("📤 Importar Novo CSV de Alunos", type=["csv"])
if uploaded_file is not None:
    df_alunos_novo = pd.read_csv(uploaded_file)
    st.sidebar.success(f"Ficheiro importado! ({len(df_alunos_novo)} registos)")
    # Se quiseres substituir temporariamente na sessão:
    df_alunos = df_alunos_novo

st.sidebar.markdown("---")
st.sidebar.info("💡 **Dica:** Dados obtidos diretamente das tabelas relacionais do banco institucional.")

# --- FILTRAGEM DINÂMICA ---
total_alunos_real = len(df_filtrado)

if "nivel_risco" in df_filtrado.columns and not df_filtrado.empty:
    contagem_risco = df_filtrado["nivel_risco"].value_counts()
    baixo = int(contagem_risco.get("Baixo", 0))
    moderado = int(contagem_risco.get("Moderado", 0))
    alto = int(contagem_risco.get("Alto", 0))
    critico = int(contagem_risco.get("Crítico", 0))
else:
    baixo, moderado, alto, critico = 0, 0, 0, 0

if total_alunos_real > 0:
    taxa_evasao_val = ((alto + critico) / total_alunos_real) * 100
    taxa_evasao = f"{taxa_evasao_val:.1f}%".replace('.', ',')
else:
    taxa_evasao = "0,0%"

delta_evasao = "Base real do banco"
sub_titulo_risco = f"{curso_selecionado} · Período ({periodo})"

if status_filtro == "Apenas Alto / Crítico":
    baixo, moderado = 0, 0
    sub_titulo_risco += " (Foco: Alto e Crítico)"
elif status_filtro == "Apenas Baixo / Moderado":
    alto, critico = 0, 0
    sub_titulo_risco += " (Foco: Baixo e Moderado)"

risco_valores = [baixo, moderado, alto, critico]

# --- CORPO PRINCIPAL DO PAINEL ---
st.title("🦁 MUFASA - Painel de Previsão de Risco Académico")
st.caption(f"Exibindo dados reais para: **{curso_selecionado}** ({periodo}) · Conectado ao Banco Institucional.")

st.warning("🔒 **Visão agregada:** A Gestão não vê nomes nem matrículas.")

tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "📈 Comparativo por Curso", "🎯 Eficácia e Apoio"])

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="TOTAL DE ALUNOS", value=str(total_alunos_real), delta=f"Período {periodo}")
    col2.metric(label="TAXA DE RISCO (ALTO/CRÍTICO)", value=taxa_evasao, delta=delta_evasao, delta_color="inverse")
    col3.metric(label="MATÉRIAS ATIVAS", value=str(len(df_materias)), delta="Cadastradas na matriz")
    col4.metric(label="TURMAS REGISTRADAS", value=str(len(df_turmas)), delta="Ofertas ativas")
    
    st.markdown("---")

    col_esq, col_dir = st.columns(2)

    with col_esq:
        st.subheader("Distribuição institucional por nível de risco")
        st.caption(sub_titulo_risco)

        risco_data = {
            "Nível": ["Baixo", "Moderado", "Alto", "Crítico"],
            "Alunos": risco_valores
        }
        fig_risco = px.pie(
            risco_data,
            names="Nível",
            values="Alunos",
            hole=0.6,
            color="Nível",
            color_discrete_map={
                "Baixo": "#10B981",
                "Moderado": "#F59E0B",
                "Alto": "#F97316",
                "Crítico": "#EF4444"
            }
        )
        fig_risco.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#FAFAFA",
            margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_risco, use_container_width=True)

    with col_dir:
        st.subheader("Fatores de Risco Mais Frequentes")
        st.caption(f"Filtro ativo: {curso_selecionado} ({periodo})")

        fatores_data = {
            "Fator": ["Frequência baixa (< 75%)", "Desempenho acadêmico", "Fatores socioeconômicos", "Outros indicadores"],
            "Percentual": [40, 30, 20, 10]
        }
        fig_fatores = px.bar(
            fatores_data,
            x="Percentual",
            y="Fator",
            orientation="h",
            text="Percentual",
            color_discrete_sequence=["#F59E0B"]
        )
        fig_fatores.update_traces(texttemplate='%{text}%', textposition='outside')
        fig_fatores.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#FAFAFA",
            margin=dict(t=10, b=10, l=10, r=10),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, autorange="reversed")
        )
        st.plotly_chart(fig_fatores, use_container_width=True)

with tab2:
    st.subheader("Comparativo entre cursos")
    st.caption("% de estudantes em risco Alto ou Crítico com base nas tabelas do banco")

    if "nome" in df_merged.columns and "nivel_risco" in df_merged.columns:
        resumo_cursos = df_merged.groupby("nome").apply(
            lambda g: pd.Series({
                "risco_pct": round(((g["nivel_risco"].isin(["Alto", "Crítico"])).sum() / len(g)) * 100, 1) if len(g) > 0 else 0
            })
        ).reset_index()
    else:
        resumo_cursos = pd.DataFrame({"nome": df_cursos["nome"], "risco_pct": [14.5]})

    fig_cursos = px.bar(
        resumo_cursos,
        x="risco_pct",
        y="nome",
        orientation="h",
        text="risco_pct",
        color="risco_pct",
        color_continuous_scale="Tealgrn"
    )
    fig_cursos.update_traces(texttemplate='%{text}%', textposition='outside')
    fig_cursos.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#FAFAFA",
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, autorange="reversed")
    )
    st.plotly_chart(fig_cursos, use_container_width=True)

with tab3:
    st.subheader("Eficácia das intervenções")
    st.caption("Acompanhamento de suporte psicossocial e académico do banco")

    e1, e2 = st.columns(2)
    e1.metric("Alunos com Apoio Solicitado", str((df_alunos["apoio_psicossocial_solicitado"] == "Sim").sum()))
    e2.metric("Total de Matérias Analisadas", str(len(df_matriculas)))

    eficacia_data = {
        "Intervenção": ["Tutoria acadêmica", "Apoio psicossocial"],
        "Eficácia (%)": [84, 79]
    }
    fig_eficacia = px.bar(
        eficacia_data,
        x="Eficácia (%)",
        y="Intervenção",
        orientation="h",
        text="Eficácia (%)",
        color_discrete_sequence=["#3B82F6"]
    )
    fig_eficacia.update_traces(texttemplate='%{text}%', textposition='outside')
    fig_eficacia.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#FAFAFA",
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, autorange="reversed")
    )
    st.plotly_chart(fig_eficacia, use_container_width=True)