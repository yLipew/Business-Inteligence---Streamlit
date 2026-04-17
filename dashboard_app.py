import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Dashboard Saneamento")

# --- CARREGAMENTO E TRATAMENTO DE DADOS ---
df = pd.read_csv("consulta.csv", sep=";", encoding="latin1")

# 1. Identificar colunas de anos
cols_anos = [col for col in df.columns if col.isdigit()]

# 2. Limpeza Numérica
for col in cols_anos:
    # Remove pontos de milhar, troca vírgula por ponto e converte para número
    df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df[col] = pd.to_numeric(df[col], errors='coerce')

# 3. Transformar de "Largo" para "Longo" (Melt)
df_melted = df.melt(id_vars=['Variável', 'Localidade'], 
                    value_vars=cols_anos, 
                    var_name='Ano', 
                    value_name='Valor')

df_melted["Ano"] = pd.to_numeric(df_melted["Ano"])

# --- FILTROS NO SIDEBAR ---
st.sidebar.header("Configurações do Dashboard")

# Filtro 1: Selecionar a Variável (Evita o erro de duplicatas no pivot)
lista_variaveis = df_melted["Variável"].unique()
variavel_selecionada = st.sidebar.selectbox("Selecione o Indicador", lista_variaveis)

# Filtro 2: Selecionar Cidades
cidades_disponiveis = df_melted["Localidade"].unique()
cidades_selecionadas = st.sidebar.multiselect(
    "Selecione as Localidades", 
    options=cidades_disponiveis,
    default=cidades_disponiveis[:3]
)

# Aplicar filtros
df_filtered = df_melted[
    (df_melted["Variável"] == variavel_selecionada) & 
    (df_melted["Localidade"].isin(cidades_selecionadas))
]

# --- DASHBOARD ---
st.title(variavel_selecionada)

# 1. Gráfico de Linha (Evolução Temporal)
# Usamos pivot_table com aggfunc='mean' para garantir que não haverá erro de duplicatas
st.subheader("Evolução ao longo dos anos")
if not df_filtered.empty:
    chart_data = df_filtered.pivot_table(
        index='Ano', 
        columns='Localidade', 
        values='Valor', 
        aggfunc='mean'
    )
    st.line_chart(chart_data)
else:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Média por Localidade (Período)")
    ranking = df_filtered.groupby("Localidade")["Valor"].mean().sort_values(ascending=False)
    st.bar_chart(ranking)

with col2:
    # Mostrar o ano mais recente disponível
    ano_max = df_filtered["Ano"].max()
    st.subheader(f"Situação no ano {ano_max}")
    dados_recentes = df_filtered[df_filtered["Ano"] == ano_max].set_index("Localidade")["Valor"]
    st.bar_chart(dados_recentes)

# Exibir os dados brutos filtrados
with st.expander("Ver base de dados filtrada"):
    st.dataframe(df_filtered)