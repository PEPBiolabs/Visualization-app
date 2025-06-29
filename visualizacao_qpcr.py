try:
    import streamlit as st
except:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
    import streamlit as st

import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Visualização Consolidada qPCR", layout="wide")
st.title("🔬 Visualização Interativa dos Resultados de qPCR")

uploaded_file = st.file_uploader("Envie o CSV consolidado dos resultados", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Corrige cabeçalhos e vírgulas como separador decimal
    df.columns = df.columns.str.strip().str.replace('\ufeff', '')
    if "Nota" in df.columns:
        df["Nota"] = df["Nota"].astype(str).str.replace(",", ".", regex=False).astype(float)
    else:
        st.error("A coluna 'Nota' não foi encontrada no arquivo CSV.")
        st.stop()

    st.sidebar.markdown("### 🎚️ Filtros")

    # Filtro por faixa de nota
    nota_min = st.sidebar.slider("Nota mínima", float(df["Nota"].min()), 10.0, 7.0, 0.1)
    nota_max = st.sidebar.slider("Nota máxima", nota_min, 10.0, 10.0, 0.1)
    df = df[(df["Nota"] >= nota_min) & (df["Nota"] <= nota_max)]

    # Filtros adicionais por variáveis categóricas, se existirem
    for var in ["cepa", "aditivos na enzima", "indução", "tampão da enzima", "condição da enzima", "data"]:
        if var in df.columns:
            opcoes = df[var].dropna().unique().tolist()
            selecao = st.sidebar.multiselect(f"Filtrar por {var}", options=opcoes, default=opcoes)
            df = df[df[var].isin(selecao)]

    # Controles para gráfico
    col_x = st.sidebar.selectbox("Eixo X", df.columns, index=df.columns.get_loc("Nota") if "Nota" in df.columns else 0)
    col_y = st.sidebar.selectbox("Eixo Y", df.columns, index=df.columns.get_loc("Nota") if "Nota" in df.columns else 1)
    cor = st.sidebar.selectbox("Colorir por", df.columns, index=df.columns.get_loc("classificação") if "classificação" in df.columns else 0)

    st.markdown("### 📈 Gráfico de dispersão")
    fig = px.scatter(df, x=col_x, y=col_y, color=cor,
                     hover_data=df.columns,
                     title="Dispersão filtrada das reações de qPCR")
    st.plotly_chart(fig, use_container_width=True)

    # Frequência das variáveis categóricas
    st.markdown("## 📊 Frequências das variáveis no grupo filtrado")

    variaveis_para_analise = [
        "Cepa",
        "Aditivos na enzima",
        "Indução",
        "Tampão da enzima",
        "Condição da enzima",
        "Data",
        "Classificação"
    ]

    for var in variaveis_para_analise:
        if var in df.columns:
            st.markdown(f"**{var.capitalize()}**")
            freq = df[var].value_counts(dropna=False).reset_index()
            freq.columns = [var, "Frequência"]
            st.dataframe(freq)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Baixar CSV filtrado", data=csv, file_name="grupo_filtrado.csv", mime="text/csv")
