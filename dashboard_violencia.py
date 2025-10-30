import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import glob
import plotly.express as px

# Título e descrição
st.set_page_config(page_title="Violência contra Mulheres - MG", layout="wide")
st.title("Dashboard ODS 5 - Igualdade de Gênero")
st.markdown("Violência contra Mulheres em Minas Gerais (2009–2025)")

# Carregar todos os CSVs automaticamente
@st.cache_data
def carregar_dados():
    arquivos = glob.glob("dados_violencia_mulheres_ses_*.csv")
    dfs = []
    for arq in arquivos:
        ano = arq.split("_")[-1].split(".")[0]
        df = pd.read_csv(arq, sep=";", decimal=",")
        df["ano"] = int(ano)
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)

dados = carregar_dados()

# Filtro de anos
anos = sorted(dados["ano"].unique())
anos_selecionados = st.multiselect(
    "Selecione os anos que deseja analisar:",
    options=anos,
    default=anos
)

dados_filtrados = dados[dados["ano"].isin(anos_selecionados)]

st.write(f"Total de registros selecionados: {len(dados_filtrados):,}")

# Fazendo gráficos fixos para a área de análises
plt.hist(dados["nu_idade_n"], bins=20, color='purple', edgecolor='white')
plt.title("Distribuição das Idades")
plt.xlabel("Idade")
plt.ylabel("Frequência")




# Dividindo em abas
tab1, tab3, tab2 = st.tabs(["Visualizações", "Análises", "Dados Brutos"])

# Aba 1 com os gráficos customizaveis
with tab1:
    st.header("Gráficos")
    fig = px.histogram(dados_filtrados, x="nu_idade_n", nbins=40,
                       title="Distribuição das Idades (Filtradas)")
    st.plotly_chart(fig, use_container_width=True)

# Outro gráfico(tipos)
    st.markdown("""Tipos de violências""")
    tipos_agressao = {
        "Fisica": dados_filtrados["viol_fisic"].value_counts().get("Sim", 0),
        "Psicologica": dados_filtrados["viol_psico"].value_counts().get("Sim", 0),
        "Sexual": dados_filtrados["viol_sexu"].value_counts().get("Sim", 0)
    }

    fig_agressao = px.bar(
        x=list(tipos_agressao.keys()),
        y=list(tipos_agressao.values()),
        text=list(tipos_agressao.values()),
        labels={"x": "Tipo de Agressão", "y": "Quantidade de Casos"},
        title="Distribuição dos Tipos de Agressão"
    )
    fig_agressao.update_traces(marker_color=['#d32f2f', '#7b1fa2', '#1976d2'], textposition="outside")
    st.plotly_chart(fig_agressao, use_container_width=True)
# Casos totais por ano
    for col in [c for c in dados_filtrados.columns if "viol" in c.lower()]:
        dados_filtrados[col] = dados_filtrados[col].map({"Sim": 1, "Não": 0})

    # Agrupa por ano e soma os casos de cada tipo
    casos_por_ano = (
        dados_filtrados.groupby("ano")[["viol_fisic", "viol_psico", "viol_sexu"]]
        .sum()
        .reset_index()
    )

    casos_long = casos_por_ano.melt(
        id_vars="ano",
        value_vars=["viol_fisic", "viol_psico", "viol_sexu"],
        var_name="Tipo de Violência",
        value_name="Casos"
    )

    fig = px.line(
        casos_long,
        x="ano",
        y="Casos",
        color="Tipo de Violência",
        markers=True,
        title="Evolução dos tipos de violência ao longo dos anos"
    )
    st.plotly_chart(fig, use_container_width=True)


# Aba 3 com análises escritas
with tab3:
    st.header("Análises")
    st.markdown("# Dados numéricos")
    st.pyplot(plt)
    st.markdown("""
    > Com esse grande fluxo de dados é interessante ver os dados numéricos como idade e seus detalhes, como média(30 anos), mediana(28) e os quartis(18, 28, 40). Com eles é possível perceber que **25% das vítimas tem menos de 18 anos**, e que 75% das mulheres que sofrem agressões tem menos de 40 anos, estão longe da terceira idade, que evidencia que idosas tem tendências à sofrer menos agressões ou enfrentam mais dificuldades em buscar ajuda e cadastrar as agressões.
    > É interessante também destacar que a diferença da média de idades e a mediana são similares, que evidenciam poucos dados extremos, que são obstáculos para as análises de dados. Além disso a média entre o primeiro e terceiro quartil cai bem no meio dos dados, provando que mesmo tendo alguns dados extremos a abundância de dados equilibra as médias.
    """)
    #Gráfico ligado ao sexo dos autores
    contagem = dados["autor_sexo"].value_counts()
    plt.figure(figsize=(6, 6))
    plt.pie(
        contagem,
        labels=contagem.index,
        autopct="%1.1f%%",
        colors=['#f518db', '#4542f5', '#292827', '#981dd1']
    )
    st.markdown("### Dados não numéricos")
    plt.title("Distribuição dos agressores por gênero")
    plt.tight_layout()
    st.pyplot(plt)
    st.markdown("""
    > A porcentagem de mulheres e homens como agressores tem uma diferença significativa, porém, infelizmente, não é nada chocante, pois é conhecimento popular que no Brasil a cada 15 minutos uma mulher é espancada.
    """)
    plt.figure(figsize=(6, 6))
    # Gráfico referente a sexualidades
    contagem = dados["orient_sex"].value_counts()
    plt.pie(
        contagem,
        labels=contagem.index,
        autopct="%1.1f%%",
        colors=['#000f91', '#7c7c7d', '#5e565d', '#280137', '#D60270']
        # Azul - heterossexual, emprestado do significado das cores da bandeira bissexual
        # Cinza - ignorado/nao aplica, falta de cor para remeter a falta de respostas
        # Roxo - homossexual, cor da bandeira labrys, importante bandeira pro movimento lesbico apesar de nao se utilizar mais
        # Rosa - bissexual, cor que sobrou da bandeira bissexual
    )
    plt.title("Distribuição das vítimas por Sexualidade")
    plt.tight_layout()
    st.pyplot(plt)
    st.markdown("""
    > Os números referentes à sexualidade são preocupantes, pois 40% das vítimas ignoraram ou marcaram como não relevante ao caso e apenas 2% das vítimas se auto declararam como LGBTQIAPN+, **evidenciando o medo em se assumir ou de registrar agressões por ser uma mulher queer**, problema que vem do Brasil ser um dos países mais homofóbicos da atualidade.
    """)
    # Gráfico referente a etnia das vitimas
    plt.figure(figsize=(6, 6))
    contagem = dados["cs_raca"].value_counts()
    plt.pie(
        contagem,
        labels=contagem.index,
        autopct="%1.1f%%",
        colors=['#731406','#5fdade','#044515',"#7c7c7d", '#dcf007', '#e03fd8'] # parda, branca, preta, ignorado, amarela, indigena
    )
    plt.title("Distribuição das vítimas por Etnia")
    plt.tight_layout()
    st.pyplot(plt)
    st.markdown("""
    > Nesse gráfico é fácil notar a distribuição, onde **quase dois terços das vítimas são mulheres racializadas**, fato que é diretamente ligado ao racismo estrutural que o Brasil ainda enfrenta dificuldades de se desfaer. 
    """)

#Aba 2 com os 1000 primeiros dados do dataframe
with tab2:
    st.header("Tabela completa")
    st.dataframe(dados.head(1000))
