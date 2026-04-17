<h1 align="center">📊 Dashboard de Saneamento Básico</h1>
<h3 align="center">Projeto Acadêmico · Business Intelligence com Streamlit & Pandas</h3>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" />
  <img src="https://img.shields.io/badge/CSV-Data-217346?style=for-the-badge&logo=files&logoColor=white" />
  <img src="https://img.shields.io/badge/Status-Concluído-green?style=for-the-badge" />
</p>

---

## 📌 Objetivo Acadêmico

Este projeto foi desenvolvido como **atividade prática da disciplina de Business Intelligence**, com o objetivo de construir um **dashboard interativo** utilizando exclusivamente **Streamlit e Pandas**, sem dependências de bibliotecas de visualização externas como Plotly ou Altair. A proposta abrange:

- Carregar e tratar dados reais de saneamento básico a partir de um arquivo CSV
- Lidar com formatação numérica brasileira (ponto como milhar, vírgula como decimal)
- Transformar dados no formato **largo** para **longo** com `df.melt()`
- Construir gráficos interativos com `st.line_chart` e `st.bar_chart`
- Aplicar filtros dinâmicos no sidebar por **indicador** e **localidade**

> 📚 **Disciplina:** Business Intelligence  
> 🏫 **Contexto:** Faculdade — Atividade Prática  
> 👤 **Aluno:** yLipew

---

## 📁 Estrutura do Repositório

```
📦 Aula-Streamlit
 ├── 📄 dashboard_app.py   # Script principal do dashboard Streamlit
 └── 📊 consulta.csv       # Dataset com indicadores de saneamento por localidade (2014–2024)
```

---

## 📊 Dataset — `consulta.csv`

O arquivo contém dados sobre o **Percentual da População Atendida com Água** em diferentes cidades (Localidades) ao longo dos anos de **2014 a 2024**.

| Campo        | Tipo   | Exemplo                        |
|--------------|--------|--------------------------------|
| `Variável`   | Texto  | `Pop. Atendida com Água (%)`   |
| `Localidade` | Texto  | `Abadiânia`                    |
| `2014`       | Float  | `85,3`                         |
| `2015`       | Float  | `87,0`                         |
| `...`        | Float  | ...                            |
| `2024`       | Float  | `92,1`                         |

> ⚠️ Os valores numéricos no CSV usam **ponto como separador de milhar** e **vírgula como separador decimal** (padrão brasileiro). O script realiza a limpeza automaticamente.

---

## 🔄 Fluxo do Projeto

```
consulta.csv (formato largo)
        │
        ▼
  Limpeza numérica
  (remove pontos, troca vírgulas)
        │
        ▼
  df.melt() → formato longo
  colunas: Variável | Localidade | Ano | Valor
        │
        ▼
  Filtros no Sidebar
  (Indicador + Localidades)
        │
        ▼
  Dashboard Streamlit
  ├── line_chart  → Evolução temporal
  ├── bar_chart   → Média por localidade
  └── bar_chart   → Situação no ano mais recente
```

---

## ⚙️ Configuração do Ambiente

### Pré-requisitos

- Python 3.8+
- `consulta.csv` na mesma pasta que `dashboard_app.py`

### 1️⃣ Instale as dependências

```bash
pip install streamlit pandas
```

---

### 2️⃣ Execute o dashboard

> ⚠️ **Atenção:** O Streamlit **não pode** ser executado com `python dashboard_app.py`. É obrigatório usar o comando abaixo:

```bash
streamlit run dashboard_app.py
```

Ou, se estiver na pasta do projeto:

```bash
cd "c:\Users\Aluno\Documents\Felipe-Mendonça\Business Inteligence\Streamlit\Aula-Streamlit-13-04\"
streamlit run dashboard_app.py
```

O dashboard abrirá automaticamente no navegador em `http://localhost:8501`.

---

## 📄 Código — `dashboard_app.py`

```python
import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Dashboard Saneamento")

# --- CARREGAMENTO E TRATAMENTO DE DADOS ---
df = pd.read_csv("consulta.csv", sep=";")

# 1. Identificar colunas de anos automaticamente
cols_anos = [col for col in df.columns if col.isdigit()]

# 2. Limpeza Numérica (padrão BR: ponto = milhar, vírgula = decimal)
for col in cols_anos:
    df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df[col] = pd.to_numeric(df[col], errors='coerce')

# 3. Transformar de formato "Largo" para "Longo" (Melt)
df_melted = df.melt(id_vars=['Variável', 'Localidade'],
                    value_vars=cols_anos,
                    var_name='Ano',
                    value_name='Valor')

df_melted["Ano"] = pd.to_numeric(df_melted["Ano"])

# --- FILTROS NO SIDEBAR ---
st.sidebar.header("Configurações do Dashboard")

variavel_selecionada = st.sidebar.selectbox(
    "Selecione o Indicador",
    df_melted["Variável"].unique()
)

cidades_disponiveis = df_melted["Localidade"].unique()
cidades_selecionadas = st.sidebar.multiselect(
    "Selecione as Localidades",
    options=cidades_disponiveis,
    default=cidades_disponiveis[:3]
)

df_filtered = df_melted[
    (df_melted["Variável"] == variavel_selecionada) &
    (df_melted["Localidade"].isin(cidades_selecionadas))
]

# --- DASHBOARD ---
st.title(variavel_selecionada)

# 1. Gráfico de Linha: Evolução Temporal
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
    ano_max = df_filtered["Ano"].max()
    st.subheader(f"Situação no ano {ano_max}")
    dados_recentes = df_filtered[df_filtered["Ano"] == ano_max].set_index("Localidade")["Valor"]
    st.bar_chart(dados_recentes)

with st.expander("Ver base de dados filtrada"):
    st.dataframe(df_filtered)
```

---

## 🛠️ Tecnologias Utilizadas

<p>
  <img src="https://img.shields.io/badge/Python_3.8+-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white" />
</p>

| Tecnologia  | Versão  | Finalidade                                           |
|-------------|---------|------------------------------------------------------|
| Python      | 3.8+    | Linguagem principal                                  |
| Streamlit   | latest  | Interface web interativa e gráficos nativos          |
| Pandas      | latest  | Leitura, limpeza, transformação e agregação dos dados|

---

<p align="center">
  Desenvolvido para fins acadêmicos · Disciplina de Business Intelligence
</p>
